from pydantic import BaseModel, Field


class SalaryValue(BaseModel):
    per: str = Field(alias="unitText")
    min: int = Field(alias="minValue")
    max: int = Field(alias="maxValue")


class Salary(BaseModel):
    currency: str
    value: SalaryValue


class Address(BaseModel):
    country: str = Field(alias="addressCountry")
    city: str = Field(alias="addressLocality")


class Location(BaseModel):
    address: Address


class JustJoinITOffer(BaseModel):
    description: str
    salary: Salary | None = Field(alias="baseSalary", default=None)
    location: Location = Field(alias="jobLocation")
