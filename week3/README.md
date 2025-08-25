# Week 3 — Querying

## Reasoning over the ontology

The task specifies to "perform reasoning with the ontology and the generated data". I interpret this to ask for the 
deductive closure of A- and T-Box. The [inferred_data.ttl](before_improvement/inferred_data.ttl) file contains the result of this reasoning
step.

## Generate the deductive hull
```shell
python reasoning.py
```

## File Descriptions
After I made the change of the "integration of tabular data step", I was able to make more advanced queries in this step.
Therefore, I have now two directories containing queries:
- `after_improvement/` contains the queries/results after the improvements
- `before_improvement/` before the improvements.

I only posted changed queries in the `after_improvement/` directory. These are "average price of a pizza margherita" and "pizza without tomato".

| File                                                                                 | Description                                                                                                                             |
|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| [pizza_data.ttl](/week2/pizza_data.ttl)                                              | The output of [integrate_tabular_data_with_ontology.py](/week2/integrate_tabular_data_with_ontology.py). Does not contain the ontology. |
| [statements.ttl](before_improvement/statements.ttl)                                                     | subtask 1: The graph with all inferences (deductive closure) over the ontology and [pizza_data.ttl](/week2/pizza_data.ttl).             |
| [pizza_without_tomato.sparql](before_improvement/pizza_without_tomato.sparql)                           | subtask 2: The query which fetches all restaurants that do not offer Pizza with tomato toppings.                                        |
| [average_price_of_pizza_margherita.sparql](before_improvement/average_price_of_pizza_margherita.sparql) | subtask 3: The query which fetches the avg price of a Pizza Margherita                                                                  |
| [restaurants_by_city.sparql](before_improvement/restaurants_by_city.sparql)                             | subtask 4                                                                                                                               |
| [restaurants_with_missing_postcode.sparql](before_improvement/restaurants_with_missing_postcode.sparql) | subtask 5                                                                                                                               |


> [!TIP]
> Owlrl generated really wrong stuff. See the example below:

```turtle
...
<http://www.wikidata.org/entity/Q967547> owl:sameAs <http://www.wikidata.org/entity/Q967547> .

<http://www.wikidata.org/entity/Q976490> owl:sameAs <http://www.wikidata.org/entity/Q976490> .

<http://www.wikidata.org/entity/Q97927338> owl:sameAs <http://www.wikidata.org/entity/Q97927338> .

<http://www.wikidata.org/entity/Q982550> owl:sameAs <http://www.wikidata.org/entity/Q982550> .

<http://www.wikidata.org/entity/Q986654> owl:sameAs <http://www.wikidata.org/entity/Q986654> .

<http://www.wikidata.org/entity/Q992432> owl:sameAs <http://www.wikidata.org/entity/Q992432> .

<http://www.wikidata.org/entity/Q993064> owl:sameAs <http://www.wikidata.org/entity/Q993064> .

<http://www.wikidata.org/entity/Q994000> owl:sameAs <http://www.wikidata.org/entity/Q994000> .

0.25 a xsd:decimal ;
    owl:sameAs 0.25 .

0.69 a xsd:decimal ;
    owl:sameAs 0.69 .

0.75 a xsd:decimal ;
    owl:sameAs 0.75 .

0.99 a xsd:decimal ;
    owl:sameAs 0.99 .

1.15 a xsd:decimal ;
    owl:sameAs 1.15 .

1.25 a xsd:decimal ;
    owl:sameAs 1.25 .
...
```

---

# Actual Task: SPARQL and Reasoning

* Subtask SPARQL.1 Perform reasoning with the created ontology and the generated data. Save the extended graph in turtle format (.ttl) (10%).

Write SPARQL queries, according to the requirements in the following subtasks, and execute them over the created ontology and the generated data.

* Subtask SPARQL.2 Return all the details of the restaurants that sell pizzas without tomato (i.e., pizza bianca). Return the results as a CSV file (20%).

* Subtask SPARQL.3 Return the average prize of a Margherita pizza (20%).

* Subtask SPARQL.4 Return number of restaurants by city, sorted by state and number of restaurants (20%).

* Subtask SPARQL.5 Return the list of restaurants with missing postcode (20%).

Subtask SPARQL.6 Correctness of the queries and code, and documentation of the created SPARQL queries in the report (10%).