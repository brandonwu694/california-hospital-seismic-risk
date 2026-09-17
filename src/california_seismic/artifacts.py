"""Fingerprint, verify, and atomically publish pipeline artifacts."""

import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path
from typing import Any


class ArtifactError(RuntimeError):
    """Raised when a staged or published artifact is inconsistent."""


def fingerprint(
    path: Path, *, relative_to: Path | None = None
) -> dict[str, str | int]:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    display_path = (
        os.path.relpath(path.resolve(), relative_to.resolve())
        if relative_to is not None
        else str(path.resolve())
    )
    return {
        "path": display_path,
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
    }


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def artifact_record(
    staged: Path, target: Path, *, relative_to: Path
) -> dict[str, str | int]:
    record = fingerprint(staged)
    record["path"] = os.path.relpath(target.resolve(), relative_to.resolve())
    return record


def publish_artifacts(
    artifacts: Sequence[tuple[Path, Path]],
    manifest_path: Path,
    manifest_payload: Mapping[str, Any],
    staging_dir: Path,
) -> None:
    staged_manifest = staging_dir / manifest_path.name
    write_json(staged_manifest, manifest_payload)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.unlink(missing_ok=True)
    for staged, target in artifacts:
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged, target)
    os.replace(staged_manifest, manifest_path)


def verify_manifest(path: Path) -> None:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArtifactError(f"Cannot read completion manifest: {path}") from exc
    if manifest.get("status") != "complete":
        raise ArtifactError(f"Manifest is not complete: {path}")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise ArtifactError(f"Manifest contains no artifacts: {path}")
    for role, expected in artifacts.items():
        if not isinstance(expected, dict) or not {
            "path",
            "bytes",
            "sha256",
        }.issubset(expected):
            raise ArtifactError(f"Manifest has an invalid {role} record: {path}")
        if not isinstance(expected["path"], str):
            raise ArtifactError(f"Manifest has an invalid {role} path: {path}")
        artifact_path = Path(expected["path"])
        if not artifact_path.is_absolute():
            artifact_path = (path.parent / artifact_path).resolve()
        try:
            observed = fingerprint(artifact_path)
        except OSError as exc:
            raise ArtifactError(f"Missing {role} artifact: {artifact_path}") from exc
        if (
            observed["bytes"] != expected["bytes"]
            or observed["sha256"] != expected["sha256"]
        ):
            raise ArtifactError(f"Artifact does not match manifest: {artifact_path}")
