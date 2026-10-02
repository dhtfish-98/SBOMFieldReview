"""Offline completeness prompts for CycloneDX component records."""
from __future__ import annotations
from strict_json import loads


def review_text(text: str) -> list[dict[str, str]]:
    document = loads(text)
    if not isinstance(document, dict) or document.get("bomFormat") != "CycloneDX":
        raise ValueError("expected a CycloneDX JSON object")
    components = document.get("components", [])
    if not isinstance(components, list):
        raise ValueError("components must be an array")
    metadata = document.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")
    stack = [(component, f"components[{index}]") for index, component in reversed(list(enumerate(components)))]
    if "component" in metadata:
        stack.append((metadata["component"], "metadata.component"))
    findings = []
    refs = set()
    while stack:
        component, where = stack.pop()
        if not isinstance(component, dict):
            raise ValueError("component must be an object")
        def add(rule, note):
            findings.append({"rule": rule, "location": where, "note": note})
        for field in ("name", "version"):
            if not isinstance(component.get(field), str) or not component[field].strip():
                add(f"missing-{field}", f"Component {field} is absent")
        ref = component.get("bom-ref")
        if not isinstance(ref, str) or not ref.strip():
            add("missing-reference", "Component has no bom-ref")
        elif ref in refs:
            add("duplicate-reference", "bom-ref is reused")
        else:
            refs.add(ref)
        nested = component.get("components", [])
        if not isinstance(nested, list):
            raise ValueError("nested components must be an array")
        stack.extend((child, f"{where}.components[{index}]") for index, child in reversed(list(enumerate(nested))))
    dependencies = document.get("dependencies")
    if dependencies is None:
        findings.append({"rule": "no-dependency-graph", "location": "root", "note": "Dependency relationships are not present"})
    elif not isinstance(dependencies, list):
        raise ValueError("dependencies must be an array")
    else:
        for index, relation in enumerate(dependencies):
            if not isinstance(relation, dict) or not isinstance(relation.get("ref"), str):
                raise ValueError("dependency relation needs a string ref")
            ref = relation["ref"]
            if ref not in refs:
                findings.append({"rule": "unknown-dependency-ref", "location": f"dependencies[{index}]", "note": "Dependency source is not a collected component"})
            targets = relation.get("dependsOn", [])
            if not isinstance(targets, list) or not all(isinstance(target, str) for target in targets):
                raise ValueError("dependsOn must be a string array")
            for target in targets:
                if target not in refs:
                    findings.append({"rule": "unknown-dependency-target", "location": f"dependencies[{index}]", "note": "Dependency target is not a collected component"})
    return findings
