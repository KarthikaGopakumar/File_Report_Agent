from fastapi.responses import FileResponse
from fastapi import FastAPI, UploadFile, File
from graph_excel import graph
from docx import Document

app = FastAPI()

def make_docx(report_text):
    doc=Document()    
    doc.add_heading("Sales Report",level=1)
    doc.add_paragraph(report_text)
    doc.save("report.docx")

@app.post("/report")
async def report(file: UploadFile = File(...)):
    contents = await file.read()
    with open("uploaded.xlsx", "wb") as f:
        f.write(contents)
    result=graph.invoke({"file_path": "uploaded.xlsx"}) 
    make_docx(result["report"])   
    return FileResponse("report.docx", filename="report.docx")