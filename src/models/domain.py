from dataclasses import dataclass
from enum import StrEnum

from yarl import URL

from criteria import LocationCriteria


class ProgrammingLanguage(StrEnum):
    PYTHON = "python"
    AI = "ai"
    ANALYTICS = "analytics"
    GO = "go"


@dataclass(frozen=True, slots=True)
class TechStackEntry:
    technology: str
    level_of_advancement: str

    def as_dict(self) -> dict:
        return {
            "technology": self.technology,
            "level_of_advancement": self.level_of_advancement,
        }


@dataclass(frozen=True, slots=True)
class WebsiteOkResponse:
    html: str
    url: URL


@dataclass(frozen=True, slots=True)
class WebsiteErrorResponse:
    url: URL
    msg: str
    status: int | None = None


@dataclass
class JobOffer:
    title: str
    text: str
    tech_stack: list[TechStackEntry]
    location_country: str
    location_city: str
    remote_options: str
    seniority: str
    url: URL
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_per: str | None = None

    def matches_location_criteria(self, location_criteria: list[LocationCriteria]):
        return all(c.is_satisfied(self.remote_options, self.location_city) for c in location_criteria)

    def as_dict(self) -> dict:
        base_data = {
            "title": self.title,
            "text": self.text,
            "tech_stack": [ts.as_dict() for ts in self.tech_stack],
            "location_country": self.location_country,
            "location_city": self.location_city,
            "remote_options": self.remote_options,
            "seniority": self.seniority,
            "url": str(self.url),
        }
        if all((self.salary_min, self.salary_max, self.salary_currency, self.salary_per)):
            return {
                **base_data,
                "salary_min": self.salary_min,
                "salary_max": self.salary_max,
                "salary_currency": self.salary_currency,
                "salary_per": self.salary_per,
            }
        return base_data
