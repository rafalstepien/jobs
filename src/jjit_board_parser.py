import json

from bs4 import BeautifulSoup
from constants import BASE_URL, SINGLE_JOB_CLASS_NAME, SINGLE_JOB_TAG_NAME
from criteria import BaseCriteria
from exceptions import JobOfferStructureError
from models.third_party_responses import JustJoinITOffer
from models.domain import (
    JobOffer,
    RawJobOffer,
    TechStackEntry,
)
from pydantic import ValidationError
from utils import open_html
from yarl import URL

# TODO:
# 1) request actual offers
# 2) setup sending emails
# 3) setup scheduler


class JJITBoardParser:
    CLASS_NAME_EXTRA_DATA = "MuiStack-root mui-aa3a55"
    CLASS_NAME_TECHNOLOGIES = "MuiTypography-root MuiTypography-subtitle2 mui-p733mp"
    CLASS_NAME_LEVELS_OF_ADVANCEMENT = "MuiTypography-root MuiTypography-subtitle4 mui-1xcqefb"

    @classmethod
    def find_offers(cls, criteria: list[BaseCriteria]) -> list[JobOffer]:
        board_response_text = open_html("board_response_python_rust")
        urls = cls._get_offers_urls(board_response_text)
        offers_texts = cls._get_offers_html(urls)
        parsed_offers = [cls._parse_offer(o) for o in offers_texts]
        return [o.model_dump() for o in parsed_offers if o.matches_criteria(criteria)]

    @classmethod
    def _get_offers_html(cls, urls: list[str]) -> list[RawJobOffer]:
        """
        TODO: make actual requests
        """
        return [
            RawJobOffer(
                html=open_html("single_offer_rust"),
                url="https://justjoin.it/job-offer/air-space-intelligence-software-engineer-gdansk-python-e10b493e",
            ),
            RawJobOffer(
                html=open_html("single_offer_rust2"),
                url="https://justjoin.it/job-offer/hyperexponential-senior-software-engineer-rust--warszawa-python",
            ),
            RawJobOffer(
                html=open_html("single_offer_multiple_cities"),
                url="https://justjoin.it/job-offer/grid-dynamics-poland-senior-full-stack-developer-python-typescript--warszawa-python",
            ),
        ]

    @classmethod
    def _get_offers_urls(cls, board_response_text: str) -> list[URL]:
        board_soup = BeautifulSoup(board_response_text, features="html.parser")
        offers_tags = board_soup.find_all(SINGLE_JOB_TAG_NAME, {"class": SINGLE_JOB_CLASS_NAME})
        return [BASE_URL / job_offer_path.lstrip("/") for t in offers_tags if (job_offer_path := t.get("href"))]

    @classmethod
    def _parse_offer(cls, offer: RawJobOffer) -> JobOffer:
        offer_soup = BeautifulSoup(offer.html, features="html.parser")
        try:
            offer_data_json = JustJoinITOffer(**json.loads(offer_soup.find("script", type="application/ld+json").text))
        except ValidationError:
            print("----------------------------- Error parsing job offer data json ---------------------------")
            raise

        seniority, remote_options = cls._get_offer_extra_data(offer_soup)
        offer = JobOffer(
            title=offer_soup.find("title").text,
            text=offer_data_json.description,
            location_city=offer_data_json.location.address.city,
            location_country=offer_data_json.location.address.country,
            seniority=seniority,
            remote_options=remote_options,
            tech_stack=cls._get_tech_stack(offer_soup),
            url=offer.url,
        )
        if offer_data_json.salary:
            offer.salary_min = offer_data_json.salary.value.min
            offer.salary_max = offer_data_json.salary.value.max
            offer.salary_currency = offer_data_json.salary.currency
            offer.salary_per = offer_data_json.salary.value.per
        return offer

    @classmethod
    def _get_offer_extra_data(cls, offer_soup: BeautifulSoup) -> tuple[str, str]:
        """
        Contract type, experience level, remote work options
        """
        extra_data = offer_soup.findAll("div", {"class": cls.CLASS_NAME_EXTRA_DATA})
        if len(extra_data) != 4:
            raise JobOfferStructureError("Job offer had different number of extra data items")
        time, contract, seniority, remote_options = extra_data
        return seniority.text, remote_options.text

    @classmethod
    def _get_tech_stack(cls, offer_soup: BeautifulSoup) -> list[TechStackEntry]:
        technologies = offer_soup.findAll("h4", {"class": cls.CLASS_NAME_TECHNOLOGIES})
        levels_of_advancement = offer_soup.findAll("span", {"class": cls.CLASS_NAME_LEVELS_OF_ADVANCEMENT})
        return [
            TechStackEntry(technology=label.text, level_of_advancement=level.text)
            for label, level in zip(technologies, levels_of_advancement)
        ]
