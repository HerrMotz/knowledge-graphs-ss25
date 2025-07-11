import json
import requests
import time
import os
import csv

def main():
    unique_cities = set()

    # create cities.txt
    with open('data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            city = row["city"].strip()
            if city:  # Only add non-empty city names
                unique_cities.add(city)

    with open('cities.txt', 'w', encoding='utf-8') as output_file:
        for city in sorted(unique_cities):  # Sort for consistent order
            output_file.write(f"{city}\n")

    # work with cities.txt as input

    # Load existing city mappings if available
    city_qid_map = {}
    if os.path.exists("locked_city_qid_map.json"):
        with open("locked_city_qid_map.json", "r", encoding="utf-8") as f:
            city_qid_map = json.load(f)

    # File containing city names (one per line)
    input_filename = "cities.txt"

    # Read all unique cities from an input file
    all_cities = set()
    with open(input_filename, 'r', encoding='utf-8') as f:
        for line in f:
            city = line.strip()
            if city:
                all_cities.add(city)


    # SPARQL query to find city QIDs
    def get_wikidata_qid(city_name):
        # Escape quotes in city names
        safe_name = city_name.replace('"', '\\"')

        query = f"""
        SELECT DISTINCT ?item ?itemLabel WHERE {{
          SERVICE wikibase:mwapi {{
            bd:serviceParam wikibase:endpoint "www.wikidata.org";
                            wikibase:api "EntitySearch";
                            mwapi:search "{safe_name}";
                            mwapi:language "en".
            ?item wikibase:apiOutputItem mwapi:item.
          }}
    
          # Filter for city types
          VALUES ?cityTypes {{
            wd:Q515     # City
            wd:Q1549591 # Big city
            wd:Q486972  # Human settlement
            wd:Q3957    # Town
            wd:Q7930989 # Village
          }}
          ?item (wdt:P31|wdt:P279) ?cityTypes.
    
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 1
        """

        url = "https://query.wikidata.org/sparql"
        headers = {"Accept": "application/json"}
        params = {"query": query, "format": "json"}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json().get("results", {}).get("bindings", [])
                if results:
                    return results[0]["item"]["value"].split("/")[-1]  # Extract QID
        except Exception as e:
            print(f"Query failed for {city_name}: {str(e)}")
        return None


    # Create/update mapping for cities
    for city in sorted(all_cities):
        # Skip existing entries
        if city in city_qid_map:
            status = "🔒 locked" if city_qid_map[city].get("locked") else "✅ exists"
            print(f"{city}: {status} ({city_qid_map[city].get('qid', 'N/A')})")
            continue

        # Fetch QID from Wikidata
        qid = get_wikidata_qid(city)
        city_qid_map[city] = {
            "qid": qid,
            "locked": False
        }

        # Print status
        if qid:
            print(f"{city}: ✅ http://www.wikidata.org/entity/{qid}")
        else:
            print(f"{city}: ❌ not found")

        time.sleep(1)  # Respect rate limits

    # Save updated mapping
    with open("city_qid_map.json", "w", encoding="utf-8") as f:
        json.dump(city_qid_map, f, ensure_ascii=False, indent=2)

    print(f"\nProcessed {len(all_cities)} cities. Mapping saved to city_qid_map.json")

if __name__ == "__main__":
    main()