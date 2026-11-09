#!/usr/bin/env python3
"""Narrow read-only final-delivery review using the preserved publication checker."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("preserved_publication_review", HERE / "publication_review.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
# Only current navigation and this run's mutable report/ledger may change.
review.DOCS = {
    "README.md", "docs/STATUS.md", "docs/BOT_PORTFOLIO.md", "docs/CONTEST_DELIVERY.md",
    "docs/EXPERIMENT_TIMELINE.md", "docs/rl/README.md", "docs/rl/v7/D16.md", "docs/rl/v7/PLAN.md",
    "experiments/rl/2026-11-09-final-delivery/REPORT.md",
    "experiments/rl/2026-11-09-final-delivery/COMMANDS.md",
}
review.PREFIXES = ("experiments/rl/2026-11-09-final-delivery/",)

if __name__ == "__main__":
    raise SystemExit(review.main())