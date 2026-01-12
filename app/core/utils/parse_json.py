import json
from fastapi.exceptions import HTTPException


def parse_json(field):
    if field is None:
        return None
    try:
        return json.loads(field)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON for field: {field}"
        )