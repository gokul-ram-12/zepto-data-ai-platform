#!/usr/bin/env python3
"""Automated acceptance checks for the Zepto Data & AI Platform.

Run artifact checks with:
    python tests/integration_test.py

Run the expensive end-to-end generators first with:
    python tests/integration_test.py --run-pipelines
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)


class ZeptoAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = ROOT
        cls.data_dir = ROOT / "data_pipeline"
        cls.analytics_dir = ROOT / "analytics"
        cls.support_dir = ROOT / "support_assistant"

    def test_repository_structure_and_documentation(self) -> None:
        for relative in ["README.md", "requirements.txt", "data_pipeline", "analytics", "support_assistant", "docker-compose.yml"]:
            self.assertTrue((ROOT / relative).exists(), relative)
        for relative in ["data_pipeline/README.md", "analytics/README.md", "support_assistant/README.md"]:
            self.assertTrue((ROOT / relative).read_text(encoding="utf-8").strip())
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for required in ["data_pipeline", "analytics", "support_assistant", "requirements.txt", "docker compose"]:
            self.assertIn(required, root_readme.lower())

    def test_data_pipeline_database_and_query_outputs(self) -> None:
        db_path = self.data_dir / "artifacts" / "books.db"
        output_path = self.data_dir / "artifacts" / "query_results.md"
        self.assertTrue(db_path.exists())
        self.assertTrue(output_path.exists())
        with sqlite3.connect(db_path) as conn:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertTrue({"categories", "books"}.issubset(tables))
            count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            self.assertGreaterEqual(count, 60)
            columns = {row[1] for row in conn.execute("PRAGMA table_info(books)")}
            self.assertTrue({"price_gbp", "price_inr", "rating", "in_stock", "category_id"}.issubset(columns))
            bad_rate = conn.execute("SELECT COUNT(*) FROM books WHERE ABS(price_inr - price_gbp * 105.50) > 0.011").fetchone()[0]
            self.assertEqual(bad_rate, 0)
            invalid_rating = conn.execute("SELECT COUNT(*) FROM books WHERE rating NOT BETWEEN 1 AND 5").fetchone()[0]
            self.assertEqual(invalid_rating, 0)
            orphan_count = conn.execute("SELECT COUNT(*) FROM books b LEFT JOIN categories c ON b.category_id=c.category_id WHERE c.category_id IS NULL").fetchone()[0]
            self.assertEqual(orphan_count, 0)
        query_text = output_path.read_text(encoding="utf-8")
        for marker in ["1_select_where", "2_distinct", "3_between", "4_in", "5_join", "pd.read_sql", "pd.merge", "Equivalent: **True**"]:
            self.assertIn(marker, query_text)
        self.assertGreaterEqual(query_text.count("```sql"), 5)

    def test_analytics_dataset_reports_charts_and_model(self) -> None:
        csv_path = self.analytics_dir / "titanic.csv"
        df = pd.read_csv(csv_path)
        self.assertGreaterEqual(len(df), 800)
        required = {"survived", "pclass", "age", "sibsp", "parch", "fare", "sex", "embarked"}
        self.assertTrue(required.issubset(df.columns))
        eda_report = (self.analytics_dir / "artifacts" / "eda_report.md").read_text(encoding="utf-8")
        model_report = (self.analytics_dir / "artifacts" / "model_report.md").read_text(encoding="utf-8")
        profile = (self.analytics_dir / "artifacts" / "profile.txt").read_text(encoding="utf-8")
        for marker in ["IQR outlier counts", "Fare mean", "Correlation interpretation", "Boolean-mask checks", "Chart interpretations", "Survival by sex and class chart", "Age distribution by class and outcome chart", "Age, fare, sex, and survival chart", "Survival by embarkation and class chart"]:
            self.assertIn(marker, eda_report)
        for marker in ["Logistic Regression", "Decision Tree", "Random Forest", "Class balance", "not_survived:", "survived:", "Grid search", "OOB score", "MAE", "RMSE", "Adjusted_R2", "Final classifier recommendation"]:
            self.assertIn(marker, model_report)
        for marker in ["INFO", "shape=", "DESCRIBE", "MISSING_PERCENTAGES"]:
            self.assertIn(marker, profile)
        charts = ["age_hist.png", "age_box.png", "fare_hist.png", "fare_box.png", "correlation_heatmap.png", "story_bar.png", "story_age_box.png", "story_scatter.png", "story_point.png", "decision_tree.png", "roc_curves.png", "fare_residuals.png"]
        for chart in charts:
            self.assertTrue((self.analytics_dir / "artifacts" / chart).exists(), chart)
        pipeline = joblib.load(self.analytics_dir / "artifacts" / "best_pipeline.joblib")
        predictions = pipeline.predict(df[["pclass", "sex", "age", "sibsp", "parch", "fare", "embarked"]].head(3))
        self.assertEqual(len(predictions), 3)

    def test_support_corpus_graph_prompt_and_api(self) -> None:
        docs = sorted((self.support_dir / "docs").glob("doc_*.txt"))
        self.assertEqual(len(docs), 8)
        self.assertTrue(all(path.read_text(encoding="utf-8").strip() for path in docs))
        source = (self.support_dir / "main.py").read_text(encoding="utf-8")
        for marker in ["PROMPT_TEMPLATE", "Role:", "Context:", "Task:", "Format:", "Length:", "Negative constraint", "Few-shot example", "hnsw:space", "cosine", "StateGraph", "classify_intent", "retrieve_and_answer", "direct_answer", "generate_real_answer", "Corrective instruction", "@app.post(\"/ask\""]:
            self.assertIn(marker, source)
        os.environ["MOCK_LLM"] = "1"
        from support_assistant.main import AskRequest, RETRIEVER, ask, generate_real_answer
        if RETRIEVER.collection is not None:
            self.assertEqual((RETRIEVER.collection.metadata or {}).get("hnsw:space"), "cosine")
        policy = ask(AskRequest(query="What is the delivery fee below INR 149?"))
        general = ask(AskRequest(query="What is the weather today?"))
        self.assertIn("Based on the retrieved context:", policy.answer)
        self.assertTrue(policy.sources)
        self.assertEqual(policy.confidence, 1.0)
        self.assertEqual(general.sources, [])
        self.assertEqual(general.confidence, 1.0)
        self.assertIn("only answer questions about Zepto policies", general.answer)
        attempts = []
        def invalid_then_valid(prompt: str) -> str:
            attempts.append(prompt)
            return "not-json" if len(attempts) < 3 else '{"answer":"ok","sources":[],"confidence":0.5}'
        retried = generate_real_answer("test prompt", call_model=invalid_then_valid)
        self.assertEqual(len(attempts), 3)
        self.assertEqual(retried.answer, "ok")
        self.assertEqual(retried.confidence, 0.5)

    def test_git_workflow_is_preserved(self) -> None:
        graph = run(["git", "log", "--graph", "--oneline", "--all"]).stdout
        self.assertIn("Merge verified artifacts feature", graph)
        self.assertIn("Include generated analytics artifacts", graph)
        self.assertIn("Document end-to-end verification", graph)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-pipelines", action="store_true", help="Regenerate all module artifacts before testing")
    args, unittest_args = parser.parse_known_args()
    if args.run_pipelines:
        commands = [[sys.executable, "data_pipeline/pipeline.py"], [sys.executable, "analytics/analysis.py"]]
        for command in commands:
            result = run(command)
            print(result.stdout.strip())
        os.environ["MOCK_LLM"] = "1"
        support_env = os.environ.copy()
        support_env["RUN_EXAMPLES"] = "1"
        result = subprocess.run([sys.executable, "support_assistant/main.py"], cwd=ROOT, text=True, capture_output=True, check=True, env=support_env)
        print(result.stdout.strip())
    unittest.main(argv=[sys.argv[0], *unittest_args], verbosity=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
