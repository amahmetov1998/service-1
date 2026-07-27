from pydantic import BaseModel

from src.core.enums import OperatorType, RegionType


class PhoneDetailAPIRequest(BaseModel):
    phone_number: str
    operator_type: OperatorType
    region_type: RegionType
    is_spam: bool = False


class PhoneDetailAPIResponse(PhoneDetailAPIRequest):
    pass
