"""
DDI Model Architecture
Extracted from the UIT challenge notebook
"""
import torch
import torch.nn as nn


class DeepDDIModel(nn.Module):
    """
    Deep Neural Network for Drug-Drug Interaction Prediction
    """
    def __init__(self, input_dim, num_labels, hidden_dim=1024, dropout=0.4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, hidden_dim // 4),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 4, num_labels)  # multi-label output
        )

    def forward(self, x1, x2):
        """
        Forward pass for two drug features
        Args:
            x1: First drug features (batch, input_dim)
            x2: Second drug features (batch, input_dim)
        Returns:
            logits: Multi-label predictions (batch, num_labels)
        """
        x = torch.cat([x1, x2], dim=1)
        return self.net(x)  # (batch, num_labels)


class FocalLoss(nn.Module):
    """
    Focal Loss for handling class imbalance
    """
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        """
        Args:
            alpha: weight for positive samples (set >1 to upweight positives)
            gamma: focusing parameter (higher = focus more on hard examples)
            reduction: 'mean' or 'sum'
        """
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        self.bce = nn.BCEWithLogitsLoss(reduction='none')

    def forward(self, logits, targets):
        bce_loss = self.bce(logits, targets)  # shape: (batch, num_labels)
        probs = torch.sigmoid(logits)
        pt = probs * targets + (1 - probs) * (1 - targets)  # prob of the true class
        focal_loss = self.alpha * (1 - pt) ** self.gamma * bce_loss

        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss