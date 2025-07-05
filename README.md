# SmartViz: Ask Your Data

SmartViz is a dynamic and intelligent data analysis dashboard built using Streamlit. It allows users to upload **any CSV file** that includes a date column and at least one numeric column, and then:

- Visualizes time-based trends
- Displays key KPIs (Total, Average, Max, Min)
- Answers simple time-based questions (like "total in April 2022" or "average in Q1")

---

## Features

- Upload your own CSV file
- Automatically detect date and numeric columns
- Generate visualizations like line charts for monthly trends
- Ask questions such as:
  - `What is the total in April?`
  - `Give the average in 2022`
  - `Max in Q1`
  - `Min in March 2023`
- Supports filtering by:
  - Year
  - Month
  - Quarter
  - Daily

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

