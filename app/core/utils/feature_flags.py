from typing import Dict, Optional

from fastapi import Depends, HTTPException

from app.core.middleware.middleware import get_current_user

# Per-agency feature flags, hardcoded for now. Every agency gets DEFAULT_FEATURES;
# AGENCY_FEATURES overrides them by exact agency_name (as it appears in the JWT).
DEFAULT_FEATURES: Dict[str, bool] = {"umrah": False}
AGENCY_FEATURES: Dict[str, Dict[str, bool]] = {
    "Amin Travels & Tours": {"umrah": True},
}


def get_agency_features(agency_name: Optional[str]) -> Dict[str, bool]:
    return {**DEFAULT_FEATURES, **AGENCY_FEATURES.get(agency_name, {})}


def require_feature(feature: str):
    """Router-level dependency: 403 unless the caller's agency has `feature` enabled."""
    def dependency(current_user: dict = Depends(get_current_user)):
        if not get_agency_features(current_user.get("agency_name")).get(feature):
            raise HTTPException(status_code=403, detail=f"The {feature} feature is not enabled for your agency")
    return dependency
