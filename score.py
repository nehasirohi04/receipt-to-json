import json
from pathlib import Path
import pandas as pd
from difflib import SequenceMatcher
MERCHANT_CUTOFF = 0.95



key = pd.read_csv("answer_key.csv")

rows = []
for f in Path("outputs").glob("*.json"):
    data = json.loads(f.read_text(encoding="utf-8"))
    data["file"] = f.stem
    rows.append(data)
pred = pd.DataFrame(rows)

df = key.merge(pred, on="file", how="left", suffixes=("_key", "_pred"))
print(df)

def blank(x):
    return pd.isna(x) or str(x).strip() == ""

def num_match(x, y):
    if blank(x) and blank(y):
        return blank(x) and blank(y)
    return abs(float(x) - float(y)) < 0.01

def text_match(x, y):
    if blank(x) and blank(y):
        return True
    return str(x).strip().lower() == str(y).strip().lower()


def clean(s):
    s=s.strip().lower()
    s="".join(ch for ch in s if ch.isalnum() or ch.isspace())
    return s



def fuzzy_match(a, b):
    if blank(a) or blank(b):
        return blank(a) and blank(b)
    score = SequenceMatcher(None, clean(a), clean(b)).ratio()
    return score >= MERCHANT_CUTOFF


rules = {"merchant": fuzzy_match, "date": text_match,
         "total": num_match, "tax": num_match}

for field, match in rules.items():
    df[f"{field}_ok"] = [match(k, p) for k, p in
                         zip(df[f"{field}_key"], df[f"{field}_pred"])]
    print(f"{field:9} {df[f'{field}_ok'].mean():.0%}")

ok_cols = [f"{field}_ok" for field in rules]
print(f"{'overall':9} {df[ok_cols].values.mean():.0%}")

df.to_csv("results.csv", index=False)