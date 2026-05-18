import pandas as pd
from sys import argv, exit
from phonenumbers import parse, format_number, is_valid_number, PhoneNumberFormat
from numpy import nan

if len(argv) < 2:
    print(f"Usage: python {argv[0]} <input CSV>")
    exit(1)

df = pd.read_csv(argv[1], encoding="utf-8", dtype={"phone_number": str, "parent_cellphone_number": str})

# 全ての空欄について、NaNとして扱う。
df = df.replace("", nan)

df = df[[
    "student_number",
    "is_male",
    "first_name",
    "last_name",
    "phone_number",
    "parent_name",
    "parent_first_name",
    "parent_last_name",
    "parent_cellphone_number"
]]

df["gender"] = df["is_male"].map({1: "男", 0: "女"})
df = df.drop(columns=["is_male"])

def format_phone(val):
    # NaNにはNaNを
    if pd.isna(val):
        return nan
    # 電話番号(ハイフンなし)をパースする。 "JP"を指定しているのは、国内電話番号周りのため
    parsed = parse(val, "JP")
    def format(parsed):
        if parsed.country_code == 81:
            return format_number(parsed, PhoneNumberFormat.NATIONAL)
        else:
            return format_number(parsed, PhoneNumberFormat.INTERNATIONAL)
    if is_valid_number(parsed):
        return format(parsed)
    else:
        # とりあえず、先頭に"プラス"を付けることで、国際電話(国コード付き電話番号)として有効な番号にならないか試行する。
        parsed = parse("+" + val, "JP")
        if is_valid_number(parsed):
            return format(parsed)
        else:
            # だめだったら、元の番号を表示、CSVにはエラー表示付きで出力させておく
            # やっぱNaNにする
            print(f"Parse Error! Phone Number: {val}")
            # return f"Error: {val}"
            return nan

old_df = df.copy()

phone_numbers = ["phone_number", "parent_cellphone_number"]
df[phone_numbers] = df[phone_numbers].map(format_phone)



student_numbers = df[df[phone_numbers].isna().any(axis=1)]["student_number"]
print(old_df[old_df["student_number"].isin(student_numbers)])
df = df.dropna(subset=phone_numbers)
