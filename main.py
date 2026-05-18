import pandas as pd
from sys import argv, exit
from phonenumbers import parse, format_number, is_valid_number, PhoneNumberFormat
from numpy import nan

if len(argv) < 2:
    print(f"Usage: python {argv[0]} <input CSV>")
    exit(1)

df = pd.read_csv(
    argv[1],
    encoding="utf-8",
    dtype={"phone_number": str, "parent_cellphone_number": str},
)

# 全ての空欄について、NaNとして扱う。
df = df.replace("", nan)

# 念の為カラムを絞る

df = df[
    [
        "student_number",
        "is_male",
        "first_name",
        "last_name",
        "school_grade",
        "phone_number",
        "parent_name",
        "parent_first_name",
        "parent_last_name",
        "parent_cellphone_number",
    ]
]

# 学籍番号を大文字にする
df["student_number"] = df["student_number"].str.upper()

# is_maleをgenderに写し、is_maleカラムを捨てる
df["gender"] = df["is_male"].map({1: "男", 0: "女"})
df = df.drop(columns=["is_male"])

# 学年の表記を指定された形式にする
df["school_grade"] = df["school_grade"].map(
    {
        1: "1年",
        2: "2年",
        3: "3年",
        4: "4年",
        5: "修1",
        6: "修2",
        7: "博1",
        8: "博2",
        9: "博3",
    }
)

# 電話番号にハイフンを入れる


def format_phone(val):
    # NaNにはNaNを
    if pd.isna(val):
        return nan
    # 電話番号(ハイフンなし)をパースする。 "JP"を指定しているのは、国内電話番号周りのため
    parsed = parse(val, "JP")

    def format(parsed):
        # 日本国内の電話番号だった場合、国内電話の番号として出力
        if parsed.country_code == 81:
            return format_number(parsed, PhoneNumberFormat.NATIONAL)
        # そうでなかった場合、国際電話の番号として出力
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
            return nan


# 変換適用前のデータフレームを保持する
old_df = df.copy()

phone_numbers = ["phone_number", "parent_cellphone_number"]
df[phone_numbers] = df[phone_numbers].map(format_phone)


# パースできなかった or NaNであった レコードの学籍番号一覧を取得
student_numbers = df[df[phone_numbers].isna().any(axis=1)]["student_number"]
# 旧DFからレコードを持ってきて、だめだったやつを表示
print("\n\n-----failed to parse phone number-----\n")
print(old_df[old_df["student_number"].isin(student_numbers)])

# だめだったやつを捨てる
df = df.dropna(subset=phone_numbers)

# ユーザ本人について、(デジコア側の事情で)氏名が逆に入っているので、修正する

df[["first_name", "last_name"]] = df[["last_name", "first_name"]]

# 保護者氏名の分離
# parent_nameに名前が存在し、parent_{last,first}_nameが空、
# 全てについて非NaN、parent_nameのみNaN という3種類の"正常"な状態が存在する。
# 部員名簿上、保護者の氏名の間に空白を入れる必要があるため、氏名を分離した状態で格納したい。
# 保護者と本人の名字は大体のケースにおいて一致するため、本人の氏をベースとして判定する。
# これだけではコケるケースもあるため、フォールバック的な処理も行う。


def split_parent_name(row):
    p_name = row["parent_name"]
    p_first = row["parent_first_name"]
    p_last = row["parent_last_name"]
    s_last = row["last_name"]

    if pd.notna(p_first) and pd.notna(p_last):
        return p_last, p_first

    if pd.isna(p_name):
        return p_last, p_first

    # 1. 空白での分割を試みる
    parts = str(p_name).strip().split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])

    # 2. 本人の名字で始まるかチェック
    if pd.notna(s_last):
        s_last_str = str(s_last).strip()
        p_name_str = str(p_name).strip()
        if p_name_str.startswith(s_last_str):
            first = p_name_str[len(s_last_str) :].strip()
            if first:
                return s_last_str, first

    # 3. 分割できない場合は、parent_nameを名字とし、名前を空(NaN)にする
    return nan, nan


old_df = df.copy()

# 実行
name_columns = ["parent_last_name", "parent_first_name"]
df[name_columns] = df.apply(lambda row: pd.Series(split_parent_name(row)), axis=1)

# パースに失敗していそうなレコードの学籍番号を取得
student_numbers = df[df[name_columns].isna().any(axis=1)]["student_number"]

# 旧DFからレコードを持ってきて、だめだったやつを表示
print("\n\n-----failed to parse parent name-----\n")
print(old_df[old_df["student_number"].isin(student_numbers)])

# parent_nameを削除
df = df.drop(columns=["parent_name"])


# done!
print("\n\n")
print(df)

df.to_csv("./out.csv", index=False)
