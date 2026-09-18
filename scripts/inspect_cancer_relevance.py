"""
Audit script for TCGA cancer relevance scores CSV.
Inspects mean expression values, normalization, missing values, and gene mappings.
"""
import os
import pandas as pd

CSV_PATH = "C:/Users/GeneCureAI/results/cancer_relevance_scores.csv"

def audit_cancer_relevance():
    print(f"=== Auditing TCGA Cancer Relevance Dataset: {CSV_PATH} ===")
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: Dataset not found at {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)
    print(f"Total Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\n--- Dataset Contents ---")
    print(df.to_string(index=False))

    print("\n--- Summary Statistics by Cancer Type ---")
    for c_type, group in df.groupby("cancer_type"):
        print(f"\nCancer Type: {c_type}")
        print(f"  Genes ({len(group)}): {list(group['gene'])}")
        print(f"  Mean Expression Range: {group['mean_expr'].min():.2f} - {group['mean_expr'].max():.2f}")
        print(f"  Relevance Score Range: {group['cancer_relevance_score'].min():.4f} - {group['cancer_relevance_score'].max():.4f}")

    print("\n--- Missing Value Audit ---")
    null_counts = df.isnull().sum()
    print(null_counts)
    print("\nAudit Complete.")

if __name__ == "__main__":
    audit_cancer_relevance()
