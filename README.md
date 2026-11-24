# receipt-to-json

Turn a photo of a receipt into clean JSON (merchant, date, total, tax) using an LLM, and measure how often it gets each field right.


## Why

Expense data gets stuck on paper. Nobody types receipts in by hand, so the spending never gets tracked. This project reads the four fields that matter from a photo, so a bill can go straight into an expense tracker.

## Results

Scored against a hand-labelled answer key: 10 receipts, 40 fields.

| Field       | Accuracy |
|-------------|----------|
| Merchant    | 100%     |
| Date        | 90%      |
| Total       | 80%      |
| Tax         | 90%      |
| **Overall** | **90%**  |

The receipts come from several countries, including India, Australia, the US and Russia, so the set mixes day-first and month-first dates and different tax systems (GST, VAT, sales tax, CGST + SGST).

## How it works

1. `main.py` sends each receipt image to an OpenAI model.
2. A Pydantic schema defines the four fields, with a description for each (for example, "total" means the final amount payable, after discounts and round-off). Structured outputs make the model return valid JSON in that shape.
3. Each result is saved to `outputs/<receipt>.json`. A receipt that fails is logged and skipped, so one bad image doesn't stop the run.
4. `score.py` compares every output with `answer_key.csv`, field by field, and writes the details to `results.csv`.

### What counts as correct

- **Merchant:** lowercased, punctuation and extra spaces removed, then fuzzy-matched with `difflib.SequenceMatcher` at a 0.95 cut-off. This accepts formatting differences, such as a trailing full stop, but rejects near-misses such as "walmart store 1234" vs "walmart store 1243" (0.944).
- **Date:** exact match, in `YYYY-MM-DD` format.
- **Total and tax:** equal to within 0.01.
- **Empty fields:** if the bill shows no value and the model returns null, that counts as correct.

## What I learned

The first score was 70%. Switching merchant matching from exact to fuzzy raised it to 75%.

Then I checked each of the 10 remaining misses against the bill ([error_analysis.md](error_analysis.md)):

- **6 were mistakes in my answer key**, not the model.
- **2 were real model errors:** it read a total of 53.32 as 52.32, and a date of 2024-06-24 as 2024-06-20.
- **2 couldn't be checked**, because I couldn't read those values on the bill.

After fixing the answer key, the score was 90%.

## Limitations

- 10 receipts is a small set: one field is worth 2.5 percentage points, so treat these numbers as a first measurement, not a benchmark.
- The 0.95 cut-off was chosen using the same receipts it scores.
- One receipt's total and tax couldn't be verified from the bill. They're still in the score, so they count as misses.
- The model's output can vary slightly between runs.


## Run it

```
pip install -r requirements.txt
# put OPENAI_API_KEY=... in a .env file
# add receipt images to receipts/
python main.py    # receipts/ → outputs/
python score.py   # outputs/ vs answer_key.csv → results.csv
```