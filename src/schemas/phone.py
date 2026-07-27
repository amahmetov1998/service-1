from pydantic import BaseModel

from src.core.enums import PhoneType, OperatorType, RegionType


class PhoneCreateRequest(BaseModel):
    phone_number: str
    phone_type: PhoneType
    is_verified: bool = False

    operator_type: OperatorType
    region_type: RegionType
    is_spam: bool = False


class PhoneResponse(PhoneCreateRequest):
    pass
