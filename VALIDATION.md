# Validation record

Scope: Missing component names, versions, references and dependency graph hints.

Local checks to rerun:

```sh
python -m unittest discover -s tests -v
python cli.py --help
python -m compileall -q review.py cli.py tests
```

Check the exact public GitHub commit and its workflow run separately after publishing. Tests use synthetic input; no production system or external target is exercised. This is not full CycloneDX schema validation, vulnerability detection, provenance verification or CISA conformance certification.

## Observed local result (2026-10-02)

- Python 3.14.6: 5/5 unit and CLI integration tests passed.
- Analyzer and CLI compiled; CLI help rendered.
- CLI ran with a synthetic finding and JSON output; invalid path returned exit code 2.
- The source and README were reviewed for local-only defensive scope and stated limitations.
- GitHub workflow result must be checked against the exact published commit.
