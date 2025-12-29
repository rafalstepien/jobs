from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LRUCacheEntry:
    created_at: datetime
    html_content: str

    _older: Optional["LRUCacheEntry"] = None
    _newer: Optional["LRUCacheEntry"] = None

    @classmethod
    def build(cls, html_content: str) -> "LRUCacheEntry":
        return cls(
            created_at=datetime.now(),
            html_content=html_content,
        )


class LRUCacheManager:
    def __init__(self, entry_limit: int):
        self.entry_limit = entry_limit
        self._cache_entries: dict[str, LRUCacheEntry] = {}
        self._newest = None
        self._oldest = None
        self._size = 0

    def put(self, url: str, html_content: str) -> None:
        e = LRUCacheEntry.build(html_content)
        self._cache_entries[url] = e
        self._add_node(e)

    def get(self, url: str) -> str | None:
        cache_hit = self._cache_entries.get(url)
        self._move_node_to_front(cache_hit)
        return cache_hit

    def _add_node(self, e: LRUCacheEntry) -> None:
        if self._newest is None:
            self._newest = e
            self._oldest = e
            self._size += 1
        elif self._size == self.entry_limit:
            self.__remove_oldest_node()
            self.__add_newest_node(e)
        else:
            self.__add_newest_node(e)
            self._size += 1

    def __add_newest_node(self, e: LRUCacheEntry) -> None:
        self._newest._newer = e
        e._older = self._newest
        self._newest = e

    def __remove_oldest_node(self) -> None:
        newer = self._oldest._newer
        self._oldest._newer = None
        self._oldest = newer
        self._oldest._older = None

    def _move_node_to_front(self, node: LRUCacheEntry) -> None:
        older = node._older
        newer = node._newer

        if not newer:
            return

        if not older:
            node._newer._older = None
            node._newer = None

            node._older = self._newest
            self._newest._newer = node
            self._newest = node

        elif older:
            node._newer._older = None
            node._newer = None

            node._older._newer = None
            node._older = None

            node._older = self._newest
            self._newest._newer = node
            self._newest = node
