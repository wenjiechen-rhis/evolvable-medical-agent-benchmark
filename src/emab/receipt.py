from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import FROZEN_EXECUTION_FILES, PROTOCOL_VERSION
from .io import canonical_json_bytes, read_json, write_json_atomic


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_receipt(bundle: Path, created_at: str | None = None) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for relative in FROZEN_EXECUTION_FILES:
        path = bundle / relative
        if not path.is_file():
            raise FileNotFoundError(f"required frozen file missing: {relative}")
        entries.append({"path": relative, "sha256": sha256_file(path), "bytes": path.stat().st_size})
    digest_material = [{"path": item["path"], "sha256": item["sha256"], "bytes": item["bytes"]} for item in entries]
    bundle_digest = hashlib.sha256(canonical_json_bytes(digest_material)).hexdigest()
    return {
        "protocol_version": PROTOCOL_VERSION,
        "algorithm": "sha256",
        "created_at": created_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "files": entries,
        "bundle_digest": bundle_digest,
    }


def freeze_bundle(bundle: Path, output: Path, force: bool = False) -> dict[str, Any]:
    if output.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing receipt: {output}")
    receipt = build_receipt(bundle)
    write_json_atomic(output, receipt)
    return receipt


def verify_receipt(bundle: Path, receipt_path: Path | None = None) -> list[str]:
    receipt_path = receipt_path or bundle / "receipt.json"
    if not receipt_path.is_file():
        return ["receipt.json is missing"]
    try:
        receipt = read_json(receipt_path)
    except Exception as exc:
        return [f"receipt could not be read: {exc}"]
    errors: list[str] = []
    if receipt.get("protocol_version") != PROTOCOL_VERSION:
        errors.append("receipt protocol_version does not match this toolkit")
    if receipt.get("algorithm") != "sha256":
        errors.append("receipt algorithm must be sha256")
    files = receipt.get("files")
    if not isinstance(files, list):
        return errors + ["receipt files must be an array"]
    actual_entries: list[dict[str, Any]] = []
    expected_paths = set(FROZEN_EXECUTION_FILES)
    seen_paths: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            errors.append("receipt contains a non-object file entry")
            continue
        relative = item.get("path")
        if not isinstance(relative, str):
            errors.append("receipt file entry has no string path")
            continue
        seen_paths.add(relative)
        path = bundle / relative
        if not path.is_file():
            errors.append(f"frozen file missing: {relative}")
            continue
        actual_digest = sha256_file(path)
        actual_size = path.stat().st_size
        if item.get("sha256") != actual_digest:
            errors.append(f"digest mismatch: {relative}")
        if item.get("bytes") != actual_size:
            errors.append(f"size mismatch: {relative}")
        actual_entries.append({"path": relative, "sha256": actual_digest, "bytes": actual_size})
    missing_receipt_entries = expected_paths - seen_paths
    extra_receipt_entries = seen_paths - expected_paths
    for relative in sorted(missing_receipt_entries):
        errors.append(f"receipt entry missing: {relative}")
    for relative in sorted(extra_receipt_entries):
        errors.append(f"unexpected frozen receipt entry: {relative}")
    actual_entries.sort(key=lambda item: FROZEN_EXECUTION_FILES.index(item["path"]) if item["path"] in expected_paths else len(expected_paths))
    actual_bundle_digest = hashlib.sha256(canonical_json_bytes(actual_entries)).hexdigest()
    if receipt.get("bundle_digest") != actual_bundle_digest:
        errors.append("bundle_digest mismatch")
    return errors


def receipt_file_digest(bundle: Path) -> str | None:
    path = bundle / "receipt.json"
    return sha256_file(path) if path.is_file() else None
