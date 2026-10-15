# SWINGDECK DASHBOARD ARCHITECTURE
- **Frontend**: Streamlit + Plotly + Streamlit-Agraph
- **Data Layer**: Direct polling of JSONL (incremental processing simulation via python generator caching).
- **Security**: Local-only, READ-ONLY, Live Execution Blocked.
