"""
Model Training Script for Hybrid Code Smell Detection

This script trains the hybrid model combining:
1. GraphCodeBERT embeddings
2. Triplet loss for contrastive learning
3. Classification loss for binary classification

Dataset Format:
- train_smells.txt: Malicious code samples (one per line)
- train_clean.txt: Clean code samples (one per line)
"""

import os
import torch
import torch.optim as optim
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import json
from datetime import datetime

from hybrid_model import HybridCodeSmellModel
from preprocessing import CodePreprocessor


class CodeSmellDataset(Dataset):
    """
    Dataset for code smell detection
    """
    
    def __init__(self, code_snippets, labels, preprocessor):
        """
        Initialize dataset
        
        Args:
            code_snippets (List[str]): List of code samples
            labels (List[int]): Binary labels (0: clean, 1: smell)
            preprocessor (CodePreprocessor): Preprocessor instance
        """
        self.code_snippets = code_snippets
        self.labels = labels
        self.preprocessor = preprocessor
    
    def __len__(self):
        return len(self.code_snippets)
    
    def __getitem__(self, idx):
        """Get preprocessed code and label"""
        code = self.code_snippets[idx]
        label = self.labels[idx]
        
        # Preprocess code
        tokens = self.preprocessor.preprocess(code)
        
        return {
            'input_ids': tokens['input_ids'].squeeze(0),
            'attention_mask': tokens['attention_mask'].squeeze(0),
            'label': torch.tensor(label, dtype=torch.long),
            'code': code
        }


def collate_fn(batch):
    """
    Custom collate function for DataLoader
    """
    input_ids = torch.stack([item['input_ids'] for item in batch])
    attention_mask = torch.stack([item['attention_mask'] for item in batch])
    labels = torch.stack([item['label'] for item in batch])
    
    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'label': labels
    }


def load_code_samples(filepath):
    """
    Load code samples from a file where samples are separated by blank lines.
    Each multi-line block is ONE sample, not each line.
    
    Args:
        filepath (str): Path to the data file
    
    Returns:
        List[str]: List of code samples
    """
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Split by blank lines (double newlines) to get multi-line samples
    samples = []
    for block in content.split('\n\n'):
        block = block.strip()
        if block and len(block) >= 10:  # Skip tiny fragments
            samples.append(block)
    
    return samples


def load_data(data_dir, split_ratio=0.8):
    """
    Load code snippets from files with proper multi-line sample handling.
    
    Args:
        data_dir (str): Directory containing train data
        split_ratio (float): Train-validation split ratio
    
    Returns:
        Tuple: (train_snippets, train_labels, val_snippets, val_labels)
    """
    clean_file = os.path.join(data_dir, 'train_clean.txt')
    smell_file = os.path.join(data_dir, 'train_smells.txt')
    
    clean_snippets = load_code_samples(clean_file)
    smell_snippets = load_code_samples(smell_file)
    
    print(f"Loaded {len(clean_snippets)} clean samples")
    print(f"Loaded {len(smell_snippets)} smell samples")
    
    # Create labels: 0 for clean, 1 for smell
    all_snippets = clean_snippets + smell_snippets
    all_labels = [0] * len(clean_snippets) + [1] * len(smell_snippets)
    
    # Stratified split: shuffle within each class, then split
    import random
    random.seed(42)
    
    clean_indices = list(range(len(clean_snippets)))
    smell_indices = list(range(len(clean_snippets), len(all_snippets)))
    random.shuffle(clean_indices)
    random.shuffle(smell_indices)
    
    clean_split = int(len(clean_indices) * split_ratio)
    smell_split = int(len(smell_indices) * split_ratio)
    
    train_indices = clean_indices[:clean_split] + smell_indices[:smell_split]
    val_indices = clean_indices[clean_split:] + smell_indices[smell_split:]
    
    random.shuffle(train_indices)
    random.shuffle(val_indices)
    
    train_snippets = [all_snippets[i] for i in train_indices]
    train_labels = [all_labels[i] for i in train_indices]
    val_snippets = [all_snippets[i] for i in val_indices]
    val_labels = [all_labels[i] for i in val_indices]
    
    return train_snippets, train_labels, val_snippets, val_labels


