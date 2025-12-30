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


class DoublyLinkedList:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.newest: LRUCacheEntry | None = None
        self.oldest: LRUCacheEntry | None = None
        self.size = 0

    def add_node(self, e: LRUCacheEntry) -> None:
        if self.newest is None:
            self.newest = e
            self.oldest = e
            self.size += 1
        elif self.size == self.capacity:
            self._remove_oldest_node()
            self._add_newest_node(e)
        else:
            self._add_newest_node(e)
            self.size += 1

    def move_node_to_front(self, node: LRUCacheEntry) -> None:
        older = node._older
        newer = node._newer

        if not newer:
            return

        if not older:
            new_oldest = node._newer

            node._newer._older = None
            node._newer = None

            node._older = self.newest
            self.newest._newer = node
            self.newest = node

            self.oldest = new_oldest

        elif older:
            node._newer._older = node._older
            node._newer = None

            node._older._newer = node._newer
            node._older = None

            node._older = self.newest
            self.newest._newer = node
            self.newest = node

    def _add_newest_node(self, e: LRUCacheEntry) -> None:
        self.newest._newer = e
        e._older = self.newest
        self.newest = e

    def _remove_oldest_node(self) -> None:
        newer = self.oldest._newer
        self.oldest._newer = None
        self.oldest = newer
        self.oldest._older = None


class LRUCacheManager:
    def __init__(self, capacity: int):
        self._cache_entries: dict[str, LRUCacheEntry] = {}
        self._order = DoublyLinkedList(capacity)

    def put(self, url: str, html_content: str) -> None:
        e = LRUCacheEntry.build(html_content)
        self._cache_entries[url] = e
        self._order.add_node(e)

    def get(self, url: str) -> LRUCacheEntry | None:
        cache_hit = self._cache_entries.get(url)
        if cache_hit:
            self._order.move_node_to_front(cache_hit)
            return cache_hit
        return None
