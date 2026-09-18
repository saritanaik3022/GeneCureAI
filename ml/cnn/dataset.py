"""
PyTorch Dataset and DataLoader for 30-nt CRISPR sgRNA sequences.
"""
from typing import List, Optional
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from ml.data.preprocess import one_hot_encode_sequence


class CRISPRSequenceDataset(Dataset):
    """
    PyTorch Dataset wrapping 30-nt sequences and target activity labels.
    """
    def __init__(self, sequences: List[str], targets: Optional[List[float]] = None):
        self.sequences = sequences
        self.targets = targets

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int):
        seq = self.sequences[idx]
        x_encoded = one_hot_encode_sequence(seq) # (4, 30)
        x_tensor = torch.tensor(x_encoded, dtype=torch.float32)

        if self.targets is not None:
            y_tensor = torch.tensor(self.targets[idx], dtype=torch.float32).unsqueeze(0) # (1,)
            return x_tensor, y_tensor
        return x_tensor


def create_dataloader(
    sequences: List[str],
    targets: Optional[List[float]] = None,
    batch_size: int = 64,
    shuffle: bool = False,
    num_workers: int = 0
) -> DataLoader:
    """Creates a PyTorch DataLoader for sequence data."""
    dataset = CRISPRSequenceDataset(sequences=sequences, targets=targets)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)
