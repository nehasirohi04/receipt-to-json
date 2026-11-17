import base64
from openai import OpenAI

from pydantic import BaseModel, Field

from dotenv import load_dotenv
load_dotenv()


with open("receipts/r01.jpg","rb") as f:
  img = base64.standard_b64encode(f.read()).decode()

client = OpenAI()


class rcp_info(BaseModel):
    merchant: str | None = Field(
        description="Name exactly as printed on the bill")
    date: str | None = Field(
        description="Bill date in YYYY-MM-DD format")
    total: float | None = Field(
        description="Final amount payable, after discounts and round-off")
    tax: float | None = Field(
        description="Total tax (CGST + SGST combined)")


resp = client.responses.parse(
    model="gpt-5.4-mini",
    input=[{"role": "user", "content": [
        {"type": "input_text",
         "text": "Read this receipt. List merchant, date, total and tax."},
        {"type": "input_image",
         "image_url": f"data:image/jpeg;base64,{img}"},
         
    ]}],
    text_format=rcp_info
)
r = resp.output_parsed              
print(r)
# print(r.total)