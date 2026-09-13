# BOTANOS

Plant care database built on RDF, SPARQL, and SKOS. Filter plants by temperature, humidity, light, watering type, and more. Built with QLever, Morph-KGC, Sparnatural-form, and Wikidata.

## Quick Start

### Prerequisites

```bash
# Create a Python 3.10+ virtual environment
/opt/homebrew/bin/python3.13 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install morph-kgc pyshacl rdflib qlever

# Start Docker (for QLever)
open -a Docker
```

### Build and Run

```bash
# 1. Stop and remove the old QLever container (if running)
docker stop qlever.server.botanos && docker rm qlever.server.botanos

# 2. Clean up old index files
rm -f qlever/botanos.* qlever/qlever-botanos.*

# 3. Build RDF from CSV (expands multi-valued columns, runs Morph-KGC, validates with SHACL, outputs N-Quads)
python3 scripts/build_rdf.py

# 4. Build QLever index and start the SPARQL server (port 7019)
./scripts/load.sh

# 5. In a separate terminal, serve the frontend (port 8000)
cd /Users/gabri/git/testenv/BOTANOS
python3 -m http.server 8000
```

### Open the site

```
http://localhost:8000/src/index.html
```

- SPARQL endpoint: `http://localhost:7019`
- QLever UI: `http://localhost:8176`

## Project Structure

```
BOTANOS/
├── raw_plants.md              # Source articles for plant care data
├── data/
│   ├── csv/plants.csv         # Manual CSV — edit this to add plants
│   ├── rml/plants.yarrrml.yml # YARRRML mapping (CSV → RDF)
│   └── rdf/plants.nq          # Generated N-Quads (don't edit)
├── ontology/
│   ├── botanos.ttl            # OWL ontology (classes, properties)
│   ├── shacl/botanos-shapes.ttl # SHACL shapes (Sparnatural config + validation)
│   └── skos/                  # 7 SKOS ConceptScheme files
├── src/
│   ├── index.html             # Filter page (Sparnatural-form + cards)
│   ├── species.html           # Species detail page
│   └── assets/
│       ├── form-query.json    # Sparnatural query structure
│       ├── form-specification.json # Form field bindings
│       ├── sparnatural-form.js # Local copy of Sparnatural-form JS
│       └── sparnatural-form.css # Local copy of Sparnatural-form CSS
├── scripts/
│   ├── build_rdf.py           # CSV → Morph-KGC → SHACL → N-Quads
│   └── load.sh                # QLever index + start server
├── qlever/                    # QLever index files (generated, don't edit)
├── Notes/TO_DO.md             # Deferred features + w3id registration
├── morph_kgc.ini              # Morph-KGC config
├── Qleverfile                 # QLever config
└── docker-compose.yml         # Alternative Docker setup
```

## Adding Plants

1. Add plant care data to `raw_plants.md`
2. Transcribe into `data/csv/plants.csv` (one row per plant per source)
3. Use semicolons for multi-valued fields: `Indoor;Outdoor`, `Vine;Tropical`
4. Rebuild and reload:
   ```bash
   docker stop qlever.server.botanos && docker rm qlever.server.botanos
   rm -f qlever/botanos.* qlever/qlever-botanos.*
   python3 scripts/build_rdf.py
   ./scripts/load.sh
   ```

## CSV Columns

| Column | Type | Example | Notes |
|---|---|---|---|
| wikidata_id | string | Q157417 | Wikidata Q-ID |
| scientific_name | string | Monstera deliciosa | Binomial name |
| common_name | string | Swiss Cheese Plant | Display name |
| indoor_outdoor | SKOS (multi) | Indoor;Outdoor | Semicolon-separated |
| temp_min | decimal | 18 | Min temp in Celsius |
| temp_max | decimal | 29 | Max temp in Celsius |
| soil_ph_min | decimal | 5.5 | Min soil pH |
| soil_ph_max | decimal | 7.0 | Max soil pH |
| soil_humidity | SKOS | ModerateSoil | DrySoil, ModerateSoil, MoistSoil, WetSoil |
| air_humidity | SKOS | HighHumidity | LowHumidity, MediumHumidity, HighHumidity, VeryHighHumidity |
| light | SKOS | PartialShade | FullSun, BrightIndirect, PartialShade, FullShade |
| watering_type | SKOS | Pour | Drip, Pour, Spray, BottomWatering, Soak |
| watering_freq | SKOS | Regular | Infrequent, Regular, Frequent |
| mature_height_min | decimal | 91 | Min height in cm |
| mature_height_max | decimal | 457 | Max height in cm |
| pot_size_min | decimal | 15 | Min pot diameter in cm |
| pot_size_max | decimal | 30 | Max pot diameter in cm |
| plant_category | SKOS (multi) | Vine;Tropical | Semicolon-separated |
| toxic_to | SKOS (multi) | Human;Dog;Cat | Semicolon-separated; NonToxic = safe for all |
| source_url | URL | https://... | Source article |
| source_name | string | The Spruce | Source name |

## What Requires Rebuilding

Not every change requires a full rebuild. Here's what each type of change needs:

| Change | What to do |
|---|---|
| Edit `data/csv/plants.csv` (add plants, change values, fix Q-IDs) | Full rebuild: `python3 scripts/build_rdf.py` then QLever reload |
| Edit `data/rml/plants.yarrrml.yml` (mapping rules) | Full rebuild + QLever reload |
| Edit `morph_kgc.ini` | Full rebuild + QLever reload |
| Edit `ontology/botanos.ttl` or `ontology/skos/*.ttl` | Full rebuild + QLever reload (baked into N-Quads at build time) |
| Edit `ontology/shacl/botanos-shapes.ttl` (widgets, labels, enableOptional) | Just refresh the browser (loaded client-side by Sparnatural-form) |
| Edit `src/index.html`, `src/species.html` | Just refresh the browser |
| Edit `src/assets/form-query.json` or `form-specification.json` | Just refresh the browser |

**Full rebuild commands** (when needed):

```bash
docker stop qlever.server.botanos && docker rm qlever.server.botanos
rm -f qlever/botanos.* qlever/qlever-botanos.*
python3 scripts/build_rdf.py
./scripts/load.sh
```
