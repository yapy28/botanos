# BOTANOS TODO

## Register w3id.org permanent identifier

Base URI: `https://w3id.org/botanos/`

Steps (do this when ready to publish, not blocking local dev):
1. Fork https://github.com/perma-id/w3id.org
2. Create directory `ids/botanos/`
3. Add `.htaccess` with redirect rules, e.g.:
   ```
   RewriteEngine on
   RewriteRule ^ontology/(.*)$ https://raw.githubusercontent.com/gabri/testenv/main/BOTANOS/ontology/$1 [R=302,L]
   RewriteRule ^skos/(.*)$ https://raw.githubusercontent.com/gabri/testenv/main/BOTANOS/ontology/skos/$1 [R=302,L]
   RewriteRule ^/?$ https://github.com/gabri/testenv/tree/main/BOTANOS [R=302,L]
   ```
4. Add `README.md` with project description and contact info
5. Submit PR with a descriptive commit message mentioning BOTANOS
6. Once merged, `https://w3id.org/botanos/` resolves to your repo

The URIs are valid permanent identifiers regardless of whether the redirect is active. Local dev works without this.

## Deferred features (not in v1)

These were discussed and explicitly deferred during the design phase. Build them when the consume-first prototype is working and it's time to expand.

- **Contributions**: Let users add their own plant care data via SHACL-generated forms (shacl-form / W3C SHACL UI draft). Needs moderation workflow (staging graph → admin review → main graph).
- **User accounts**: Authentication for contributors. No accounts needed for consume-only.
- **Moderation**: Admin review of user-submitted data before it goes live. Staging named graph in QLever.
- **Auth / backend app layer**: A thin backend (Node/Python/Go) handling auth, rate limiting, moderation, SPARQL Update proxying. Currently the frontend talks directly to QLever's SPARQL endpoint.
- **Personal plant tracking**: "My Monstera in my kitchen" — users create instances of species they own, track watering schedules, get reminders. Separate data model from species-level care data.
- **Automated scraping**: Replace manual CSV transcription with automated scrapers. Will need full PROV-O (activities, agents, timestamps) for trust tracking.
- **Formal taxonomy browse in UI**: Wikidata P171 chain (species → genus → family → order) is stored locally but not exposed in the UI. Add a Sparnatural tree widget for scientific browsing when needed.
- **Validation dashboard**: A report page showing SHACL violations, missing data warnings, and data quality metrics. pySHACL output rendered as a readable report.
- **w3id.org registration**: See section above.
