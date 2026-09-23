from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FeedEventCreate(BaseModel):
    pond_id: int = Field(..., alias="pondId")
    fed_at: datetime = Field(..., alias="fedAt")
    feed_type: str = Field(..., min_length=1, max_length=64, alias="feedType")
    amount_kg: float = Field(..., gt=0, alias="amountKg")
    operator_name: str = Field(..., min_length=1, max_length=64, alias="operatorName")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("operator_name")
    @classmethod
    def operator_name_stripped_nonempty(cls, value: str) -> str:
        # 读入即去首尾空白,去空白后不允许为空,保证入库非空
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("操作人不能为空")
        return cleaned


class FeedEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    pond_id: int = Field(serialization_alias="pondId")
    fed_at: datetime = Field(serialization_alias="fedAt")
    feed_type: str = Field(serialization_alias="feedType")
    amount_kg: float = Field(serialization_alias="amountKg")
    operator_name: str = Field(serialization_alias="operatorName")

    @field_validator("operator_name")
    @classmethod
    def operator_name_stripped_on_read(cls, value: str) -> str:
        # 读出同样去首尾空白,兼容历史脏数据
        return value.strip()
