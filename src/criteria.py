from abc import ABC, abstractmethod
from difflib import SequenceMatcher
from enum import StrEnum
from typing import Callable, Literal, Mapping

from pydantic import BaseModel


class LocationKeyword(BaseModel):
    form: str | None = None
    city: str | None = None


class TechKeyword(BaseModel):
    name: str


class CriteriaRule(StrEnum):
    ALL = "all"
    AT_LEAST_ONE = "at_least_one"


class CriteriaKind(StrEnum):
    TECH = "tech"
    LOCATION = "location"


class BaseCriteria(BaseModel, ABC):
    rule: CriteriaRule
    kind: CriteriaKind

    @abstractmethod
    def is_satisfied(self, context: dict) -> bool: ...


RULES_MAPPING: Mapping[CriteriaRule, Callable] = {CriteriaRule.ALL: all, CriteriaRule.AT_LEAST_ONE: any}


class TechCriteria(BaseCriteria):
    kind: Literal[CriteriaKind.TECH] = CriteriaKind.TECH
    keywords: list[TechKeyword]

    def is_satisfied(self, context: dict) -> bool:
        keywords_matched = []
        for keyword in self.keywords:
            keyword_appended = False
            for tse in context.get("tech_stack"):
                if words_are_similar(keyword.name, tse.technology):
                    keywords_matched.append(True)
                    keyword_appended = True
            if not keyword_appended:
                keywords_matched.append(False)
        return RULES_MAPPING.get(self.rule)(keywords_matched)


class LocationCriteria(BaseCriteria):
    kind: Literal[CriteriaKind.LOCATION] = CriteriaKind.LOCATION
    keywords: list[LocationKeyword]

    def is_satisfied(self, context: dict) -> bool:
        # TODO: what if there are multiple cities in job description?
        # TODO: what if there are multiple options specified in description
        
        keywords_matched = []
        for keyword in self.keywords:
            keywords_matched.append(
                words_are_similar(keyword.form, context.get("remote_options"))
                and words_are_similar(keyword.city, context.get("location_city"))
            )
        return RULES_MAPPING.get(self.rule)(keywords_matched)


def words_are_similar(w1: str, w2: str) -> bool:
    THRESHOLD = 0.75
    return SequenceMatcher(None, w1.lower(), w2.lower()).ratio() >= THRESHOLD
