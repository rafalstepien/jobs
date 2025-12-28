from dataclasses import dataclass

from yarl import URL

from criteria import BaseCriteria


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
class WebsiteResponse:
    html: str
    url: URL


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

    def as_dict(self) -> dict:
        base_data = {
            "title": self.title,
            "text": self.text,
            "tech_stack": [ts.as_dict() for ts in self.tech_stack],
            "location_country": self.location_country,
            "location_city": self.location_city,
            "remote_options": self.remote_options,
            "seniority": self.seniority,
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
