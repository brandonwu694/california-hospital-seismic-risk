"""Audit and join the building and seismic sources."""

from dataclasses import asdict, dataclass

from .cleaning.quality import add_dataset_review_flags, add_review_flags
from .cleaning.values import Scalar
from .schema import JOIN_KEYS, SEISMIC_ONLY_COLUMNS, SHARED_COLUMNS
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
        integrated.append(add_review_flags(combined))

    audit = JoinAudit(
        building_rows=len(building_rows),
        seismic_rows=len(seismic_rows),
        matched_rows=len(matched),
        building_only_keys=len(building_only),
        seismic_only_keys=len(seismic_only),
        shared_field_mismatches=len(mismatches),
    )

    if mismatches:
        raise ValidationError(
            f"Shared fields disagree for {len(mismatches)} values; sample={mismatches[:5]}"
        )
    if require_complete_match and (building_only or seismic_only):
        raise ValidationError(
            "Join is incomplete; "
            f"building_only={len(building_only)}, seismic_only={len(seismic_only)}, "
            f"building_sample={building_only[:5]}, seismic_sample={seismic_only[:5]}"
        )
    return add_dataset_review_flags(integrated), audit


def _key(row: dict[str, Scalar]) -> Key:
    values = tuple(row[column] for column in JOIN_KEYS)
    if not all(isinstance(value, str) for value in values):
        raise ValidationError(f"Join key contains a non-string value: {values}")
    return values  # type: ignore[return-value]
