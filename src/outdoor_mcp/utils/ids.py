from __future__ import annotations

from ..models.common import Coordinates
from ..core.exceptions import ValidationError


def coords_from_location_id(location_id: str) -> Coordinates:
    # Expected format: osm:<type>:<id>:<lat>:<lon>
    parts = location_id.split(":")
    if len(parts) < 5:
        raise ValidationError(code="invalid_location_id", message="Unsupported location_id format.", details={"location_id": location_id})
    try:
        lat = float(parts[-2])
        lon = float(parts[-1])
    except ValueError:
        raise ValidationError(code="invalid_location_id", message="location_id does not contain valid coordinates.", details={"location_id": location_id})
    return Coordinates(lat=lat, lon=lon)
