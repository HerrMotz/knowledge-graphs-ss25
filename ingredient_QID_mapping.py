import json
import requests
import time
import os

ingredient_qid_map = {}

#load existing mapping if available
if os.path.exists("ingredient_qid_map.json"):
    with open("ingredient_qid_map.json", "r", encoding="utf-8") as f:
        ingredient_qid_map = json.load(f)

filename = "results_13.jsonl"

#set of all ingredients
all_ingredients = set()

#extract ingredients from JSONL file
with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        try:
            _x = data['response']['body']['choices'][0]['message']['content']
            _x = _x.replace("```json", "").replace("```", "")
            ingredients = json.loads(_x).get('ingredients', [])
            all_ingredients.update(ingredients)
        except Exception as e:
            print(f"Fehler beim Verarbeiten: {e}")

#SPARQL query for exact search
def get_wikidata_qid(ingredient):
    query = f"""
    SELECT ?item ?itemLabel WHERE {{
      # Use the built-in MediaWiki EntitySearch service (wbsearchentities)
      SERVICE wikibase:mwapi {{
        bd:serviceParam wikibase:endpoint "www.wikidata.org";
                        wikibase:api       "EntitySearch";
                        mwapi:search       "{ingredient}";   # prefix you’re looking for
                        mwapi:language     "en";             # or "de", etc.
                        mwapi:limit        "1".              # internal limit is faster than SPARQL LIMIT
        ?item wikibase:apiOutputItem mwapi:item .
      }}
    
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 1
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/json"}
    params = {"query": query}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()["results"]["bindings"]
        if results:
            return results[0]["item"]["value"].split("/")[-1]  #extract QID
    return None

#SPARQL query for fuzzy search -- not used right now
def get_wikidata_qid_fuzzy(ingredient):
    query = f"""
    SELECT ?item ?itemLabel WHERE {{
      SERVICE wikibase:mwapi {{
        bd:serviceParam wikibase:endpoint "www.wikidata.org";
                        wikibase:api "EntitySearch";
                        mwapi:search "{ingredient}";
                        mwapi:language "en".
        ?item wikibase:apiOutputItem mwapi:item.
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 1
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/json"}
    params = {"query": query}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()["results"]["bindings"]
        if results:
            return results[0]["item"]["value"].split("/")[-1]
    return None

#checks if QID is a food item by checking if there is a path from QID to Q19861951 (food item) in Wikidata -- not used right now
def is_food_item(qid):
    query = f"""
    ASK {{
      wd:{qid} wdt:P31/wdt:P279* wd:Q19861951.
    }}
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    params = {"query": query}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("boolean", False)
    return False



#create mapping of ingredients to QIDs
ingredient_qid_map = {}

locked_qid_map = {}

with open("locked_qid_map.json", "r", encoding="utf-8") as f:
    locked_qid_map = json.load(f)
for ingredient in sorted(all_ingredients):
    entry = locked_qid_map.get(ingredient)

    #skip locked entries
    if entry and isinstance(entry, dict) and entry.get("locked"):
        print(f"{ingredient}: 🔒 locked ({entry['qid']})")
        continue

    #get QID from Wikidata
    qid = get_wikidata_qid(ingredient)
    if not qid:
        print(f"{ingredient}: ❌ not found")
    else:
        print(f"{ingredient}: ✅ http://www.wikidata.org/entity/{qid}")

    #save QID to mapping
    ingredient_qid_map[ingredient] = {
        "qid": qid,
        "locked": False
    }

    time.sleep(1)  #for rate limit

#save mapping to JSON
with open("ingredient_qid_map.json", "w", encoding="utf-8") as f:
    json.dump(ingredient_qid_map, f, ensure_ascii=False, indent=2)