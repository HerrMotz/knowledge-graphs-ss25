# Week 4 — Ontology Alignment 🧑‍🔬

This project demonstrates an advanced ontology alignment pipeline using `BERTMap` and `BERTSubs` from the `deeponto` library to generate equivalence and subsumption mappings between two ontologies.

## Starting Considerations

The given external ontology by Rector et al. only describes dishes and what makes them characteristic. For example, the dishes (or foods) pizza and ice cream are described. _Ice Cream_, _Pizza_, _Pizza Base_ and _Food Topping_ are in the same ontological hierarchy (using the subclass relation) and all categorised as _Food_. This is a bit confusing, especially because _Food Topping_ only has one subclass, namely _Pizza Topping_. More confusingly, _Ice Cream_ can have an instance of _Fruit Topping_ (subclass of _Pizza Topping_), with the only subclass being _Sultana Topping_.

---

## ⚙️ Prerequisites & Setup

Before running the main script, several setup steps and manual patches are required due to library bugs and environment-specific issues, especially on Windows with modern Java versions.

### 1. Python & PyTorch Installation

First, install the required Python packages. It is highly recommended to use a virtual environment.

```shell
pip install rdflib argostranslate deeponto torch torchvision torchaudio
```

> [!IMPORTANT]
> If you have an NVIDIA GPU, install the version of PyTorch that matches your CUDA toolkit version for a massive speed-up. For CUDA 12.1, use this command:
> ```shell
> pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
> ```
> For other versions, refer to the [official PyTorch installation guide](https://pytorch.org/get-started/locally/).

### 2. Java Environment Variable

The alignment process calls an external Java `.jar` file. If you are using a modern Java version (JDK 9+), you **must** set the following environment variable in your shell session *before* running the script. This grants the necessary permissions that were restricted in recent Java versions.

> [!TIP]
> Run this command in your terminal every time you start a new session to run the alignment script.

```bash
export _JAVA_OPTIONS="--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED"
```

---

## 🔧 Required Manual Patches to `deeponto`

The `deeponto` library requires a few manual code changes to fix bugs related to its configuration handling and Windows file path compatibility.

### ✅ PATCH 1: Fix Score Thresholding

A bug prevents the correct loading of mappings based on a score threshold.

* **File:** `.\.venv\Lib\site-packages\deeponto\align\mapping.py`
* **Action:** Go to around line **149** and modify the `if` condition.

**BEFORE:**
```py
if dp.Score >= threshold:
    #...
```

**AFTER:**
```py
if not threshold or dp.Score >= threshold:
    #...
```

### ✅ PATCH 2: Fix File Path Handling for LogMap (Critical for Windows)

The library incorrectly formats file paths when calling the external LogMap `.jar` file on Windows.

* **File:** `.\.venv\Lib\site-packages\deeponto\align\logmap\__init__.py`
* **Action:** Replace the `run_logmap_repair` function with the patched version below. This uses Python's `pathlib` to correctly create file URIs.

```py
# Add this import at the top of the file
import pathlib

# Replace the entire function with this one
def run_logmap_repair(
    src_onto_path: str, tgt_onto_path: str, mapping_file_path: str, output_path: str, max_jvm_memory: str = "10g"
):
    """Run the repair module of LogMap with `java -jar`."""

    # find logmap directory
    logmap_path = os.path.dirname(__file__)

    # obtain absolute paths
    src_onto_path = os.path.abspath(src_onto_path)
    tgt_onto_path = os.path.abspath(tgt_onto_path)
    mapping_file_path = os.path.abspath(mapping_file_path)
    output_path = os.path.abspath(output_path)
    
    # Convert paths to proper file URIs for java
    src_onto_uri = pathlib.Path(src_onto_path).resolve().as_uri()
    tgt_onto_uri = pathlib.Path(tgt_onto_path).resolve().as_uri()

    # run jar command
    print(f"Run the repair module of LogMap from {logmap_path}.")
    repair_command = (
        f"java -Xms500m -Xmx{max_jvm_memory} -DentityExpansionLimit=100000000 -jar {logmap_path}/logmap-matcher-4.0.jar DEBUGGER "
        + f"{src_onto_uri} {tgt_onto_uri} TXT {mapping_file_path}" # Use the new URI variables
        + f" {output_path} false false"
    )
    print(f"The jar command is:\n{repair_command}.")
    run_jar(repair_command)
```

### ✅ PATCH 3: Force BERTMap to Respect Configuration

The BERTMap pipeline ignores the `repair: enabled: false` setting in the config file. We must force it to skip the broken repair step.

* **File:** `.\.venv\Lib\site-packages\deeponto\align\bertmap\pipeline.py`
* **Action:** Find the `__init__` method of the `BERTMapPipeline` class. Near the end of the method (around line 211), comment out the call to `self.mapping_refiner.mapping_repair()`.

**BEFORE:**
```py
# ...
self.mapping_refiner.mapping_extension()  # mapping extension
self.mapping_refiner.mapping_repair()  # mapping repair
# ...
```

**AFTER:**
```py
# ...
self.mapping_refiner.mapping_extension()  # mapping extension
# self.mapping_refiner.mapping_repair()  # mapping repair
# ...
```

---

## 🚀 Execution

After applying all the environment and code patches, you are ready to run the alignment.

1.  **Set the Java environment variable** (as described in Prerequisites).
2.  **Delete any old results:** `rm -rf bertmap_work` to ensure a clean run.
3.  **Run the script** from the `week4` subfolder:

```shell
python bertmap_alignment.py ..\week1\ontology.xml existing_pizza.owl -c bertmap_config.yaml --subs-config bertsubs_config.yaml --work-dir bertmap_work --output bertmap_equivalences.ttl --subs-output bertmap_subsumptions.ttl
```

The script will first run `BERTMap` and save its results to `bertmap_equivalences.ttl`. It will then proceed to run `BERTSubs` and save its results to `bertmap_subsumptions.ttl`.

---

## 🧐 Verifying the Results

The output `.ttl` files contain the discovered alignments. The best way to inspect them is with an ontology editor.

1.  **Open Protégé.**
2.  Open your first source ontology (e.g., `ontology.xml`).
3.  Go to **File -> Open from URI...** and open one of the generated mapping files (e.g., `bertmap_equivalences.ttl`).
4.  Protégé will ask; choose to **"Open in current window (merge)"**.
5.  Now, when you click on a class in the "Entities" tab, you can see the `equivalentClass` or `subClassOf` axioms in the description panel on the right, linking it to the concepts in the second ontology.