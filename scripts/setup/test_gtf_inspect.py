import os
from pathlib import Path

gtf_path = Path('C:/Users/GeneCureAI/data/annotation/gencode.v46.annotation.gtf')
target_symbols = {'BRCA1', 'ERBB2', 'HER2', 'TP53', 'EGFR', 'KRAS', 'ALK', 'CTNNB1', 'AXIN1', 'TERT'}

found_genes = {}
with open(gtf_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('#'):
            continue
        parts = line.strip().split('\t')
        if len(parts) < 9:
            continue
        feature = parts[2]
        if feature == 'gene':
            attrs = parts[8]
            gene_name = None
            gene_id = None
            for attr in attrs.split(';'):
                attr = attr.strip()
                if attr.startswith('gene_name'):
                    gene_name = attr.split('"')[1]
                elif attr.startswith('gene_id'):
                    gene_id = attr.split('"')[1]
            if gene_name in target_symbols or gene_name == 'ERBB2':
                chrom, start, end, strand = parts[0], int(parts[3]), int(parts[4]), parts[6]
                found_genes[gene_name] = {
                    'gene_id': gene_id,
                    'chrom': chrom,
                    'start': start,
                    'end': end,
                    'strand': strand
                }

print("FOUND GENES:")
for k, v in found_genes.items():
    print(f"{k:<8} | ID: {v['gene_id']:<20} | Chr: {v['chrom']:<5} | Start: {v['start']:<10} | End: {v['end']:<10} | Strand: {v['strand']}")
