"""Offline completeness prompts for CycloneDX JSON component records."""

from __future__ import annotations
import json


def review_text(text: str) -> list[dict[str, str]]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid SBOM JSON") from exc
    if not isinstance(document, dict) or document.get("bomFormat") != "CycloneDX":
        raise ValueError("expected a CycloneDX JSON object")
    components = document.get("components")
    if not isinstance(components, list):
        raise ValueError("components must be an array")
    findings = []
    refs = set()
    metadata = document.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("component"), dict):
        root_ref = metadata["component"].get("bom-ref")
        if isinstance(root_ref, str):
            refs.add(root_ref)
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            raise ValueError("component must be an object")
        where = f"components[{index}]"
        def add(rule, note):
            findings.append({"rule": rule, "location": where, "note": note})
        if not isinstance(component.get("name"), str) or not component["name"].strip():
            add("missing-name", "Component name is absent")
        if not isinstance(component.get("version"), str) or not component["version"].strip():
            add("missing-version", "Component version is absent")
        ref = component.get("bom-ref")
        if not isinstance(ref, str) or not ref:
            add("missing-reference", "Component has no bom-ref")
        elif ref in refs:
            add("duplicate-reference", "bom-ref is reused")
        else:
            refs.add(ref)
    dependencies = document.get("dependencies")
    if dependencies is None:
        findings.append({"rule": "no-dependency-graph", "location": "root", "note": "Dependency relationships are not present"})
    elif not isinstance(dependencies, list):
        raise ValueError("dependencies must be an array")
    else:
        for index, relation in enumerate(dependencies):
            if not isinstance(relation, dict):
                raise ValueError("dependency relation must be an object")
            ref = relation.get("ref")
            if not isinstance(ref, str):
                raise ValueError("dependency ref must be a string")
            if ref not in refs:
                findings.append({"rule": "unknown-dependency-ref", "location": f"dependencies[{index}]", "note": "Dependency source is not in components"})
            targets = relation.get("dependsOn", [])
            if not isinstance(targets, list) or not all(isinstance(target, str) for target in targets):
                raise ValueError("dependsOn must be a string array")
            for target in targets:
                if target not in refs:
                    findings.append({"rule": "unknown-dependency-target", "location": f"dependencies[{index}]", "note": "Dependency target is not in components"})
    return findings
