"""
PyTorch 1D Convolutional Neural Network for CRISPR sgRNA On-Target Activity.
Learns deep motif representations directly from 30-nt one-hot matrices.
"""
from typing import Optional, Tuple
import torch
import torch.nn as nn


class CRISPR1DCNN(nn.Module):
    """
    1D CNN architecture learning sequence motifs from 30-nt one-hot matrices.
    Input shape: (Batch, 4, 30)
    Output shape: (Batch, 1) in range [0.0, 1.0]
    """
    def __init__(self, embedding_dim: int = 64):
        super().__init__()
        self.embedding_dim = embedding_dim

        # Block 1: Local motif detection (3-mer receptive field)
        self.conv1 = nn.Conv1d(in_channels=4, out_channels=64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(64)
        self.act1 = nn.LeakyReLU(0.1)

        # Block 2: Extended motif combination (5-mer receptive field)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=5, padding=2)
        self.bn2 = nn.BatchNorm1d(128)
        self.act2 = nn.LeakyReLU(0.1)
        self.pool = nn.MaxPool1d(kernel_size=2, stride=2) # 30 -> 15

        # Dense Sequence Embedding Layer
        self.fc1 = nn.Linear(128 * 15, embedding_dim)
        self.bn3 = nn.BatchNorm1d(embedding_dim)
        self.act3 = nn.LeakyReLU(0.1)
        self.dropout = nn.Dropout(0.3)

        # Output Regression Head
        self.out = nn.Linear(embedding_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extracts dense sequence embeddings (Batch, embedding_dim)."""
        x = self.act1(self.bn1(self.conv1(x)))
        x = self.act2(self.bn2(self.conv2(x)))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.act3(self.bn3(self.fc1(x)))
        return x

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass predicting on-target cleavage efficiency."""
        emb = self.forward_features(x)
        emb = self.dropout(emb)
        out = self.sigmoid(self.out(emb))
        return out
