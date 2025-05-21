import csv
import json
import os

def load_csv_data(csv_path):
    items = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        lol = 0
        for row in reader:
            lol += 1
            menu_item = row["menu item"]
            description = row["item description"] or ""
            restaurant = row["name"]
            # Match an exact custom_id format
            custom_id = f"{lol-1}"
            items[custom_id] = {
                "restaurant": restaurant,
                "name": menu_item,
                "description": description
            }
    return items


def load_results_jsonl(jsonl_path):
    results = {}
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            custom_id = data.get("custom_id")
            response_text = None  # make sure it's always defined
            try:
                # Batch response format typically puts actual content in `response`
                if "response" in data and "body" in data["response"]:
                    choices = data["response"]["body"]["choices"]
                    response_text = choices[0]["message"]["content"]
                    parsed = json.loads(response_text)
                else:
                    raise KeyError("Missing 'choices' in response['body'].")
            except Exception as e:
                parsed = {
                    "error": f"Failed to parse: {e}",
                    "raw": response_text or json.dumps(data)
                }
            results[custom_id] = parsed
        return results

def find_matching_result_key(match_key, result_keys):
    for key in result_keys:
        if key.startswith(match_key):
            return key
    return None

def display_comparison(input_data, output_data):
    for match_key, item in input_data.items():
        print("=" * 60)
        print(f"Restaurant: {item['restaurant']}")
        print(f"Menu Item: {item['name']}")
        print(f"Description: {item['description']}")
        matching_result_key = find_matching_result_key(match_key, output_data.keys())

        if not matching_result_key:
            print("❌ No result found.")
        else:
            result = output_data[matching_result_key]
            if "error" in result:
                print("⚠️  Error:", result["error"])
                print("Raw:", result.get("raw", ""))
            else:
                print("✅ Output:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        # input("\nPress Enter to continue...")

if __name__ == "__main__":
    csv_path = "data.csv"
    result_path = "results_5.jsonl"

    if not os.path.exists(csv_path) or not os.path.exists(result_path):
        print(f"❌ Missing '{csv_path}' or '{result_path}'. Please make sure both files exist.")
        exit(1)

    input_data = load_csv_data(csv_path)
    output_data = load_results_jsonl(result_path)
    display_comparison(input_data, output_data)
