import json
import requests
import time
import os

ingredient_qid_map = {}

# load existing mapping if available
if os.path.exists("ingredient_qid_map.json"):
    with open("ingredient_qid_map.json", "r", encoding="utf-8") as f:
        ingredient_qid_map = json.load(f)

filename = "results_13.jsonl"

# set of all ingredients
all_ingredients = set()

# extract ingredients from JSONL file
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


# SPARQL query for exact search
def get_wikidata_qid(ingredient):
    query = f"""
    SELECT DISTINCT ?item ?itemLabel WHERE {{
      SERVICE wikibase:mwapi {{
        bd:serviceParam wikibase:endpoint "www.wikidata.org" ;
                        wikibase:api      "EntitySearch" ;
                        mwapi:search      "{ingredient}" ;   # English label search, indexed
                        mwapi:language    "en" ;
                        mwapi:uselang     "en" .
        ?item wikibase:apiOutputItem mwapi:item .
      }}
    
      VALUES ?foodType {{
        wd:Q2095        # food
        wd:Q746549      # food ingredient
        wd:Q25403900    # food additive
        # the above classes should be enough
        # as the classes listed below are all
        # subclasses of food ingredient or additive
        wd:Q11004       # vegetable
        wd:Q9323487     # edible plant (plant as food)
        wd:Q207123      # herb
        wd:Q3088299     # cow's milk cheese
      }}
    
      ?item (wdt:P31|wdt:P279)+ ?foodType.
    
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,[AUTO_LANGUAGE]" }}
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
            return results[0]["item"]["value"].split("/")[-1]  # extract QID
    return None


# SPARQL query for fuzzy search -- not used right now
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


# checks if QID is a food item by checking if there is a path from QID to Q19861951 (food item) in Wikidata -- not used right now
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


# create mapping of ingredients to QIDs
ingredient_qid_map = {}

locked_qid_map = {}

with open("locked_qid_map.json", "r", encoding="utf-8") as f:
    locked_qid_map = json.load(f)
for ingredient in sorted(all_ingredients):
    entry = locked_qid_map.get(ingredient)

    # skip locked entries
    if entry and isinstance(entry, dict) and entry.get("locked"):
        print(f"{ingredient}: 🔒 locked ({entry['qid']})")
        continue

    # get QID from Wikidata
    qid = get_wikidata_qid(ingredient)
    if not qid:
        print(f"{ingredient}: ❌ not found")
    else:
        print(f"{ingredient}: ✅ http://www.wikidata.org/entity/{qid}")

    # save QID to mapping
    ingredient_qid_map[ingredient] = {
        "qid": qid,
        "locked": False
    }

    time.sleep(1)  # for rate limit

# save mapping to JSON
with open("ingredient_qid_map.json", "w", encoding="utf-8") as f:
    json.dump(ingredient_qid_map, f, ensure_ascii=False, indent=2)
