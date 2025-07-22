import json
import csv

# Load the JSON data from the specified file path
with open("before_improvement/restaurants_with_missing_postcode.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

# Extract the variables (column headers)
headers = json_data["head"]["vars"]

# Open a CSV file for writing
with open("before_improvement/restaurants_with_missing_postcode.csv", mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(headers)

    # Write each row of data
    for binding in json_data["results"]["bindings"]:
        row = []
        for key in headers:
            value = binding.get(key, {}).get("value", "")
            row.append(value)
        writer.writerow(row)

print("CSV file 'restaurants_with_missing_postcode.csv' created successfully.")
