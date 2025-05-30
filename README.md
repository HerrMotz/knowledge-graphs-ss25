# Group 05 — Becks

## Week 1 — Modelling
Please open [modelling.pdf](https://git.uni-jena.de/fusion/teaching/project/2025sose/KnowledgeGraphs/group-05/-/blob/main/modelling.pdf)

## Week 2 — Create KG from Tabular Data
The pipeline works as follows:

1. Extract ingredients from the dataset (tabular data) using a large language model `create_batch.py`, `upload_batch.py`
2. Download the results using `get_batch_results.py`
3. Map the ingredients to WikiData items using elastic search and a SPARQL query `ingredient_QID_mapping.py`
4. Extract cities from the dataset and map them to WikiData items `city_QID_mapping.py`
5. Use `rdflib` to integrate the three data sources into statements within the ontology `integrate_tabular_data_with_ontology.py`
   1. Add the pizza places with schema.org-addresses
   2. Create the pizzas
      1. The ontology has existing ingredients. Again override the mapping to the entities from within the ontology using
           `KNOWN_INGREDIENTS`
      2. Add these ingredients (hierarchy: use ontology ingredients → use wikidata items → create canonical ingredient in the ontology)
      3. Add the price
   3. Write the results to `pizza_data.ttl`

### Possible improvements
+ It is obvious that the ontology is in German and the data is English, and it would be nice to unify them
    We made an informed decision to keep them different, to show that they can be integrated, even though different
    languages were used. Furthermore, we could use this for other cases, were different, but equivalently legitimate 
    terminology was used.
+ Add place categories to Pizzeria, like "Burger Place", "University", ...
+ The list of KNOWN_INGREDIENTS should only contain ingredients which are not present in WikiData. 
    Furthermore, it would be even better to add the missing ingredients to WikiData, instead of
    defining them in our ontology. But this script's purpose it to show what can be done, not the real deal.
+ We could, instead of creating our own ontology, use `schema.org` for any assertion.

```turtle
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <http://example.org/> .
@prefix schema: <http://schema.org/> .

ex:Store1 a schema:FoodEstablishment ;
  schema:hasMenuItem ex:MenuItem1 .

ex:MenuItem1 a schema:MenuItem ;
  schema:name "Cheeseburger" ;
  schema:price "5.99"^^xsd:decimal ;
  schema:priceCurrency "USD" .
```