from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from yandex_py.direct.rpc import DirectUnits


class RegionalAdjustment(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    region_id: int | None = Field(default=None, alias="RegionId")
    bid_modifier: int | None = Field(default=None, alias="BidModifier")
    enabled: str | None = Field(default=None, alias="Enabled")


class BidModifier(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int | None = Field(default=None, alias="Id")
    campaign_id: int | None = Field(default=None, alias="CampaignId")
    ad_group_id: int | None = Field(default=None, alias="AdGroupId")
    level: str | None = Field(default=None, alias="Level")
    type: str | None = Field(default=None, alias="Type")
    regional_adjustment: RegionalAdjustment | None = Field(
        default=None, alias="RegionalAdjustment"
    )


class BidModifiersPage(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bid_modifiers: list[BidModifier] = Field(default_factory=list, alias="BidModifiers")
    limited_by: int | None = Field(default=None, alias="LimitedBy")
    units: DirectUnits | None = None
