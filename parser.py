import pandas as pd
from datetime import datetime


def parse_first_page():
    file_path = 'data.xlsx'
    xls = pd.ExcelFile(file_path)
    sheet1 = pd.read_excel(xls, sheet_name='olimpyads_info')
    if 'id' in sheet1.columns:
        sheet1.drop('id', axis=1, inplace=True)
    sheet1 = sheet1.astype(str)
    rows_sheet1 = sheet1.values.tolist()
    return rows_sheet1


def parse_second_page():
    file_path = 'data.xlsx'
    xls = pd.ExcelFile(file_path)
    sheet2 = pd.read_excel(xls, sheet_name='olimpyads_dates')
    if 'id' in sheet2.columns:
        sheet2.drop('id', axis=1, inplace=True)
    sheet2 = sheet2.astype(str)
    rows_sheet2 = sheet2.values.tolist()
    return rows_sheet2


def convert_date(date_str):
    current_year = datetime.now().year
    full_date_str = f"{date_str}.{current_year}"
    return datetime.strptime(full_date_str, "%d.%m.%Y")


a = parse_first_page()
b = parse_second_page()
for x in b:
    t = False
    for y in a:
        if x[0] == y[0]:
            t = True
    if not t:
        print(x)