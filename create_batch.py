import csv
import json

MODEL = "gpt-4.1-nano"
SYSTEM_PROMPT = """Analyze an item to determine if it qualifies as a pizza based on its name and description.

Use the following guidelines to determine whether an item can be classified as a pizza. Assess both the "name" and "description" fields to identify typical pizza ingredients. Simplify ingredient names, and separate multiple items found in descriptions. Leverage real-world knowledge to infer assumed typical ingredients based on the name of the item. Exclude non-ingredients like "thick pan" from the ingredient list.

# Steps
1. Ingredient Evaluation: Look for typical pizza ingredients in both the "name" and "description" fields.
2. Simplification: Simplify and unify the ingredient names.
3. Exclusion: Do not include non-ingredients in the list.
4. Assumption: Assume typical ingredients based on the item name when description is incomplete.

# Output Format
- `"name"`: The name of the menu item. Use simplified canonical names for known pizzas, e.g. Veggie Lovers Pizza -> Vegetarian Pizza.
- `"is_pizza"`: Boolean indicating if the item is a pizza.
- `"ingredients"`: List of simplified ingredients.

If the input suggests that they could be multiple menu items, then output an array of menu items, e.g. Chesse or Pepperoni pizza should give an array if menu items.

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
```

# Notes
- Ensure the analysis is based on known pizza ingredients and doesn't solely depend on the presence of the word "pizza" in the name.
- Consider edge cases where names may suggest pizza-style but are misleading (e.g., "Pizza Bagel" is not a pizza).
- Simplify the ingredients. E.g. canadian bacon should be bacon, green pepper should be pepper, and so on."""

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
