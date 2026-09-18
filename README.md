# Gene-Cure AI 🧬🎯

**A Deep Learning-Driven Platform for Automated CRISPR Guide RNA Design Targeting Breast, Lung, and Liver Cancer Therapeutics.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Scientific Validation Disclaimer**:
> This platform provides *in-silico* computational predictions and is not a substitute for experimental validation in molecular biology or clinical laboratories. All generated guide RNAs, efficiency predictions, and off-target safety evaluations must undergo wet-lab functional validation before any biological or therapeutic application.

---

## 🎯 Target Cancers & Genes

| Target Cancer | Target Genes |
| :--- | :--- |
| **Breast Cancer** | `BRCA1`, `HER2` (ERBB2), `TP53` |
| **Lung Cancer** | `EGFR`, `KRAS`, `ALK` |
| **Liver Cancer** | `CTNNB1`, `AXIN1`, `TERT` |

---

## 🔬 Five-Stage Computational Pipeline

1. **Stage 1 — Cancer Gene Selection**: Curated cancer gene registry with complete data provenance (NCBI, Ensembl, HGNC).
2. **Stage 2 — Guide RNA Identification**: SpCas9 20-nt protospacer scanning with 5'-NGG PAM on forward and reverse-complement strands.
3. **Stage 3 — On-Target Efficiency Prediction**: Hybrid deep learning architecture combining PyTorch 1D-CNN (sequence representations) and XGBoost (105 engineered bio-physicochemical features).
4. **Stage 4 — Off-Target Analysis**: GRCh38 seed-and-extend alignment (Bowtie2 / BLAST+) with Cutting Frequency Determination (CFD) scoring.
5. **Stage 5 — Guide RNA Ranking**: Multi-criteria decision analysis using **TOPSIS** with mathematically grounded weighting (On-target: 35%, Off-target safety: 30%, Cancer relevance: 20%, GC optimality: 15%).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional for containerized deployment)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Running via Docker
```bash
docker-compose up --build
```

Access:
- Frontend: `http://localhost:5173`
- Backend API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

---

## 🧪 Testing

Run backend tests:
```bash
pytest backend/tests
```

Run ranking tests:
```bash
pytest ranking/tests
```

---

## 📚 Project Architecture & Documentation
For full architectural specifications, ML formulations, and feature definitions, refer to:
- [`docs/MASTER_IMPLEMENTATION_PLAN.md`](docs/MASTER_IMPLEMENTATION_PLAN.md)
