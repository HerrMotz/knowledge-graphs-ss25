import json
import requests
import time

filename = "results.jsonl"

#set of all ingredients
all_ingredients = set()

#extract ingredients from JSONL file
with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        try:
            ingredients = json.loads(data['response']['body']['choices'][0]['message']['content']).get('ingredients', [])
            all_ingredients.update(ingredients)
        except Exception as e:
            print(f"Fehler beim Verarbeiten: {e}")

#SPARQL query for exact search
def get_wikidata_qid(ingredient):
    query = f"""
    SELECT ?item ?itemLabel WHERE {{
      ?item ?label "{ingredient}"@en.
      FILTER(STRSTARTS(STR(?item), "http://www.wikidata.org/entity/Q"))
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
            return results[0]["item"]["value"].split("/")[-1]  # Q-Nummer extrahieren
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


#create mapping of ingredients to QIDs
ingredient_qid_map = {}
for ingredient in sorted(all_ingredients):
    qid = get_wikidata_qid(ingredient)
    #if qid is None:
    #    qid = get_wikidata_qid_fuzzy(ingredient)
    ingredient_qid_map[ingredient] = qid
    print(f"{ingredient}: {qid}")
    time.sleep(1)  #for rate limit

#save mapping to JSON
with open("ingredient_qid_map.json", "w", encoding="utf-8") as f:
    json.dump(ingredient_qid_map, f, ensure_ascii=False, indent=2)