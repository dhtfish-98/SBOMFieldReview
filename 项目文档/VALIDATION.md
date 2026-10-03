# Validation record

Scope: Missing component names, versions, references and dependency graph hints.

Local checks to rerun:

```sh
python -m unittest discover -s tests -v
python cli.py --help
python -m compileall -q review.py cli.py tests
```

Check the exact public GitHub commit and its workflow run separately after publishing. Tests use synthetic input; no production system or external target is exercised. This is not full CycloneDX schema validation, vulnerability detection, provenance verification or CISA conformance certification.

## Current source result (2026-10-02)

- Python 3.14.6: 8/8 unit and CLI integration tests passed.
- Tests include the specific malformed-input, incomplete-review and declaration cases added during the source audit.
- Metadata root and nested components participate in the field/reference review. Services and other CycloneDX structures are outside this component-focused check; this is not complete schema validation.
- Test input is synthetic. No external target, live credential or production cluster is exercised.
- The public commit and its corresponding GitHub workflow must be verified separately after this update.
