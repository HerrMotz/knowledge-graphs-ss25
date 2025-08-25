# Week 4 — Ontology Alignment

## Starting Considerations

The given external ontology by Rector et al. only describes dishes and what makes them characteristic. For example, the
dishes (or foods) pizza and ice cream are described. _Ice Cream_, _Pizza_, _Pizza Base_ and _Food Topping_ are in the same
ontological hierarchy (using the subclass relation) and all categorised as _Food_. This is a bit confusing, especially 
because _Food Topping_ only has one subclass, namely _Pizza Topping_. More confusingly, _Ice Cream_ can have an instance 
of _Fruit Topping_ (subclass of _Pizza Topping_), with the only subclass being _Sultana Topping_.

## File Overview

| File                                                  | Description                                                                                                                    |
|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| [aml_alignment.rdf](/week4/outputs_own_ontology/aml_alignment.rdf)         | Alignment generated using AML                                                                                                  |
| [own_alignment.ttl](/week4/outputs_own_ontology/own_alignment.ttl)         | Own Alignment using Sequence Matching and ArgosTranslate                                                                       |
| [bert_raw_mapping.json](/week4/outputs_own_ontology/bert_raw_mapping.json) | BERTMap (as part of the deeponto package, which was extremely difficult to setup and still does not do everything it promises) |

## Prompts/Commands
### AML
Automatic Matching

### ChatLLM
```
Create an alignment between these two ontologies. Output it in Alignment API RDF format (same as AML/LogMap). Minimal pattern:

@prefix align: <http://knowledgeweb.semanticweb.org/heterogeneity/alignment#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

[] a align:Alignment ;
   align:map [
      a align:Cell ;
      align:entity1 <IRI_of_source_class> ;
      align:entity2 <IRI_of_target_class> ;
      align:relation "=" ;
      align:measure "0.87"^^xsd:float
   
   
 ] .
```


## Example usage for BERTMap
> [!TIP]
> You will first need to make some _manual_ changes to the package `deeponto` to make some fixes.
> Look in the section below

Run this command from the subfolder `week4`:
```shell
python bertmap_alignment.py ..\week1\ontology.xml existing_pizza.owl -c bertmap_config.yaml --subs-config bertsubs_config.yaml --output bertmap_equivalences.ttl --subs-output bertmap_subsumptions.ttl
```

## Required manual changes to the `deeponto` package

You want to install torch with CUDA support (if you have a CUDA gfx ofc). For CUDA 12.x use also 12.1:

```shell
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
```

There is a [full guide on installing torch](https://pytorch.org/get-started/locally/) and which wheels to use for which CUDA version.

Furthermore, there is a bug the ontodeep package for some reason. Go ahead and change line 149 in `.\.venv\site-packages\deeponto\align\mapping.py` to:
```py
if not threshold or dp.Score >= threshold:
```

Once more, you need to change the `__init__.py` for BertSubs located at `venv\Lib\site-packages\deeponto\align\bertsubs\__init__.py`. Replace the code line with:
```py
from deeponto.complete.bertsubs import BERTSubsInterPipeline, DEFAULT_CONFIG_FILE_INTER
```

so that it exports the configuration file.

--- 

# Actual Task: Ontology Alignment

Perform a basic alignment between the pizza.owl ontology and your created ontology. This alignment is important to perform SPARQL queries using the vocabulary of the pizza.owl ontology instead of the created ontology.

Link for the Pizza Ontology: https://moodle.uni-jena.de/pluginfile.php/1974943/mod_wiki/attachments/2070//pizza-ontology%20%281%29.zip?forcedownload=1

* Subtask OA.1 Compute equivalences between the entities of the input ontologies. Save the equivalences as triples in turtle format (.ttl). Tip: use owl:equivalentClass and owl:equivalentProperty as predicates of the equivalence triples (50%).

* Subtask OA.2 Repeat Subtask QA.1 using other two matching systems (e.g. AML and LogMap) . (20%)

Subtask OA.3 To evaluate the different matching systems, first generate matchings using: 1) your solution from OA.1 2) e.g. AML 3) e.g. LogMap for two provided ontologies: a) a model ontology (download https://drive.google.com/drive/folders/1WlINYleyUdV-rQst8qqBefiixwv9yGvR - pizza-restaurants-model-ontology) and b) the Pizza ontology Then: Calculate precision and recall using a given set of reference mappings https://moodle.uni-jena.de/pluginfile.php/1974943/mod_wiki/attachments/2070//reference-mappings-pizza%20%282%29.ttl?forcedownload=1] (10%).

Subtask OA.3 Correctness of the code and discussion of the used alignment techniques (20%).