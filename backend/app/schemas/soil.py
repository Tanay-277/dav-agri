from typing import Dict, Optional
from pydantic import BaseModel

class SoilDataResponse(BaseModel):
    location: str
    properties: Dict[str, Dict[str, float]]  # friendly_name -> {depth: value}
    source: str = "soilgrids"
    is_live: bool = True
    language: str = "mr"
    localized_names: Optional[Dict[str, Dict[str, str]]] = None  # friendly_name -> {en, hi, mr}
