"""Audit and join the building and seismic sources."""

from dataclasses import asdict, dataclass

from .schema import JOIN_KEYS, SEISMIC_ONLY_COLUMNS, SHARED_COLUMNS, Scalar
from .validation import ValidationError, validate_keys


Key = tuple[str, str]


@dataclass(frozen=True)
class JoinAudit:
    building_rows: int
    seismic_rows: int
    matched_rows: int
    building_only_keys: int
    seismic_only_keys: int
    shared_field_mismatches: int

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


class JoinValidationError(ValidationError):
    """Raised with structured diagnostics when source integration fails."""

    def __init__(self, message: str, diagnostics: dict[str, object]) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics


def join_sources(
    building_rows: list[dict[str, Scalar]],
    seismic_rows: list[dict[str, Scalar]],
    *,
    require_complete_match: bool = True,
) -> tuple[list[dict[str, Scalar]], JoinAudit]:
    validate_keys(building_rows, "hospital_building")
    validate_keys(seismic_rows, "seismic_ratings")
    building_index = {_key(row): row for row in building_rows}
    seismic_index = {_key(row): row for row in seismic_rows}
    building_only = sorted(building_index.keys() - seismic_index.keys())
    seismic_only = sorted(seismic_index.keys() - building_index.keys())
    matched = sorted(building_index.keys() & seismic_index.keys())

    mismatches: list[tuple[Key, str, Scalar, Scalar]] = []
    integrated: list[dict[str, Scalar]] = []
    for key in matched:
        building = building_index[key]
        seismic = seismic_index[key]
        for column in SHARED_COLUMNS:
            if building[column] != seismic[column]:
                mismatches.append((key, column, building[column], seismic[column]))
        combined = dict(building)
        combined.update({column: seismic[column] for column in SEISMIC_ONLY_COLUMNS})
        integrated.append(combined)

    audit = JoinAudit(
        building_rows=len(building_rows),
        seismic_rows=len(seismic_rows),
        matched_rows=len(matched),
        building_only_keys=len(building_only),
        seismic_only_keys=len(seismic_only),
        shared_field_mismatches=len(mismatches),
    )

    problems: list[str] = []
    if mismatches:
        problems.append(f"shared fields disagree for {len(mismatches)} values")
    if require_complete_match and (building_only or seismic_only):
        problems.append(
            f"join is incomplete: building_only={len(building_only)}, "
            f"seismic_only={len(seismic_only)}"
        )
    if problems:
        diagnostics: dict[str, object] = {
            "audit": audit.as_dict(),
            "building_only_keys": [_key_record(key) for key in building_only],
            "seismic_only_keys": [_key_record(key) for key in seismic_only],
            "shared_field_mismatches": [
                {
                    "facility_id": key[0],
                    "building_id": key[1],
                    "field": field,
                    "building_value": building_value,
                    "seismic_value": seismic_value,
                }
                for key, field, building_value, seismic_value in mismatches
            ],
        }
        raise JoinValidationError("; ".join(problems), diagnostics)
    return integrated, audit


def _key(row: dict[str, Scalar]) -> Key:
    values = tuple(row[column] for column in JOIN_KEYS)
    if not all(isinstance(value, str) for value in values):
        raise ValidationError(f"Join key contains a non-string value: {values}")
    return values  # type: ignore[return-value]


def _key_record(key: Key) -> dict[str, str]:
    return {"facility_id": key[0], "building_id": key[1]}
