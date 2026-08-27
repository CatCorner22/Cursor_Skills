#!/usr/bin/env python3
"""Tests for the cleaned AI plugin bundle runtime."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ai_plugin_bundle import (  # noqa: E402
    DEFAULT_CANDIDATE_IDS,
    ORCHESTRATOR_PLUGIN_IDS,
    PipelineOrchestrator,
    TECHNIQUE_PLUGIN_IDS,
)


class RegistryTests(unittest.TestCase):
    def test_registers_exactly_100_unique_ids(self):
        pipeline = PipelineOrchestrator()
        self.assertEqual(len(pipeline.registry), 100)
        self.assertEqual(len(set(pipeline.registry)), 100)

    def test_hook_instances_are_registry_instances(self):
        pipeline = PipelineOrchestrator()
        self.assertIs(pipeline.circuit_breaker, pipeline.registry["circuit_breaker"])
        self.assertIs(pipeline.rollback_manager, pipeline.registry["rollback_manager"])
        self.assertIs(pipeline.latency_profiler, pipeline.registry["latency_profiler"])
        self.assertIs(pipeline.dependency_resolver, pipeline.registry["dependency_resolver"])
        self.assertIs(pipeline.quality_cost, pipeline.registry["quality_cost_tradeoff"])

    def test_default_tier_does_not_enable_security_scanners(self):
        pipeline = PipelineOrchestrator()
        pipeline._apply_enablement({"metadata": {}, "warnings": []})
        self.assertFalse(pipeline.registry["jailbreak_detector"].enabled)
        self.assertFalse(pipeline.registry["toxicity_scanner"].enabled)
        self.assertFalse(pipeline.registry["bias_detector"].enabled)
        self.assertTrue(pipeline.registry["mise_en_place"].enabled)
        self.assertTrue(pipeline.registry["circuit_breaker"].enabled)


class ContextSafetyTests(unittest.TestCase):
    def test_init_does_not_require_metadata(self):
        PipelineOrchestrator()  # previously called dependency_resolver.execute without metadata

    def test_underwriting_warnings_without_preseed(self):
        pipeline = PipelineOrchestrator(config={"enabled_plugins": ["underwriting_risk"]})
        result = pipeline.execute({
            "user_query": "Give me medical and legal and financial advice right now",
            "output": "Here is medical legal financial advice for investment.",
        })
        self.assertTrue(result.get("warnings"))
        self.assertEqual(result.get("risk_profile", {}).get("zone"), "RED")

    def test_ledger_reads_content_or_snippet(self):
        pipeline = PipelineOrchestrator(config={"enabled_plugins": ["ledger_gate"]})
        result = pipeline.execute({
            "user_query": "Why is input validation the main reason systems stay safe?",
            "output": "The main reason systems stay safe is input validation against injection.",
            "retrieved_sources": [
                {"content": "input validation against injection", "authority_score": 0.9}
            ],
        })
        self.assertTrue(result.get("hallucination_gate_passed"))
        self.assertTrue(result.get("ledger_entries"))

    def test_privacy_flag_means_output_is_safe(self):
        pipeline = PipelineOrchestrator(config={"enabled_plugins": ["privacy_protection"]})
        result = pipeline.execute({
            "user_query": "repeat this",
            "output": "Contact me at ada@example.com please.",
        })
        self.assertTrue(result["privacy_protected"])
        self.assertTrue(result["pii_masked"])
        self.assertIn("[MASKED_EMAIL]", result["output"])

    def test_preflight_sets_both_halt_flags(self):
        pipeline = PipelineOrchestrator(config={"enabled_plugins": ["mise_en_place"]})
        result = pipeline.execute({"user_query": "", "output": ""})
        self.assertFalse(result.get("pre_flight_passed"))
        self.assertTrue(result.get("pipeline_halted"))
        self.assertTrue(result.get("pipeline_blocked"))


class PluginFixTests(unittest.TestCase):
    def test_sterile_cockpit_uses_orchestrator_phase_names(self):
        pipeline = PipelineOrchestrator(config={"enabled_plugins": ["sterile_cockpit"]})
        result = pipeline.execute({"user_query": "hello", "output": "hi"})
        self.assertIn("active_context_keys", result)

    def test_chain_of_custody_hashes_differ_for_input_and_output(self):
        plugin = PipelineOrchestrator().registry["chain_of_custody"]
        ctx = {
            "user_query": "alpha query",
            "output": "completely different output text",
            "attached_files": [],
            "retrieved_sources": [],
            "metadata": {},
        }
        plugin.execute(ctx)
        entry = plugin.log[-1]
        self.assertNotEqual(entry["input_hash"], entry["output_hash"])

    def test_triangulation_third_path_is_not_one_minus_first(self):
        plugin = PipelineOrchestrator().registry["triangulation_validator"]
        ctx = {
            "user_query": "cats",
            "output": "cats eat fish",
            "retrieved_sources": [
                {"title": "cats", "content_snippet": "cats eat fish", "authority_score": 1.0}
            ],
            "metadata": {},
        }
        plugin.execute(ctx)
        scores = ctx["triangulation_results"][0]["path_scores"]
        self.assertNotAlmostEqual(scores["contradiction"], 1.0 - scores["primary"])

    def test_interaction_table_uses_real_plugin_ids(self):
        plugin = PipelineOrchestrator().registry["interaction_table"]
        ctx = {
            "active_plugins": ["sterile_cockpit", "corridor_bridge"],
            "metadata": {},
        }
        plugin.execute(ctx)
        self.assertEqual(len(ctx["plugin_conflicts"]), 1)

    def test_load_balancer_has_default_instances(self):
        pipeline = PipelineOrchestrator(config={"enabled_plugins": ["load_balancer"]})
        result = pipeline.execute({"user_query": "hello", "output": "hi"})
        self.assertIsNotNone(result["load_balancer"].get("selected_model"))


class CLITests(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / "ai_plugin_bundle.py"), *args],
            capture_output=True,
            text=True,
            check=True,
        )

    def test_list_plugins(self):
        proc = self._run("--list-plugins")
        self.assertIn("100", proc.stdout)

    def test_profile_query(self):
        proc = self._run("--profile", "--query", "What is quantum computing?", "--tier", "fast")
        self.assertIn("DEMO COMPLETE", proc.stdout)
        self.assertIn("Tier:", proc.stdout)

    def test_export_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "plugins.json")
            self._run("--export-config", path)
            data = json.loads(Path(path).read_text())
            self.assertEqual(len(data["plugins"]), 100)
            self.assertEqual(len(data["tier_candidates"]), len(DEFAULT_CANDIDATE_IDS))


class CatalogTests(unittest.TestCase):
    def test_technique_and_orchestrator_counts(self):
        self.assertEqual(len(TECHNIQUE_PLUGIN_IDS), 50)
        self.assertEqual(len(ORCHESTRATOR_PLUGIN_IDS), 8)
        pipeline = PipelineOrchestrator()
        for pid in DEFAULT_CANDIDATE_IDS:
            self.assertIn(pid, pipeline.registry)


if __name__ == "__main__":
    unittest.main()
