from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import pandas as pd


load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-20b")


class State(TypedDict):
    file_path: str
    summary: str
    report: str
    row_count: int
    analysis: str
    missing: list
    error: str
 

def read_excel(state: State):
    df = pd.read_excel(state["file_path"])
    lst=["product","region","quantity","price"]
    missing=[]
    for x in lst:
        if x not in df.columns:
            missing.append(x)
    
    summary = (
    f"Rows: {len(df)}\n"
    f"Columns: {list(df.columns)}\n\n"
    f"Statistics:\n{df.describe().to_string()}\n\n"  
    f"First rows:\n{df.head(5).to_string()}"
)
    # print(missing)
    return {"summary": summary, "row_count": len(df),"missing":missing}

def bad_columns(state: State):
    return{"error": f"These required columns are missing:{state['missing']}"}

def empty_file(state: State):
    return {"error": "file is empty, please upload a file with data rows "}

def check_rows(state: State):
    if state["row_count"]==0:
        return "empty_file"
    elif len(state["missing"]) > 0:
        return "bad_columns"
    else:
        return "write_report"
    
def analyze(state: State):
    
    df = pd.read_excel(state["file_path"])
    df["quantity"]=pd.to_numeric(df["quantity"], errors="coerce")
    df["price"]=pd.to_numeric(df["price"], errors="coerce")
    skipped = df[["quantity", "price"]].isna().any(axis=1).sum()
    df["revenue"] = df["quantity"] * df["price"]
    by_product = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)  

    # print(by_product)
    # print(by_region)

    analysis = (
        f"Revenue by product:\n{by_product.to_string()}\n\n"
        f"Revenue by region:\n{by_region.to_string()}"
        f"\n\nRows skipped (missing or invalid quantity/price): {skipped}"
    )
    return {"analysis": analysis}  


def write_report(state: State):
    prompt = "You are a data analyst. Write a short report (3 bullet points, simple English) based on this data. Do not add currency symbols or facts that are not in the data. About the missed rows, it needs to be in separate line other then in the 3.\n\n" + state["analysis"] +"\n\n" + state["summary"]
    # print(prompt)
    result = llm.invoke(prompt)
    return {"report": result.content}


builder= StateGraph(State)
builder.add_node("read_excel", read_excel)
builder.add_node("write_report", write_report)
builder.add_node("empty_file", empty_file)
builder.add_node("bad_columns", bad_columns)
builder.add_node("analyze", analyze)
builder.set_entry_point("read_excel")
builder.add_conditional_edges(
       "read_excel",
       check_rows,
       {"write_report": "analyze", "empty_file": "empty_file", "bad_columns": "bad_columns"},
   )
builder.add_edge("analyze","write_report")
builder.add_edge("write_report", END)
builder.add_edge("bad_columns", END)
builder.add_edge("empty_file", END)
graph=builder.compile()
if __name__ == "__main__":
    result = graph.invoke({"file_path": "sales_data.xlsx"})
    print(result["report"])