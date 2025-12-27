from pydantic import BaseModel, Field


class JJITSalaryValue(BaseModel):
    per: str = Field(alias="unitText")
    min: int = Field(alias="minValue")
    max: int = Field(alias="maxValue")


class JJITSalary(BaseModel):
    currency: str
    value: JJITSalaryValue


class JJITAddress(BaseModel):
    country: str = Field(alias="addressCountry")
    city: str = Field(alias="addressLocality")


class JJITLocation(BaseModel):
    address: JJITAddress


class JJITOffer(BaseModel):
    description: str
    salary: JJITSalary | None = Field(alias="baseSalary", default=None)
    location: JJITLocation = Field(alias="jobLocation")
