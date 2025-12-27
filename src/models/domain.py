from dataclasses import dataclass

from pydantic import BaseModel

from criteria import BaseCriteria


@dataclass(frozen=True, slots=True)
class TechStackEntry:
    technology: str
    level_of_advancement: str


@dataclass(frozen=True, slots=True)
class RawJobOffer:
    html: str
    url: str


class JobOffer(BaseModel):
    title: str
    text: str
    tech_stack: list[TechStackEntry]
    location_country: str
    location_city: str
    remote_options: str
    seniority: str
    url: str
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_per: str | None = None

    def matches_criteria(self, criteria: list[BaseCriteria]) -> bool:
        return all(
            c.is_satisfied(
                context={
                    "tech_stack": self.tech_stack,
                    "remote_options": self.remote_options,
                    "location_city": self.location_city,
                }
            )
            for c in criteria
        )
