import pandas as pd
import json
from pandas.io.json import json_normalize


def get_df(file, header, newheader, outputdir, currenttime):
    with open(outputdir + "/" + file + ".json") as f:
        data = json.load(f)
    tmp = json_normalize(data)
    tmp = tmp[["values"]]
    tmp.columns = ["Werte"]
    df = json_normalize(tmp.Werte[0])
    df = df[header]
    df.columns = newheader
    if file == "balance_transactions":
        df = df[df.Type == "INTEREST_DIVIDENDS"][["Date", "WKN", "Netto"]]
        df["Brutto"] = (
            df.WKN.str.split("05")
            .str[1]
            .str.split(" ")
            .str[2]
            .str.replace(",", ".")
            .astype("float")
        )
        df.WKN = (
            df.WKN.str.split("03").str[1].str.split(
                "04").str[1].str.split(" ").str[0]
        )
    df.to_excel(outputdir + "/" + file + "_" + currenttime + ".xlsx", index=False)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    # Excel output with column width = max length of values in column
    writer = pd.ExcelWriter(
        outputdir + "/" + file + "_" + currenttime + ".xlsx", engine="xlsxwriter"
    )
    df.to_excel(writer, index=False)

    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    for i, col in enumerate(df.columns):
        column_len = df[col].astype(str).str.len().max()
        column_len = max(column_len, len(col)) + 2
        worksheet.set_column(i, i, column_len)
    writer.save()
    return df
