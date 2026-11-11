"""
Hybrid Contrastive-Transformer Fusion Framework for Code Smell Detection

This module implements a sophisticated hybrid model combining:
1. GraphCodeBERT transformer-based embeddings
2. Triplet loss for contrastive learning
3. Classification layer with cross-entropy loss

The hybrid loss combines triplet loss (contrastive) and classification loss
to detect code smells effectively.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer


class TripletLoss(nn.Module):
    """
    Triplet Loss Module
    
    Minimizes:
    L = max(d(anchor, positive) - d(anchor, negative) + margin, 0)
    
    where d is Euclidean distance
    """
    
    def __init__(self, margin=1.0):
        """
        Initialize Triplet Loss
        
        Args:
            margin (float): Margin for triplet loss. Default: 1.0
        """
        super(TripletLoss, self).__init__()
        self.margin = margin
    
    def forward(self, anchor, positive, negative):
        """
        Forward pass for triplet loss
        
        Args:
            anchor (Tensor): Anchor embeddings [batch_size, embedding_dim]
            positive (Tensor): Positive embeddings [batch_size, embedding_dim]
            negative (Tensor): Negative embeddings [batch_size, embedding_dim]
        
        Returns:
            Tensor: Triplet loss value (scalar)
        """
        pos_distance = F.pairwise_distance(anchor, positive, p=2)
        neg_distance = F.pairwise_distance(anchor, negative, p=2)
        
        losses = F.relu(pos_distance - neg_distance + self.margin)
        return losses.mean()


class HybridCodeSmellModel(nn.Module):
    """
    Hybrid Contrastive-Transformer Fusion Model for Code Smell Detection
    
    Architecture:
    1. GraphCodeBERT encoder for contextual code embeddings
    2. Triplet loss for contrastive learning
    3. Classification head for binary classification (Smell / No Smell)
    4. Hybrid loss = Triplet Loss + λ * Classification Loss
    """
    
    def __init__(self, model_name='microsoft/graphcodebert-base', embedding_dim=768, 
                 hidden_dim=256, dropout=0.1):
        """
        Initialize Hybrid Model
        
        Args:
            model_name (str): HuggingFace model identifier
            embedding_dim (int): Dimension of GraphCodeBERT embeddings
            hidden_dim (int): Hidden dimension for classification head
            dropout (float): Dropout probability
        """
        super(HybridCodeSmellModel, self).__init__()
        
        # Load GraphCodeBERT encoder
        self.encoder = AutoModel.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Freeze encoder initially (optional, can be unfrozen for fine-tuning)
        for param in self.encoder.parameters():
            param.requires_grad = False
        
        self.embedding_dim = embedding_dim
        
        # Classification head (binary classification: smell vs no-smell)
        self.classification_head = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 2)  # Binary classification: [no-smell, smell]
        )
        
        # Triplet loss module
        self.triplet_loss_fn = TripletLoss(margin=1.0)
        
        # Cross-entropy loss for classification
        self.ce_loss_fn = nn.CrossEntropyLoss()
        
        # Loss weights
        self.lambda_clf = 0.5  # Weight for classification loss
        self.lambda_triplet = 1.0  # Weight for triplet loss
    
    def get_embeddings(self, input_ids, attention_mask):
        """
        Extract CLS embeddings from GraphCodeBERT encoder
        
        Args:
            input_ids (Tensor): Tokenized input [batch_size, seq_length]
            attention_mask (Tensor): Attention mask [batch_size, seq_length]
        
        Returns:
            Tensor: CLS embeddings [batch_size, embedding_dim]
        """
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_embeddings = outputs.last_hidden_state[:, 0, :]  # CLS token
        return cls_embeddings
    
    def forward(self, input_ids, attention_mask, labels=None):
        """
        Forward pass for inference (classification only)
        
        Args:
            input_ids (Tensor): Tokenized input
            attention_mask (Tensor): Attention mask
            labels (Tensor, optional): Target labels for training
        
        Returns:
            dict: Contains 'logits' and optionally 'loss'
        """
        embeddings = self.get_embeddings(input_ids, attention_mask)
        logits = self.classification_head(embeddings)
        
        output = {'logits': logits, 'embeddings': embeddings}
        
        if labels is not None:
            loss = self.ce_loss_fn(logits, labels)
            output['loss'] = loss
        
        return output
    
    def forward_triplet(self, anchor_ids, anchor_mask, 
                       positive_ids, positive_mask, 
                       negative_ids, negative_mask, 
                       anchor_labels):
        """
        Forward pass for hybrid training (triplet + classification)
        
        Args:
            anchor_ids (Tensor): Anchor input IDs
            anchor_mask (Tensor): Anchor attention mask
            positive_ids (Tensor): Positive input IDs
            positive_mask (Tensor): Positive attention mask
            negative_ids (Tensor): Negative input IDs
            negative_mask (Tensor): Negative attention mask
            anchor_labels (Tensor): Labels for anchor samples
        
        Returns:
            dict: Contains 'loss', 'cls_loss', 'triplet_loss', 'logits'
        """
        # Get embeddings
        anchor_emb = self.get_embeddings(anchor_ids, anchor_mask)
        positive_emb = self.get_embeddings(positive_ids, positive_mask)
        negative_emb = self.get_embeddings(negative_ids, negative_mask)
        
        # Classification loss
        anchor_logits = self.classification_head(anchor_emb)
        cls_loss = self.ce_loss_fn(anchor_logits, anchor_labels)
        
        # Triplet loss
        triplet_loss = self.triplet_loss_fn(anchor_emb, positive_emb, negative_emb)
        
        # Hybrid loss
        hybrid_loss = self.lambda_triplet * triplet_loss + self.lambda_clf * cls_loss
        
        return {
            'loss': hybrid_loss,
            'cls_loss': cls_loss,
            'triplet_loss': triplet_loss,
            'logits': anchor_logits,
            'embeddings': anchor_emb
        }
    
    def predict(self, code, device='cpu'):
        """
        Predict code smell for a single code snippet
        
        Args:
            code (str): Source code to analyze
            device (str): Device to use ('cpu' or 'cuda')
        
        Returns:
            dict: Contains 'prediction' (0/1), 'confidence' (0-1), 'logits'
        """
        # Tokenize
        inputs = self.tokenizer(code, return_tensors='pt', max_length=512, 
                               truncation=True, padding=True).to(device)
        
        # Forward pass
        with torch.no_grad():
            outputs = self.forward(**inputs)
        
        logits = outputs['logits']
        probs = F.softmax(logits, dim=1)
        pred_class = torch.argmax(probs, dim=1)
        confidence = probs[0, pred_class[0]].item()
        
        return {
            'prediction': pred_class[0].item(),
            'confidence': confidence,
            'logits': logits[0].detach().cpu().numpy(),
            'probabilities': probs[0].detach().cpu().numpy()
        }
    
    def unfreeze_encoder(self, num_layers=2):
        """
        Unfreeze the last N layers of the encoder for fine-tuning
        
        Args:
            num_layers (int): Number of layers to unfreeze from the end
        """
        for i, layer in enumerate(self.encoder.encoder.layer):
            if i >= len(self.encoder.encoder.layer) - num_layers:
                for param in layer.parameters():
                    param.requires_grad = True
