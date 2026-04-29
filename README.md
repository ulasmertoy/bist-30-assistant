# BIST Insight Assistant

A knowledge assistant that helps individual investors detect unusual price/volume movements in BIST stocks and understand the news behind them.

> ⚠️ This system does not make predictions, generate signals, or provide investment advice. It only synthesizes information.

## Architecture
`Data → Anomaly Detection (XGBoost) → RAG (ChromaDB) → FastAPI + Streamlit`

## Tech Stack
- **Data:** yfinance, KAP scraper, Bloomberg HT RSS
- **ML:** XGBoost, Isolation Forest, LLM sentiment scoring
- **RAG:** ChromaDB, hybrid search (BM25 + dense), citation tracking
- **Production:** FastAPI, Streamlit, Docker

## Status
- [x] Repo setup
- [ ] Data layer
- [ ] ML layer
- [ ] RAG layer
- [ ] Production

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```