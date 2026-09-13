# BOTANOS TODO

## Register w3id.org permanent identifier

Base URI: `https://w3id.org/botanos/`

PR submitted: https://github.com/perma-id/w3id.org/pull/6687

Current `.htaccess` (in `ids/botanos/.htaccess`):
```
RewriteEngine on
RewriteRule ^ontology/(.*)$ https://raw.githubusercontent.com/yapy28/botanos/main/ontology/$1 [R=302,L]
RewriteRule ^skos/(.*)$ https://raw.githubusercontent.com/yapy28/botanos/main/ontology/skos/$1 [R=302,L]
RewriteRule ^/?$ https://github.com/yapy28/botanos [R=302,L]
```

Status: PR submitted, awaiting merge. URIs are valid regardless.

### Enhancement: content negotiation

Current setup is simple file redirects (302). Consider upgrading to content-negotiated redirects like OMARO (see PR #6681 on w3id.org). This would serve the right format based on the Accept header:

- `Accept: text/turtle` -> `.ttl` file
- `Accept: application/ld+json` -> `.jsonld` file
- `Accept: application/rdf+xml` -> `.rdf` file
- No Accept header (browser) -> HTML landing page

This requires generating JSON-LD and RDF/XML serializations of the ontology and SKOS files, and updating the `.htaccess` with `RewriteCond %{HTTP_ACCEPT}` rules.

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
- **w3id.org content negotiation**: See enhancement section above.