def create_triplet_batch(batch, all_labels, device):
    """
    Create a triplet batch from a classification batch.
    Anchor = current sample
    Positive = another sample with same label
    Negative = sample with different label
    
    Args:
        batch: Current batch with input_ids, attention_mask, labels
        all_labels: All labels in dataset for finding positive/negative
        device: Device
    
    Returns:
        Tuple: (anchor_ids, anchor_mask, pos_ids, pos_mask, neg_ids, neg_mask, labels)
    """
    input_ids = batch['input_ids']
    attention_mask = batch['attention_mask']
    labels = batch['label']
    batch_size = input_ids.shape[0]
    
    # For simplicity, use shifted indices as positives/negatives
    # In production, use proper hard negative mining
    pos_indices = torch.roll(torch.arange(batch_size), shifts=1)
    neg_indices = torch.roll(torch.arange(batch_size), shifts=batch_size // 2)
    
    # Ensure positives have same label, negatives have different label
    for i in range(batch_size):
        # Find a positive with same label
        for j in range(batch_size):
            if labels[j] == labels[i] and j != i:
                pos_indices[i] = j
                break
        # Find a negative with different label
        for j in range(batch_size):
            if labels[j] != labels[i]:
                neg_indices[i] = j
                break
    
    pos_ids = input_ids[pos_indices]
    pos_mask = attention_mask[pos_indices]
    neg_ids = input_ids[neg_indices]
    neg_mask = attention_mask[neg_indices]
    
    return input_ids, attention_mask, pos_ids, pos_mask, neg_ids, neg_mask, labels


def train_epoch(model, dataloader, optimizer, device, epoch, use_triplet=True, triplet_weight=1.0):
    """
    Train for one epoch with hybrid loss (classification + triplet).
    
    Args:
        model: PyTorch model
        dataloader: Training dataloader
        optimizer: Optimizer
        device: Device (cpu/cuda)
        epoch (int): Epoch number
        use_triplet (bool): Whether to use triplet loss
        triplet_weight (float): Weight for triplet loss
    
    Returns:
        dict: Training metrics
    """
    model.train()
    total_loss = 0
    total_cls_loss = 0
    total_triplet_loss = 0
    predictions = []
    ground_truth = []
    
    for batch_idx, batch in enumerate(dataloader):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)
        
        optimizer.zero_grad()
        
        if use_triplet:
            # Create triplet batch
            a_ids, a_mask, p_ids, p_mask, n_ids, n_mask, lbls = create_triplet_batch(
                batch, None, device
            )
            a_ids, a_mask = a_ids.to(device), a_mask.to(device)
            p_ids, p_mask = p_ids.to(device), p_mask.to(device)
            n_ids, n_mask = n_ids.to(device), n_mask.to(device)
            
            # Forward pass with triplet loss
            outputs = model.forward_triplet(
                a_ids, a_mask, p_ids, p_mask, n_ids, n_mask, lbls.to(device)
            )
            
            cls_loss = outputs['cls_loss']
            triplet_loss = outputs['triplet_loss']
            loss = outputs['loss']  # hybrid loss = triplet + 0.5 * cls
            
            total_cls_loss += cls_loss.item()
            total_triplet_loss += triplet_loss.item()
            
            logits = outputs['logits']
        else:
            # Classification only
            outputs = model(input_ids=input_ids, 
                           attention_mask=attention_mask, 
                           labels=labels)
            loss = outputs['loss']
            total_cls_loss += loss.item()
            logits = outputs['logits']
        
        # Backward pass
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        total_loss += loss.item()
        
        # Store predictions
        preds = torch.argmax(logits, dim=1)
        predictions.extend(preds.cpu().numpy())
        ground_truth.extend(labels.cpu().numpy())
        
        if (batch_idx + 1) % 10 == 0:
            msg = f"Epoch {epoch}, Batch {batch_idx + 1}, Loss: {loss.item():.4f}"
            if use_triplet:
                msg += f" (cls: {cls_loss.item():.4f}, tri: {triplet_loss.item():.4f})"
            print(msg)
    
    # Calculate metrics
    accuracy = accuracy_score(ground_truth, predictions)
    precision = precision_score(ground_truth, predictions, average='weighted', zero_division=0)
    recall = recall_score(ground_truth, predictions, average='weighted', zero_division=0)
    f1 = f1_score(ground_truth, predictions, average='weighted', zero_division=0)
    
    result = {
        'loss': total_loss / len(dataloader),
        'cls_loss': total_cls_loss / len(dataloader),
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }
    
    if use_triplet:
        result['triplet_loss'] = total_triplet_loss / len(dataloader)
    
    return result


