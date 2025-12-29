from collections.abc import Callable, Mapping
from difflib import SequenceMatcher
from enum import StrEnum

from pydantic import BaseModel


class LocationKeyword(BaseModel):
    form: str
    city: str | None = None


class LocationRule(StrEnum):
    ALL = "all"
    AT_LEAST_ONE = "at_least_one"


RULES_MAPPING: Mapping[LocationRule, Callable] = {LocationRule.ALL: all, LocationRule.AT_LEAST_ONE: any}
WORD_SIMILARITY_THRESHOLD = 0.75  # if words similarity score is less than this value, then words are not similar


class LocationCriteria(BaseModel):
    keywords: list[LocationKeyword]
    rule: LocationRule

    def is_satisfied(self, remote_options: str, city: str) -> bool:
        keywords_matched = []
        for keyword in self.keywords:
            if keyword.city:
                keywords_matched.append(
                    words_are_similar(keyword.form, remote_options) and words_are_similar(keyword.city, city)
                )
            else:
                keywords_matched.append(words_are_similar(keyword.form, remote_options))
        return RULES_MAPPING.get(self.rule)(keywords_matched)  # type: ignore[misc]


def words_are_similar(w1: str, w2: str) -> bool:
    """
    Handle simple typos.
    """
    return SequenceMatcher(None, w1.lower(), w2.lower()).ratio() >= WORD_SIMILARITY_THRESHOLD
