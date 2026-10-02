import json
import unittest
from review import review_text


class SBOMTests(unittest.TestCase):
    def test_complete_small_bom(self):
        bom = {"bomFormat": "CycloneDX", "components": [{"name": "owned-lib", "version": "1.0", "bom-ref": "lib-1"}], "dependencies": [{"ref": "lib-1", "dependsOn": []}]}
        self.assertEqual(review_text(json.dumps(bom)), [])

    def test_incomplete_and_duplicate_records(self):
        bom = {"bomFormat": "CycloneDX", "components": [{"name": "a", "bom-ref": "same"}, {"version": "2", "bom-ref": "same"}], "dependencies": [{"ref": "other"}]}
        rules = {item["rule"] for item in review_text(json.dumps(bom))}
        self.assertEqual(rules, {"missing-name", "missing-version", "duplicate-reference", "unknown-dependency-ref"})

    def test_bad_schema(self):
        for value in ("{}", '{"bomFormat":"CycloneDX","components":{}}', '{"bomFormat":"CycloneDX","components":[],"dependencies":[{"ref":{}}]}', "invalid"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                review_text(value)

    def test_unknown_target_and_metadata_root(self):
        bom = {"bomFormat": "CycloneDX", "metadata": {"component": {"bom-ref": "root"}}, "components": [{"name": "x", "version": "1", "bom-ref": "x"}], "dependencies": [{"ref": "root", "dependsOn": ["x", "unknown"]}]}
        self.assertEqual([item["rule"] for item in review_text(json.dumps(bom))], ["unknown-dependency-target"])
