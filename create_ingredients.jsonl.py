import json

from validate_classification import load_results_jsonl

def main():
    res = load_results_jsonl("results_15_complete.jsonl")

    with open("ingredients.jsonl", "w", encoding="utf-8") as f:
        for item in res.values():
            json_line = json.dumps(item)
            f.write(json_line + "\n")

if __name__ == "__main__":
    main()