def validate(model, dataloader, device):
    """
    Validate model
    
    Args:
        model: PyTorch model
        dataloader: Validation dataloader
        device: Device (cpu/cuda)
    
    Returns:
        dict: Validation metrics
    """
    model.eval()
    total_loss = 0
    predictions = []
    ground_truth = []
    
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(input_ids=input_ids, 
                           attention_mask=attention_mask, 
                           labels=labels)
            
            loss = outputs['loss']
            logits = outputs['logits']
            
            total_loss += loss.item()
            
            preds = torch.argmax(logits, dim=1)
            predictions.extend(preds.cpu().numpy())
            ground_truth.extend(labels.cpu().numpy())
    
    # Calculate metrics
    accuracy = accuracy_score(ground_truth, predictions)
    precision = precision_score(ground_truth, predictions, average='weighted', zero_division=0)
    recall = recall_score(ground_truth, predictions, average='weighted', zero_division=0)
    f1 = f1_score(ground_truth, predictions, average='weighted', zero_division=0)
    cm = confusion_matrix(ground_truth, predictions)
    
    return {
        'loss': total_loss / len(dataloader),
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm.tolist()
    }


def train(data_dir, model_save_path, epochs=5, batch_size=16, learning_rate=2e-5, use_triplet=True):
    """
    Main training function
    
    Args:
        data_dir (str): Directory containing training data
        model_save_path (str): Path to save trained model
        epochs (int): Number of epochs
        batch_size (int): Batch size
        learning_rate (float): Learning rate
        use_triplet (bool): Whether to use triplet loss
    """
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    print(f"Triplet loss: {'ENABLED' if use_triplet else 'DISABLED'}")
    
    # Initialize preprocessor
    preprocessor = CodePreprocessor(model_name='microsoft/graphcodebert-base', max_length=512)
    
    # Load data
    print("Loading data...")
    train_snippets, train_labels, val_snippets, val_labels = load_data(data_dir)
    
    print(f"Training samples: {len(train_snippets)}")
    print(f"Validation samples: {len(val_snippets)}")
    
    # Create datasets and dataloaders
    train_dataset = CodeSmellDataset(train_snippets, train_labels, preprocessor)
    val_dataset = CodeSmellDataset(val_snippets, val_labels, preprocessor)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
    
    # Initialize model
    print("Initializing model...")
    model = HybridCodeSmellModel(model_name='microsoft/graphcodebert-base')
    model.to(device)
    
    # Setup optimizer with weight decay
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # Training loop with early stopping
    best_f1 = 0
    patience = 3
    patience_counter = 0
    training_history = {'train': [], 'val': []}
    
    for epoch in range(1, epochs + 1):
        print(f"\n{'='*50}")
        print(f"Epoch {epoch}/{epochs}")
        print(f"{'='*50}")
        
        # Training
        train_metrics = train_epoch(model, train_loader, optimizer, device, epoch, use_triplet=use_triplet)
        print(f"Train Loss: {train_metrics['loss']:.4f}")
        print(f"Train Accuracy: {train_metrics['accuracy']:.4f}")
        print(f"Train F1: {train_metrics['f1']:.4f}")
        
        # Validation
        val_metrics = validate(model, val_loader, device)
        print(f"\nVal Loss: {val_metrics['loss']:.4f}")
        print(f"Val Accuracy: {val_metrics['accuracy']:.4f}")
        print(f"Val Precision: {val_metrics['precision']:.4f}")
        print(f"Val Recall: {val_metrics['recall']:.4f}")
        print(f"Val F1: {val_metrics['f1']:.4f}")
        
        # Step scheduler
        scheduler.step()
        
        training_history['train'].append(train_metrics)
        training_history['val'].append(val_metrics)
        
        # Save best model
        if val_metrics['f1'] > best_f1:
            best_f1 = val_metrics['f1']
            patience_counter = 0
            print(f"\nNew best F1: {best_f1:.4f}. Saving model...")
            os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
            torch.save(model.state_dict(), model_save_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\nEarly stopping at epoch {epoch} (no improvement for {patience} epochs)")
                break
    
    # Save training history
    history_save_path = model_save_path.replace('.pt', '_history.json')
    with open(history_save_path, 'w') as f:
        # Convert numpy arrays in confusion matrix to lists
        for metric in training_history['val']:
            if 'confusion_matrix' in metric:
                metric['confusion_matrix'] = [[int(x) for x in row] for row in metric['confusion_matrix']]
        json.dump(training_history, f, indent=2)
    
    print(f"\nTraining complete! Best F1: {best_f1:.4f}")
    print(f"Model saved to: {model_save_path}")
    print(f"History saved to: {history_save_path}")


if __name__ == "__main__":
    # Configuration
    DATA_DIR = '../dataset'
    MODEL_SAVE_PATH = '../ml_pipeline/saved_models/hybrid_code_smell_model.pt'
    EPOCHS = 5
    BATCH_SIZE = 16
    LEARNING_RATE = 2e-5
    
    # Train
    train(
        data_dir=DATA_DIR,
        model_save_path=MODEL_SAVE_PATH,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE
    )
