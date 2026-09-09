# BIRAC BIG connector

This connector reads BIRAC's Biotechnology Ignition Grant awardee PDFs. The authoritative
listing page is `https://birac.nic.in/big.php`; task 008 deliberately does not fetch it.
`discover()` returns only the explicit cohort artifact URLs recorded in `config/sources.yaml`.

The parser supports the committed BIG-21 and BIG-24 fixtures. It uses PDF table geometry to
handle wrapped references, names and scores, normalises category-heading punctuation, and
emits one typed signal per awardee. Applicant classification is conservative: legal suffixes
identify companies, honorifics and a restricted personal-name shape identify people, and
everything else is routed as ambiguous. The reference-number year is represented as 1 January
with explicit year precision in payload; the artifact URL timestamp is retained separately as
`list_published_at`.

If BIRAC redesigns the tables, changes the category headings, adds a partner prefix, or stops
embedding Unix timestamps in artifact filenames, the golden and invariant tests should fail.
Add a real fixture for each new layout before changing the parser. Live listing-page discovery
and its provenance are deferred to task 010.
