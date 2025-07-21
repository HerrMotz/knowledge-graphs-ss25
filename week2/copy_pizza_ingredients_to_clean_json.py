import json

INPUT_FILE = "./llm_results/results_15_complete.jsonl"
OUTPUT_FILE = "menu_items.json"

def extract_pizza_items(input_path):
    menu_items = []

    with open(input_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                record = json.loads(line)
                content = record["response"]["body"]["choices"][0]["message"]["content"]

                # Extract JSON object from within triple-backtick block
                json_start = content.find("{")
                json_end = content.rfind("}")
                if json_start == -1 or json_end == -1:
                    continue

                json_str = content[json_start:json_end+1]
                item = json.loads(json_str)

                if item.get("is_pizza") is True and isinstance(item.get("ingredients"), list):
                    menu_items.append({
                        "name": item["name"],
                        "ingredients": item["ingredients"]
                    })

            except (json.JSONDecodeError, KeyError, TypeError):
                continue  # skip invalid or malformed entries

    return menu_items

def write_to_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    pizzas = extract_pizza_items(INPUT_FILE)
    write_to_json(pizzas, OUTPUT_FILE)

