import pandas as pd

df=pd.read_excel("sales_data.xlsx")
df.loc[2,"quantity"]=None
df.to_excel("blank_cells.xlsx",index=False)

df=pd.read_excel("sales_data.xlsx")
df["quantity"] = df["quantity"].astype(object)
df.loc[3,"quantity"]="ten"
df.to_excel("text_quantity.xlsx",index=False)