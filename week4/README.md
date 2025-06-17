# Week 4 — Ontology Alignment

## Starting Considerations

The given external ontology by Rector et al. only describes dishes and what makes them characteristic. For example, the
dishes (or foods) pizza and ice cream are described. _Ice Cream_, _Pizza_, _Pizza Base_ and _Food Topping_ are in the same
ontological hierarchy (using the subclass relation) and all categorised as _Food_. This is a bit confusing, especially 
because _Food Topping_ only has one subclass, namely _Pizza Topping_. More confusingly, _Ice Cream_ can have an instance 
of _Fruit Topping_ (subclass of _Pizza Topping_), with the only subclass being _Sultana Topping_.