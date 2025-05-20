import csv
import json

MODEL = "gpt-4.1-nano"
SYSTEM_PROMPT = """Analyze a single item to determine if it qualifies as a pizza based on its name and description.

# Steps

1. **Identify if the Item is a Pizza**:
   - Evaluate the "name" field. If it explicitly mentions "pizza," it can also not be a pizza, for example a "Pizza Bagel" or "Pizza Sub" is not a pizza.
   - Alternatively, if the "description" contains typical pizza ingredients (e.g., dough, cheese, sauce), and the name doesn't explicitly indicate a non-pizza item, classify it as a pizza.
   - The names may contain spelling errors or weird punctuation. These should be cleaned up.

2. **Extract Ingredients**:
   - Parse the "description" field to list all mentioned components as ingredients.
   - The description field may indicate, that there are more than one menu item with different options. Split these up into separate entries.

3. **Output Decision**:
   - Determine if the item is identified as a pizza and list the results.

# Output Format

Provide the output in JSON format with the following structure:
- `"is_pizza"`: A boolean indicating if the item is identified as pizza.
- `"ingredients"`: A list of ingredients extracted from the description. Simplify them, e.g. "fresh mozzarella" should just be "mozzarella". Filter out non-ingredients (like "thick" or some "style").

# Example

**Input:**
name: "Hawaiin Pizza" description: "Pineapple, Ham."

**Output:**
```json
{
  "name": "Pizza Hawaii",
  "is_pizza": true,
  "ingredients": ["Pineapple", "Ham"]
}
```"""

def read_csv(file_path):
    items = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        lol = 0
        reader = csv.DictReader(f)
        for row in reader:
            lol+=1
            name = row["menu item"]
            description = row["item description"] or ""
            items.append({
                "custom_id": f"{lol}_{row['name']}_{name}".replace(" ", "_").replace(",", ""),  # unique ID for batch
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"name: \"{name}\" description: \"{description}\""}
                    ],
                    "temperature": 1,
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
    batch_items = read_csv(csv_file_path)
    write_jsonl(batch_items)
