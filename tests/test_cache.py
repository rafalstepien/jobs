from src.custom_cache import LRUCacheManager


def test__cache_happy_path():
    manager = LRUCacheManager(entry_limit=3)
    urls = {
        "http://test-url-1": "html1",
        "http://test-url-2": "html2",
        "http://test-url-3": "html3",
    }

    for url, html in urls.items():
        manager.put(url, html)
        
    assert manager._size == 3

    assert manager._newest.html_content == "html3"
    assert manager._newest._older.html_content == "html2"
    assert manager._newest._older._older.html_content == "html1"


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


def test__cache_hit_newest_node():
    manager = LRUCacheManager(entry_limit=3)
    urls = {
        "http://test-url-1": "html1",
        "http://test-url-2": "html2",
        "http://test-url-3": "html3",
    }
    
    for url, html in urls.items():
        manager.put(url, html)
    
    cache_hit = manager.get("http://test-url-3")
    
    assert manager._size == 3
    
    assert cache_hit.html_content == "html3"
    assert cache_hit._older.html_content == "html2"
    assert cache_hit._older._older.html_content == "html1"
    
    

def test__cache_hit_oldest_node():
    manager = LRUCacheManager(entry_limit=3)
    urls = {
        "http://test-url-1": "html1",#    --+
        "http://test-url-2": "html2",#      |
        "http://test-url-3": "html3",#      |
    }  #                             <------+
    
    for url, html in urls.items():
        manager.put(url, html)
    
    cache_hit = manager.get("http://test-url-1")
    
    assert manager._size == 3
    
    assert cache_hit.html_content == "html1"
    assert cache_hit._older.html_content == "html3"
    assert cache_hit._older._older.html_content == "html2"
    


def test__cache_hit_middle_node():
    manager = LRUCacheManager(entry_limit=5)
    urls = {
        "http://test-url-1": "html1",
        "http://test-url-2": "html2",
        "http://test-url-3": "html3",#  --+
        "http://test-url-4": "html4",#    |
        "http://test-url-5": "html5",#    |
    }  #                           <------+ 
    
    for url, html in urls.items():
        manager.put(url, html)
    
    cache_hit = manager.get("http://test-url-3")
    
    assert manager._size == 5
    
    assert cache_hit.html_content == "html3"
    assert cache_hit._older.html_content == "html5"
    assert cache_hit._older._older.html_content == "html4"
    assert cache_hit._older._older._older.html_content == "html2"
    assert cache_hit._older._older._older._older.html_content == "html1"
