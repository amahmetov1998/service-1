from pydantic import BaseModel, field_validator, Field, ConfigDict

from src.enums import PhoneType, OperatorType, RegionType


class PhoneCreateRequest(BaseModel):
    phone_number: str = Field(max_length=20)
    phone_type: PhoneType
    is_verified: bool = False

    operator_type: OperatorType
    region_type: RegionType
    is_spam: bool = False

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not all(char.isdigit() or char in "+() -" for char in v):
            raise ValueError("Phone number must contain only digits")
        return v


class PhoneResponse(PhoneCreateRequest):
    pass


class PhoneDetailAPIRequest(BaseModel):
    phone_number: str
    operator_type: OperatorType
    region_type: RegionType
    is_spam: bool = False

    model_config = ConfigDict(from_attributes=True)


class PhoneDetailAPIResponse(PhoneDetailAPIRequest):
    pass


class PhoneNumbers(BaseModel):
    phone_numbers: list[str]
