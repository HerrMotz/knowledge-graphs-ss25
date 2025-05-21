import csv
import json

MODEL = "gpt-4.1-nano"
SYSTEM_PROMPT = """Analyze an item to determine if it qualifies as a pizza based on its name and description.

Evaluate the "name" field and "description" for typical pizza ingredients. Simplify ingredient names and separate multiple items in descriptions. Use real world knowledge to fill in assumed typical ingredients to a pizza based on its name. Do not include non-ingredients in the ingredient list, e.g. "thick pan" is not an ingredit.

Output in JSON:
- `"is_pizza"`: Boolean indicating if the item is a pizza.
- `"ingredients"`: List of simplified ingredients.

# Examples

**Input:**
name: "Hawaiin Pizza" description: "Pineapple, Ham."

**Output:**
```json
{
  "name": "Pizza Hawaii",
  "is_pizza": true,
  "ingredients": ["Pineapple", "Ham"]
}
```

**Input:**
name: "Pizza, Margherita" description: ""

**Output:**
```json
{
  "name": "Pizza Margherita",
  "is_pizza": true,
  "ingredients": ["basil", "mozzarella", "tomato", "olive oil"]
}
```"""

included_lines = [20, 10, 24, 11, 5, 42, 44, 45, 46, 55, 60, 59, 40, 83, 102, 103, 172, 179, 189]  # Example line numbers

def read_csv(file_path, included_lines):
    items = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader):
            if index-1 in included_lines:
                name = row["menu item"]
                description = row["item description"] or ""
                items.append({
                    "custom_id": f"{index}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"name: \"{name}\" description: \"{description}\""}
                        ],
                        "temperature": 1,
                        "max_tokens": 1000,
                    }
                })
    return items

def write_jsonl(items, output_path="openai_batch_input.jsonl"):
    with open(output_path, "w", encoding="utf-8") as f:
        for item in items:
            json.dump(item, f)
            f.write("\n")
    print(f"✅ Batch input written to {output_path}")

if __name__ == "__main__":
    csv_file_path = "data.csv"
    batch_items = read_csv(csv_file_path, included_lines)
    write_jsonl(batch_items)
