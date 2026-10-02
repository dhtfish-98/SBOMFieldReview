import json
import plistlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from review import review_text


class RegressionTests(unittest.TestCase):

    def test_nested_components_are_collected(self):
        bom={"bomFormat":"CycloneDX","components":[{"name":"parent","version":"1","bom-ref":"p","components":[{"name":"child","bom-ref":"c"}]}],"dependencies":[{"ref":"p","dependsOn":["c"]}]}
        findings=review_text(json.dumps(bom))
        self.assertEqual([x["rule"] for x in findings],["missing-version"])
        self.assertEqual(findings[0]["location"],"components[0].components[0]")
