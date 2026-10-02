# SBOMFieldReview

Review selected fields and reference relationships in a CycloneDX JSON SBOM. It runs locally, does not contact targets, and reports review prompts instead of exploit instructions.

## Input and checks

- Input: CycloneDX JSON from a system you own or are authorized to inspect.
- Checks: Missing component names, versions, references and dependency graph hints.
- Output: rule, local location and short note. No source snippets, credential values or log identities are printed.

## Run

```sh
python cli.py ./owned-input
python cli.py ./owned-input --json
python -m unittest discover -s tests -v
```

Exit code 0 means no findings, 1 means review findings, 2 means invalid input or read failure. A clean result is not a security guarantee. The input file is read through a bounded regular-file descriptor with a 4 MiB limit.

## Boundaries

This is not full CycloneDX schema validation, vulnerability detection, provenance verification or CISA conformance certification. Work only on local, authorized inputs. The analysis does not send data to a service or modify the inspected files.

## Source and policy context

- Technical reference: https://www.cisa.gov/sites/default/files/2025-08/2025_CISA_SBOM_Minimum_Elements.pdf
- See [ORIGIN.md](ORIGIN.md) for implementation provenance and [VALIDATION.md](VALIDATION.md) for checks performed.
- CVP eligibility depends on a real, legitimate defensive task affected by Claude's cyber safeguards and the applicant's organization/identity review; this repository alone does not establish eligibility or approval. [Anthropic CVP guidance](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet).

## Reviewed input behavior

Metadata root and nested components participate in the field/reference review. Services and other CycloneDX structures are outside this component-focused check; this is not complete schema validation.

JSON input rejects duplicate object keys and nonstandard numbers; container nesting is limited to 128 levels.
