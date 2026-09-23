from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FeedEventCreate(BaseModel):
    pond_id: int = Field(..., alias="pondId")
    fed_at: datetime = Field(..., alias="fedAt")
    feed_type: str = Field(..., min_length=1, max_length=64, alias="feedType")
    amount_kg: float = Field(..., gt=0, alias="amountKg")
    operator_name: str = Field(..., max_length=64, alias="operatorName")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("operator_name")
    @classmethod
    def strip_and_require_operator(cls, value: str) -> str:
        # 读写两侧统一去空白；入库必须非空，避免“留空”记录。
        value = value.strip()
        if not value:
            raise ValueError("操作人不能为空")
        return value


class FeedEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    pond_id: int = Field(serialization_alias="pondId")
    fed_at: datetime = Field(serialization_alias="fedAt")
    feed_type: str = Field(serialization_alias="feedType")
    amount_kg: float = Field(serialization_alias="amountKg")
    operator_name: str = Field(serialization_alias="operatorName")

    @field_validator("operator_name", "feed_type", mode="after")
    @classmethod
    def strip_on_read(cls, value: str) -> str:
        # 读出时也去空白，兼容历史数据。
        return value.strip()
