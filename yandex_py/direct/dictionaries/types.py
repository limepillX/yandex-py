from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GeoRegion(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    geo_region_id: int = Field(alias="GeoRegionId")
    geo_region_name: str | None = Field(default=None, alias="GeoRegionName")
    geo_region_type: str | None = Field(default=None, alias="GeoRegionType")
    parent_id: int | None = Field(default=None, alias="ParentId")
