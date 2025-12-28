import json

from bs4 import BeautifulSoup
from pydantic import ValidationError
from yarl import URL

from constants import SINGLE_JOB_CLASS_NAME, SINGLE_JOB_TAG_NAME
from criteria import LocationCriteria
from exceptions import JustJoinITOfferStructureError
from jjit_api_client import JJITAPIClient
from models import JJITOffer, JobOffer, ProgrammingLanguage, TechStackEntry, WebsiteOkResponse




class JJITBoardParser:
    CLASS_NAME_EXTRA_DATA = "MuiStack-root mui-aa3a55"
    CLASS_NAME_TECHNOLOGIES = "MuiTypography-root MuiTypography-subtitle2 mui-p733mp"
    CLASS_NAME_LEVELS_OF_ADVANCEMENT = "MuiTypography-root MuiTypography-subtitle4 mui-1xcqefb"

    def __init__(self, api_client: JJITAPIClient):
        self.api_client = api_client

    async def find_offers(
        self,
        include_skills: list[str],
        location_criteria: list[LocationCriteria],
        language: ProgrammingLanguage,
    ) -> list[dict]:
        board_response_text = await self.api_client.fetch_base_board(language, include_skills)
        urls = self._extract_urls_to_individual_jobs(board_response_text)
        
        # TODO: Cache
        # TODO: Handle pagination
        # TODO: Test server for 100s of requests

        matched_offers = []
        async for offer_response in self.api_client.fetch_multiple_urls(urls):
            parsed = self._parse_offer(offer_response)
            if parsed.matches_location_criteria(location_criteria):
                matched_offers.append(parsed.as_dict())
        return matched_offers

    def _extract_urls_to_individual_jobs(self, website_response: WebsiteOkResponse) -> list[URL]:
        board_soup = BeautifulSoup(website_response.html, features="html.parser")
        offers_tags = board_soup.find_all(SINGLE_JOB_TAG_NAME, {"class": SINGLE_JOB_CLASS_NAME})
        return [
            self.api_client.build_url_for_individual_offer(job_offer_path)
            for t in offers_tags
            if (job_offer_path := str(t.get("href")))
        ]

    @classmethod
    def _parse_offer(cls, offer: WebsiteOkResponse) -> JobOffer:
        offer_soup = BeautifulSoup(offer.html, features="html.parser")
        offer_data = script_tag.text if (script_tag := offer_soup.find("script", type="application/ld+json")) else None
        if not offer_data:
            raise JustJoinITOfferStructureError("Tag containing necessary info not found")
        try:
            offer_data_json = JJITOffer(**json.loads(offer_data))
        except ValidationError as e:
            raise JustJoinITOfferStructureError("HTML file had different structure than expected") from e

        seniority, remote_options = cls._get_offer_extra_data(offer_soup)
        partial_offer = JobOffer(
            title=title.text if (title := offer_soup.find("title")) else "",
            text=offer_data_json.description,
            location_city=offer_data_json.location.address.city,
            location_country=offer_data_json.location.address.country,
            seniority=seniority,
            remote_options=remote_options,
            tech_stack=cls._get_tech_stack(offer_soup),
            url=offer.url,
        )
        if offer_data_json.salary:
            partial_offer.salary_min = offer_data_json.salary.value.min
            partial_offer.salary_max = offer_data_json.salary.value.max
            partial_offer.salary_currency = offer_data_json.salary.currency
            partial_offer.salary_per = offer_data_json.salary.value.per

        return partial_offer

    @classmethod
    def _get_offer_extra_data(cls, offer_soup: BeautifulSoup) -> tuple[str, str]:
        """
        Contract type, experience level, remote work options.
        """
        extra_data = offer_soup.find_all("div", {"class": cls.CLASS_NAME_EXTRA_DATA})
        if len(extra_data) != 4:
            raise JustJoinITOfferStructureError(
                "Job offer does not contain all of the expected fields."
                f"Expected length: 4, actual length: {len(extra_data)}. "
                f"Fields in the response: {extra_data}."
            )
        time, contract, seniority, remote_options = extra_data
        return seniority.text, remote_options.text

    @classmethod
    def _get_tech_stack(cls, offer_soup: BeautifulSoup) -> list[TechStackEntry]:
        technologies = offer_soup.find_all("h4", {"class": cls.CLASS_NAME_TECHNOLOGIES})
        levels_of_advancement = offer_soup.find_all("span", {"class": cls.CLASS_NAME_LEVELS_OF_ADVANCEMENT})
        if not technologies or not levels_of_advancement:
            raise JustJoinITOfferStructureError(
                f"Tech stack data missing. Technologies: {technologies}, levels of advancement: {levels_of_advancement}"
            )
        if len(technologies) != len(levels_of_advancement):
            raise JustJoinITOfferStructureError("Length of technologies list and level of advancement differ.")
        return [
            TechStackEntry(technology=label.text, level_of_advancement=level.text)
            for label, level in zip(technologies, levels_of_advancement, strict=True)
        ]
