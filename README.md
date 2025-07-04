# Chocolate Sales Analytics Dashboard + AI Q&A

This is an interactive Streamlit dashboard for analyzing chocolate sales data, with a built-in **AI-powered Q&A assistant**. It lets users ask **natural language questions** about sales, products, and revenue, and get accurate answers based on real data using a **hybrid logic + AI pipeline**.

---
## Technologies Used
Streamlit

Pandas

Plotly

Transformers

LangChain

ChromaDB

Sentence Transformers

---

## Features

### Data Analytics
- **Year and Country filters**
- Monthly revenue bar chart
- Product-wise revenue pie chart
- Live KPIs:
  - Total Revenue
  - Total Boxes Shipped
  - Top Product by Revenue
---

### AI Q&A Assistant (Hybrid)
- Built-in question answering using:
  - **Logic rules** for known queries (faster + 100% accurate)
  - **Retrieval-Augmented Generation (RAG)** for open-ended Q&A using:
    - `sentence-transformers` for document embeddings
    - `Chroma` vector DB for retrieval
    - `distilbert-base-cased-distilled-squad` as a local QA model

> Example Questions:
> - What is the total revenue?
> - Which country had the highest revenue?
> - What product sold the most in 2022?

---

### How to Run

1. **Clone or download the repository**

2. **Install dependencies**

```bash
pip install -r requirements.txt
```
---
### Run the app
```bash
streamlit run app.py
```

