#!/usr/bin/env python3
"""Audit release evidence traceability for rfp-architect."""

import argparse
import hashlib
import json
from pathlib import Path


BAD_COMMIT_MARKERS = ("local-only", "local working tree")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_source_path(release_dir: Path, source_path: str) -> Path:
    # Evidence may come from another machine; use the release-local basename.
    return release_dir / Path(source_path).name


def check_commit(value: str, label: str, findings: list):
    if not value:
        findings.append(f"{label} is missing")
        return
    if any(marker in value for marker in BAD_COMMIT_MARKERS):
        findings.append(f"{label} is not traceable: {value}")


def _version_key(value: str) -> tuple:
    parts = []
    for chunk in str(value).split("."):
        parts.append(int(chunk) if chunk.isdigit() else 0)
    return tuple(parts)


def _latest_evidence(release_dir: Path) -> Path:
    """Audit the latest release: pick the evidence-*.json with the highest `version`.
    Older dated artifacts are retained as history but not re-audited."""
    candidates = sorted(release_dir.glob("evidence-*.json"))
    if not candidates:
        raise FileNotFoundError(f"no evidence-*.json in {release_dir}")
    return max(candidates, key=lambda p: _version_key(json.loads(p.read_text(encoding="utf-8")).get("version", "0")))


def audit(root: Path) -> dict:
    release_dir = root / "release"
    evidence_path = _latest_evidence(release_dir)
    findings = []
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    summary_path = release_dir / Path(evidence["benchmark_summary_path"]).name
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    source_path = local_source_path(release_dir, summary["source_path"])
    if not source_path.exists():
        findings.append(f"benchmark source not found: {source_path}")
    else:
        actual = sha256(source_path)
        expected = summary.get("source_sha256")
        if actual != expected:
            findings.append(f"benchmark summary source_sha256 mismatch: expected {expected}, actual {actual}")

    embedded = evidence.get("benchmark_summary", {})
    if embedded.get("source_sha256") != summary.get("source_sha256"):
        findings.append("embedded benchmark_summary source_sha256 differs from benchmark summary file")

    check_commit(evidence.get("commit", ""), "evidence.commit", findings)
    check_commit(summary.get("metadata", {}).get("git_commit", ""), "summary.metadata.git_commit", findings)
    check_commit(embedded.get("metadata", {}).get("git_commit", ""), "evidence.benchmark_summary.metadata.git_commit", findings)

    return {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "checked_files": [
            str(evidence_path),
            str(summary_path),
            str(source_path),
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="repo or skill root")
    parser.add_argument("--json", action="store_true")
    ns = parser.parse_args()
    result = audit(Path(ns.root).resolve())
    if ns.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["status"])
        for finding in result["findings"]:
            print(f"- {finding}")
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
