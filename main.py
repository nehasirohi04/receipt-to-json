import base64
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()


from pydantic import BaseModel, Field

from pathlib import Path


class rcp_info(BaseModel):
    merchant: str | None = Field(
        description="Name exactly as printed on the bill")
    date: str | None = Field(
        description="Bill date in YYYY-MM-DD format")
    total: float | None = Field(
        description="Final amount payable, after discounts and round-off")
    tax: float | None = Field(
        description="Total tax shown on the bill (GST, VAT, sales tax, or CGST + SGST combined), even if included in the total. Null if no tax is shown.")
MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

def extract(path):
    with open(path,"rb") as f:
        img = base64.standard_b64encode(f.read()).decode()

    client = OpenAI()
    media = MEDIA_TYPES[path.suffix.lower()]            
    resp = client.responses.parse(
        model="gpt-5.4-mini",
        input=[{"role": "user", "content": [
            {"type": "input_text",
            "text": "Read this receipt. List merchant, date, total and tax."},
            {"type": "input_image",
            "image_url": f"data:{media};base64,{img}"},
            
        ]}],
        text_format=rcp_info
    )
    return resp.output_parsed

Path("outputs").mkdir(exist_ok=True)

images = [p for p in Path("receipts").iterdir()
          if p.suffix.lower() in MEDIA_TYPES]

for path in sorted(images):
    try:
        r = extract(path)
        out = Path("outputs") / f"{path.stem}.json"
        out.write_text(r.model_dump_json(indent=2), encoding="utf-8")
        print("OK  ", path.name, r.total)
    except Exception as e:
        print("FAIL", path.name, e)