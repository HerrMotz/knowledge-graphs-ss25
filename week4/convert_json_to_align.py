#!/usr/bin/env python3

import json
import argparse
from pathlib import Path

# Known prefixes
PREFIXES = {
    "pizza": "http://www.co-ode.org/ontologies/pizza/pizza.owl#",
    "city": "http://www.semanticweb.org/city/in3067-inm713/2024/restaurants#",
}
ALT_PIZZA = "http://www.co-ode.org/ontologies/pizza#"  # some entries use this base

TTL_HEADER = """@prefix align: <http://knowledgeweb.semanticweb.org/heterogeneity/alignment#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix city:    <http://www.semanticweb.org/city/in3067-inm713/2024/restaurants#> .
@prefix pizza: <http://www.co-ode.org/ontologies/pizza/pizza.owl#> .

[] a align:Alignment ;
"""

def qname(uri: str) -> str:
    """Return a QName using the known prefixes, or wrap the URI in <> if unknown."""
    if uri.startswith(PREFIXES["pizza"]):
        return f"pizza:{uri[len(PREFIXES['pizza']):]}"
    if uri.startswith(ALT_PIZZA):
        return f"pizza:{uri[len(ALT_PIZZA):]}"
    if uri.startswith(PREFIXES["city"]):
        return f"city:{uri[len(PREFIXES['city']):]}"
    return f"<{uri}>"

def main():
    parser = argparse.ArgumentParser(description="Convert JSON mappings to Alignment API TTL.")
    parser.add_argument("input", help="Path to the JSON file with mappings.")
    parser.add_argument("-o", "--output", default="-", help="Output TTL file (default: stdout).")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text())

    cells = []
    for key, pairs in data.items():
        if not pairs:
            continue
        for pair in pairs:
            # Expect pair format: [pizza_uri, city_uri, score]
            # But we’ll detect which is which just in case.
            uri_a, uri_b, score = pair
            if uri_a.startswith(PREFIXES["city"]) or uri_a.startswith("http://www.semanticweb.org/"):
                city_uri, pizza_uri = uri_a, uri_b
            else:
                pizza_uri, city_uri = uri_a, uri_b

            cell = f"""   align:map [
      a align:Cell ;
      align:entity1 {qname(city_uri)} ;
      align:entity2 {qname(pizza_uri)} ;
      align:relation "=" ;
      align:measure "{float(score):.6f}"^^xsd:float
   ]"""
            cells.append(cell)

    # Join all cells; the last one ends with " ."
    ttl_body = " ;\n".join(cells) + " .\n"

    ttl = TTL_HEADER + ttl_body

    if args.output == "-":
        print(ttl)
    else:
        Path(args.output).write_text(ttl)
        print(f"Wrote {args.output}")

if __name__ == "__main__":
    main()
