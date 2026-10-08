# Excel Report Agent

Upload an Excel sales file and get a Word report with AI-written insights.

# How it works

1) Checks the file for an empty sheet or missing required columns, and stops with a clear message if something is wrong.
2) Calculates revenue (quantity x price) by product and region with pandas.
3) An LLM (Groq) turns those numbers into a short written report, saved as a Word file.