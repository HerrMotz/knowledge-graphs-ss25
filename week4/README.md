# Week 4 — Ontology Alignment

## Starting Considerations

The given external ontology by Rector et al. only describes dishes and what makes them characteristic. For example, the
dishes (or foods) pizza and ice cream are described. _Ice Cream_, _Pizza_, _Pizza Base_ and _Food Topping_ are in the same
ontological hierarchy (using the subclass relation) and all categorised as _Food_. This is a bit confusing, especially 
because _Food Topping_ only has one subclass, namely _Pizza Topping_. More confusingly, _Ice Cream_ can have an instance 
of _Fruit Topping_ (subclass of _Pizza Topping_), with the only subclass being _Sultana Topping_.



## Hints for Running these scripts

You want to install torch with CUDA support (if you have a CUDA gfx ofc). For CUDA 12.x use also 12.1:

```shell
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
```

There is a [full guide on installing torch](https://pytorch.org/get-started/locally/) and which wheels to use for which CUDA version.

Furthermore, there is a bug the ontodeep package for some reason. Go ahead and change line 149 in `.\.venv\site-packages\deeponto\align\mapping.py` to:
```py
if not threshold or dp.Score >= threshold:
```

Furthermore, you need to change the `__init__.py` for BertSubs located at `venv\Lib\site-packages\deeponto\align\bertsubs\__init__.py`. Replace the code line with:
```py
from deeponto.complete.bertsubs import BERTSubsInterPipeline, DEFAULT_CONFIG_FILE_INTER
```

so that it exports the configuration file.