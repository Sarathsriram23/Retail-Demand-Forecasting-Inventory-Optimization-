from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional

class CalendarRow(BaseModel):
    """Pydantic model representing a single row in the Calendar dimension table."""
    date: date
    wm_yr_wk: int = Field(..., ge=11101, le=12000)
    weekday: str
    wday: int = Field(..., ge=1, le=7)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2011, le=2018)
    d: str
    event_name_1: Optional[str] = "None"
    event_type_1: Optional[str] = "None"
    event_name_2: Optional[str] = "None"
    event_type_2: Optional[str] = "None"
    snap_CA: int = Field(..., ge=0, le=1)
    snap_TX: int = Field(..., ge=0, le=1)
    snap_WI: int = Field(..., ge=0, le=1)

    @field_validator("d")
    def validate_day_format(cls, v):
        if not v.startswith("d_"):
            raise ValueError("Day index must start with 'd_' prefix")
        return v

class SellPriceRow(BaseModel):
    """Pydantic model representing a single row in the Sell Prices table."""
    store_id: str
    item_id: str
    wm_yr_wk: int = Field(..., ge=11101, le=12000)
    sell_price: float = Field(..., gt=0.0)

class SalesValidationRow(BaseModel):
    """Pydantic model representing metadata for a series in Sales Staging validation."""
    id: str
    item_id: str
    dept_id: str
    cat_id: str
    store_id: str
    state_id: str

class SalesFactRow(BaseModel):
    """Pydantic model representing a single row in the long-format Sales Fact analytics table."""
    id: str
    item_id: str
    dept_id: str
    cat_id: str
    store_id: str
    state_id: str
    d: str
    date: date
    sales_qty: int = Field(..., ge=0)
