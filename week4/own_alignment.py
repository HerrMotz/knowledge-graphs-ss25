"""
Ontology alignment script (Argos-powered, auto-installer)
=======================================================
Aligns two OWL/RDF ontologies at the *schema* level (classes and properties)
and writes the result in **Alignment API RDF format** (as used by AML/LogMap).

Output pattern (minimal):

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

Quick start
-----------
```bash
python own_alignment.py \
    pizza_en.owl http://example.org/pizza_en#
    pizza_de.owl http://example.org/pizza_de#
```
On first run the script downloads the *de→en* model (~50 MB) and proceeds to
compute alignments. Later runs start instantly.
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Iterable, Tuple, Generator

from difflib import SequenceMatcher

from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD

# -----------------------------------------------------------------------------
# Argos‑Translate setup: auto‑download de→en model if missing
# -----------------------------------------------------------------------------
try:
    from argostranslate import package, translate as _at  # type: ignore

    def _ensure_langpair(src: str = "de", dst: str = "en") -> None:
        """Ensure the Argos model *src→dst* is installed (download if needed)."""
        installed_langs = _at.get_installed_languages()
        src_lang = next((l for l in installed_langs if l.code == src), None)
        dst_lang = next((l for l in installed_langs if l.code == dst), None)
        if src_lang and dst_lang and src_lang.get_translation(dst_lang):
            return  # already present

        logging.info("Argos model %s→%s not found – downloading…", src, dst)
        package.update_package_index()
        for pkg in package.get_available_packages():
            if pkg.from_code == src and pkg.to_code == dst:
                model_path = pkg.download()  # ← fixed API call
                package.install_from_path(model_path)
                break
        else:
            raise RuntimeError(f"No Argos model found online for {src}->{dst}")

    _ensure_langpair()
    _AT_LANGS = _at.get_installed_languages()
    _AT_EN_LANG = next((lang for lang in _AT_LANGS if lang.code == "en"), None)
    _ARGOS_OK = _AT_EN_LANG is not None
except Exception as exc:  # pragma: no cover – Argos missing or install failed
    _ARGOS_OK = False
    logging.warning("Argos‑Translate setup failed (%s) – labels will not be translated.", exc)


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

_CAMEL_RE = re.compile(r"(?<!^)(?=[A-Z])")
_SEP_RE = re.compile(r"[_\-\s]+")


def split_identifier(text: str) -> Iterable[str]:
    """Split CamelCase or snake_case identifier into lower‑cased tokens."""
    text = _SEP_RE.sub(" ", text)
    text = _CAMEL_RE.sub(" ", text)
    return [tok.lower() for tok in text.split() if tok]


def _argos_translate_token(tok: str) -> str:
    """Translate *tok* to English via Argos‑Translate (fallback: identity)."""
    if not _ARGOS_OK or tok == "":
        return tok
    try:
        for lang in _AT_LANGS:
            if lang.code == "en":
                continue
            translation = lang.get_translation(_AT_EN_LANG)
            if translation and translation.is_loaded:
                result = translation.translate(tok)
                if result and result.lower() != tok.lower():
                    return result.lower()
        return tok
    except Exception as exc:  # pragma: no cover
        logging.debug("Argos translate failed for '%s': %s", tok, exc)
        return tok


def normalise_label(label: str | None, fallback: str) -> str:
    raw = label or fallback
    tokens = split_identifier(raw)
    return " ".join(_argos_translate_token(t) for t in tokens)


def similarity(a: str, b: str) -> float:  # Jaro‑Winkler via SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()


# -----------------------------------------------------------------------------
# Alignment logic
# -----------------------------------------------------------------------------


def _entities(g: Graph, rdf_type: URIRef) -> Iterable[URIRef]:
    yield from g.subjects(RDF.type, rdf_type)


def _align(
    g1: Graph,
    g2: Graph,
    rdf_type: URIRef,
    threshold: float,
) -> Generator[Tuple[URIRef, URIRef, float], None, None]:
    """Yield (e1, e2, score) for all pairs of *rdf_type* with score >= threshold."""
    # Precompute normalized labels for speed
    labels1 = {
        e1: normalise_label(str(g1.value(e1, RDFS.label)), e1.split("#")[-1])
        for e1 in _entities(g1, rdf_type)
    }
    labels2 = {
        e2: normalise_label(str(g2.value(e2, RDFS.label)), e2.split("#")[-1])
        for e2 in _entities(g2, rdf_type)
    }

    for e1, norm1 in labels1.items():
        for e2, norm2 in labels2.items():
            score = similarity(norm1, norm2)
            if score >= threshold:
                yield e1, e2, score


ALIGN = Namespace("http://knowledgeweb.semanticweb.org/heterogeneity/alignment#")


def build_alignment_api_graph(
    g1: Graph,
    g2: Graph,
    ns1: Namespace,
    ns2: Namespace,
    threshold: float,
) -> Graph:
    """Create an Alignment API RDF graph from two ontologies."""
    out = Graph()
    out.bind("align", ALIGN)
    out.bind("xsd", XSD)
    out.bind("p1", ns1)
    out.bind("p2", ns2)

    root = BNode()
    out.add((root, RDF.type, ALIGN.Alignment))

    # Classes
    for c1, c2, score in _align(g1, g2, OWL.Class, threshold):
        _add_cell(out, root, c1, c2, score)

    # Object + data properties
    for prop_t in (OWL.ObjectProperty, OWL.DatatypeProperty):
        for p1, p2, score in _align(g1, g2, prop_t, threshold):
            _add_cell(out, root, p1, p2, score)

    return out


def _add_cell(g: Graph, root: BNode, e1: URIRef, e2: URIRef, score: float) -> None:
    cell = BNode()
    g.add((root, ALIGN.map, cell))
    g.add((cell, RDF.type, ALIGN.Cell))
    g.add((cell, ALIGN.entity1, e1))
    g.add((cell, ALIGN.entity2, e2))
    g.add((cell, ALIGN.relation, Literal("=")))
    g.add((cell, ALIGN.measure, Literal(score, datatype=XSD.float)))


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description="Ontology alignment script")
    p.add_argument("ontology1", type=Path, help="First ontology (.owl/.ttl)")
    p.add_argument("ns1", help="Namespace IRI of first ontology (ends with # or /)")
    p.add_argument("ontology2", type=Path, help="Second ontology (.owl/.ttl)")
    p.add_argument("ns2", help="Namespace IRI of second ontology (ends with # or /)")
    p.add_argument("-o", "--output", type=Path, default=Path("outputs_reference_ontology/own_alignment_api.ttl"))
    p.add_argument("--threshold", type=float, default=0.87)
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    logging.info("Loading ontologies…")
    g1 = Graph().parse(args.ontology1)
    g2 = Graph().parse(args.ontology2)

    logging.info("Computing alignments (threshold %.2f)…", args.threshold)
    alignment = build_alignment_api_graph(g1, g2, Namespace(args.ns1), Namespace(args.ns2), args.threshold)

    logging.info("Found %d equivalence cells", len(list(alignment.objects(None, ALIGN.map))))
    alignment.serialize(args.output, format="turtle")
    logging.info("Alignment written to %s", args.output)


if __name__ == "__main__":
    main()
