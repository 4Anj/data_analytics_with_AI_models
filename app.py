# app.py
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from transformers import pipeline


df = pd.read_csv(r"C:\Users\anjan\Downloads\Chocolate Sales.csv")
df["Amount"] = df["Amount"].replace(r"[\$,]", "", regex=True).astype(float)
df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")
df["Year"] = df["Date"].dt.year
df["Quarter"] = df["Date"].dt.quarter
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day

st.sidebar.title("Filters")
selected_year = st.sidebar.multiselect("Select Year", sorted(df["Year"].unique()), default=df["Year"].unique())
selected_country = st.sidebar.multiselect("Select Country", df["Country"].unique(), default=df["Country"].unique())

filtered_df = df[df["Year"].isin(selected_year) & df["Country"].isin(selected_country)]

st.title("🍫 Chocolate Sales Analytics Dashboard")


if not filtered_df.empty:
    total_revenue = filtered_df["Amount"].sum()
    total_boxes = filtered_df["Boxes Shipped"].sum()
    top_product = filtered_df.groupby("Product")["Amount"].sum().idxmax()

    st.metric("Total Revenue", f"${total_revenue:,.2f}")
    st.metric("Total Boxes Shipped", f"{total_boxes}")
    st.metric("Top Product by Revenue", top_product)
else:
    st.warning("⚠️ No data available for the selected filters.")


st.subheader("Revenue by Month")
fig1 = px.bar(filtered_df, x="Month", y="Amount", color="Country", barmode="group")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Revenue by Product")
fig2 = px.pie(filtered_df, names="Product", values="Amount")
st.plotly_chart(fig2, use_container_width=True)

st.sidebar.write("Filtered Rows:", len(filtered_df))
st.sidebar.dataframe(filtered_df.head())


st.subheader("Ask a Question about the Sales Data")

# --- Step 1: Create documents from filtered DataFrame
def create_docs(df):
    docs = []
    for _, row in df.iterrows():
        text = f"Date: {row['Date'].date()}, Country: {row['Country']}, Product: {row['Product']}, Boxes: {row['Boxes Shipped']}, Amount: ${row['Amount']}"
        docs.append(Document(page_content=text))
    return docs

# --- Step 2: Load vectorstore with sentence-transformers
@st.cache_resource
def load_vectorstore():
    persist_dir = "./choco_vector_db"
    os.makedirs(persist_dir, exist_ok=True)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    docs = create_docs(df)

    if os.path.exists(os.path.join(persist_dir, "index")):
        return Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    else:
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = text_splitter.split_documents(docs)
        vectordb = Chroma.from_documents(split_docs, embeddings, persist_directory=persist_dir)
        vectordb.persist()
        return vectordb

vectorstore = load_vectorstore()

# --- Step 3: Load lightweight QA model locally
@st.cache_resource
def load_qa_chain():
    hf_qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    llm = HuggingFacePipeline(pipeline=hf_qa_pipeline)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

qa_chain = load_qa_chain()

# --- Step 4: Add logic-based fallback
def logic_answer(question, df):
    q = question.lower()
    try:
        if "total revenue" in q:
            return f"${df['Amount'].sum():,.2f}"
        if "boxes" in q:
            return f"{df['Boxes Shipped'].sum()} boxes"
        if "top product" in q:
            return df.groupby("Product")["Amount"].sum().idxmax()
        if "top country" in q or "most revenue" in q:
            return df.groupby("Country")["Amount"].sum().idxmax()
        for country in df['Country'].unique():
            if country.lower() in q:
                rev = df[df['Country'] == country]['Amount'].sum()
                return f"${rev:,.2f} from {country}"
        return None
    except:
        return None

# --- Step 5: User input
question = st.text_input("Ask your question:")

if question:
    with st.spinner("Thinking..."):
        answer = logic_answer(question, filtered_df)
        if answer:
            st.success(f"**Answer:** {answer}")
        else:
            try:
                result = qa_chain.run(question)
                st.success(f"**Answer:** {result}")
            except Exception as e:
                st.warning("I don't know the answer to that. Please ask something related to chocolate sales.")
   
