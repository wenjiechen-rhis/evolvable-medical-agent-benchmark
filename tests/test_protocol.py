from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from emab.metrics import compute_public_metrics
from emab.receipt import freeze_bundle, verify_receipt
from emab.validation import errors_only, validate_bundle


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "mechanical-conformance"


class ProtocolTests(unittest.TestCase):
    def make_bundle(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        bundle = Path(temporary.name) / "bundle"
        shutil.copytree(FIXTURE, bundle)
        receipt = bundle / "receipt.json"
        if receipt.exists():
            receipt.unlink()
        return temporary, bundle

    def test_fixture_validates(self) -> None:
        issues = validate_bundle(FIXTURE)
        self.assertEqual([], errors_only(issues), [issue.render() for issue in issues])

    def test_freeze_and_verify(self) -> None:
        temporary, bundle = self.make_bundle()
        self.addCleanup(temporary.cleanup)
        freeze_bundle(bundle, bundle / "receipt.json")
        self.assertEqual([], verify_receipt(bundle))

    def test_tamper_is_detected(self) -> None:
        temporary, bundle = self.make_bundle()
        self.addCleanup(temporary.cleanup)
        freeze_bundle(bundle, bundle / "receipt.json")
        with (bundle / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write("\n")
        errors = verify_receipt(bundle)
        self.assertTrue(any("mismatch" in error for error in errors), errors)

    def test_metrics_keep_unknown_official_denominator(self) -> None:
        metrics = compute_public_metrics(FIXTURE)
        self.assertEqual({"numerator": 1, "denominator": 1, "value": 1.0}, metrics["completion"])
        self.assertEqual(0, metrics["official_correctness"]["denominator"])
        self.assertIsNone(metrics["official_correctness"]["value"])
        self.assertEqual(1, metrics["official_label_counts"]["not_evaluated"])

    def test_human_action_before_handoff_is_rejected(self) -> None:
        temporary, bundle = self.make_bundle()
        self.addCleanup(temporary.cleanup)
        events_path = bundle / "events.jsonl"
        lines = events_path.read_text(encoding="utf-8").splitlines()
        event = json.loads(lines[1])
        event["actor_type"] = "human_after_handoff"
        lines[1] = json.dumps(event, separators=(",", ":"))
        events_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        issues = errors_only(validate_bundle(bundle))
        self.assertTrue(any(issue.code == "human_before_handoff" for issue in issues), [issue.render() for issue in issues])


if __name__ == "__main__":
    unittest.main()
