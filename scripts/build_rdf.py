#!/usr/bin/env python3
"""
BOTANOS build pipeline: CSV -> Morph-KGC CLI -> RDFLib -> pySHACL -> N-Quads

Usage:
    python3 scripts/build_rdf.py

Requirements:
    pip install morph-kgc pyshacl rdflib
"""

import sys
import os
import subprocess
from rdflib import Graph, Dataset, Literal, URIRef
from rdflib.namespace import XSD
import pyshacl

# Paths (relative to project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "morph_kgc.ini")
SHACL_PATH = os.path.join(PROJECT_ROOT, "ontology", "shacl", "botanos-shapes.ttl")
ONTOLOGY_PATHS = [
    os.path.join(PROJECT_ROOT, "ontology", "botanos.ttl"),
    os.path.join(PROJECT_ROOT, "ontology", "skos", "indoor-outdoor.ttl"),
    os.path.join(PROJECT_ROOT, "ontology", "skos", "soil-humidity.ttl"),
    os.path.join(PROJECT_ROOT, "ontology", "skos", "air-humidity.ttl"),
    os.path.join(PROJECT_ROOT, "ontology", "skos", "light.ttl"),
    os.path.join(PROJECT_ROOT, "ontology", "skos", "watering-type.ttl"),
    os.path.join(PROJECT_ROOT, "ontology", "skos", "watering-frequency.ttl"),
    os.path.join(PROJECT_ROOT, "ontology", "skos", "plant-categories.ttl"),
    os.path.join(PROJECT_ROOT, "ontology", "skos", "toxicity.ttl"),
]
DATA_NQ_PATH = os.path.join(PROJECT_ROOT, "data", "rdf", "plants-data.nq")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "rdf", "plants.nq")

BOTANOS_BASE = "https://w3id.org/botanos/"

def botanos_prop(name):
    return URIRef(BOTANOS_BASE + name)

DECIMAL_PROPS = {
    botanos_prop("tempMin"), botanos_prop("tempMax"),
    botanos_prop("soilPhMin"), botanos_prop("soilPhMax"),
    botanos_prop("matureHeightMin"), botanos_prop("matureHeightMax"),
    botanos_prop("potSizeMin"), botanos_prop("potSizeMax"),
}


def main():
    print("=== BOTANOS Build Pipeline ===")

    # Step 0: Expand semicolon-separated multi-valued CSV columns into multiple rows
    print("\n[0/4] Expanding multi-valued CSV columns...")
    import csv
    CSV_PATH = os.path.join(PROJECT_ROOT, "data", "csv", "plants.csv")
    CSV_EXPANDED_PATH = os.path.join(PROJECT_ROOT, "data", "csv", "plants-expanded.csv")
    MULTI_VAL_COLS = ["indoor_outdoor", "plant_category", "toxic_to"]
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    expanded_rows = []
    for row in rows:
        # Find columns that have semicolons
        splits = {col: row[col].split(";") for col in MULTI_VAL_COLS if ";" in row.get(col, "")}
        if not splits:
            expanded_rows.append(row)
            continue
        # Generate cartesian product of all split values
        import itertools
        keys = list(splits.keys())
        for combo in itertools.product(*[splits[k] for k in keys]):
            new_row = dict(row)
            for k, v in zip(keys, combo):
                new_row[k] = v.strip()
            expanded_rows.append(new_row)
    with open(CSV_EXPANDED_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(expanded_rows)
    print(f"  {len(rows)} rows -> {len(expanded_rows)} expanded rows")

    # Step 1: Materialize RDF from expanded CSV using Morph-KGC CLI (preserves named graphs)
    print("\n[1/4] Materializing RDF from CSV via Morph-KGC CLI...")
    os.makedirs(os.path.dirname(DATA_NQ_PATH), exist_ok=True)
    result = subprocess.run(
        [sys.executable, "-m", "morph_kgc", CONFIG_PATH],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        print(f"  ERROR during materialization:\n{result.stderr}")
        sys.exit(1)
    for line in result.stderr.strip().split('\n')[-3:]:
        print(f"  {line}")
    print(f"  Output: {DATA_NQ_PATH}")

    # Step 2: Load the N-Quads into a Dataset and fix datatypes
    print("\n[2/4] Loading N-Quads and fixing xsd:decimal datatypes...")
    dataset = Dataset()
    dataset.parse(DATA_NQ_PATH, format="nquads")

    fixed = 0
    for graph in list(dataset.graphs()):
        for s, p, o in list(graph):
            if p in DECIMAL_PROPS and isinstance(o, Literal) and o.datatype is None:
                try:
                    float(o.value)
                    graph.remove((s, p, o))
                    graph.add((s, p, Literal(o.value, datatype=XSD.decimal)))
                    fixed += 1
                except (ValueError, TypeError):
                    pass
    print(f"  Fixed {fixed} numeric literals with xsd:decimal")

    # Step 3: Validate against SHACL
    print("\n[3/4] Validating RDF against SHACL shapes...")
    ontology_graph = Graph()
    for path in ONTOLOGY_PATHS:
        ontology_graph.parse(path, format="turtle")
    print(f"  Loaded {len(ONTOLOGY_PATHS)} ontology files")

    shapes_graph = Graph()
    shapes_graph.parse(SHACL_PATH, format="turtle")
    print(f"  Loaded SHACL shapes")

    # Build a flat validation graph (merge all named graphs + ontology)
    validation_graph = Graph()
    for graph in dataset.graphs():
        for triple in graph:
            validation_graph.add(triple)
    for triple in ontology_graph:
        validation_graph.add(triple)

    conforms, results_graph, results_text = pyshacl.validate(
        validation_graph,
        shapes_graph=shapes_graph,
        ont_graph=ontology_graph,
        inference="rdfs",
    )

    if conforms:
        print("  SHACL validation PASSED")
    else:
        print("  SHACL validation FAILED:")
        print(results_text)
        print("  Continuing anyway (non-blocking for now)...")

    # Step 4: Add ontology to default graph and serialize final N-Quads
    print("\n[4/4] Merging ontology + serializing final N-Quads...")
    default_graph = dataset.graph()
    for triple in ontology_graph:
        default_graph.add(triple)

    dataset.serialize(destination=OUTPUT_PATH, format="nquads")
    print(f"  Written to {OUTPUT_PATH}")

    # Summary
    print("\n=== Summary ===")
    total = 0
    for ctx in dataset.graphs():
        ctx_id = str(ctx.identifier) if ctx.identifier else "default"
        count = len(list(ctx))
        total += count
        if count > 0:
            print(f"  Graph <{ctx_id}>: {count} triples")
    print(f"  Total: {total} triples")

    print("\nDone. Next step: ./scripts/load.sh to load into QLever.")


if __name__ == "__main__":
    main()
