from custom_cache import LRUCacheManager


def test__cache_happy_path():
    manager = LRUCacheManager(entry_limit=3)
    urls = {
        "http://test-url-1": "html1",
        "http://test-url-2": "html2",
        "http://test-url-3": "html3",
    }

    for url, html in urls.items():
        manager.put(url, html)

    assert all([url in manager._cache_entries for url in urls])


def test__cache_exceeded_limit():
    manager = LRUCacheManager(entry_limit=2)
    urls = {
        "http://test-url-1": "html1",
        "http://test-url-2": "html2",
        "http://test-url-3": "html3",
    }

    for url, html in urls.items():
        manager.put(url, html)

    assert manager._size == 2
    assert manager._newest.html_content == "html3"
    assert manager._oldest.html_content == "html2"


def test__cache_hit_newest_node(): ...


def test__cache_hit_oldest_node(): ...


def test__cache_hit_middle_node(): ...
