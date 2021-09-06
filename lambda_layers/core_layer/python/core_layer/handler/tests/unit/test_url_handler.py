from urllib.parse import urlparse
import pytest
from core_layer.handler import item_handler, url_handler, claimant_handler
from core_layer.model.item_model import Item
from core_layer.db_handler import Session


def test_prepare_and_store_urls():
    with Session() as session:
        str_urls = ["https://smopo.ch/zehntausende-als-falsche-coronatote-deklariert/"]

        item = Item()
        item = item_handler.create_item(item, session)

        url_handler.prepare_and_store_urls(item, str_urls, session)
        for str_url in str_urls:
            url = verify_and_get_url(item, str_url, session)
            assert url.unsafe is None

        assert item.status != 'Unsafe'


def test_prepare_and_store_urls_with_unsafe_items():
    with Session() as session:
        str_urls = ["http://testsafebrowsing.appspot.com/s/malware.html"]

        item = Item()
        item = item_handler.create_item(item, session)

        url_handler.prepare_and_store_urls(item, str_urls, session)
        for str_url in str_urls:
            url = verify_and_get_url(item, str_url, session)
            assert url.unsafe is not None

        assert item.status == 'Unsafe'

def test_prepare_and_store_urls_multiply_urls():
    with Session() as session:
        str_urls = ["https://smopo.ch/zehntausende-als-falsche-coronatote-deklariert/", "https://www.google.de/" ]

        item = Item()
        item = item_handler.create_item(item, session)

        url_handler.prepare_and_store_urls(item, str_urls, session)
        for str_url in str_urls:
            url = verify_and_get_url(item, str_url, session)
            assert url.unsafe is None

        assert item.status != 'Unsafe'

def test_prepare_and_store_urls_multiply_urls_with_unsafe_items():
    with Session() as session:
        str_urls = ["http://testsafebrowsing.appspot.com/s/phishing.html",
                    "https://www.google.de/" ]

        item = Item()
        item = item_handler.create_item(item, session)

        url_handler.prepare_and_store_urls(item, str_urls, session)
        for str_url in str_urls:
            verify_and_get_url(item, str_url, session)

        assert item.status == 'Unsafe'

def test_prepare_and_store_urls_for_localhost_url():
    with Session() as session:
        str_urls = ["http://LOCALHOST/utes-moma-127-8-altmaier-will-haertere-strafen-bei-verstoessen-gegen-die-corona-regeln/",
                    "http://127.0.0.1/utes-moma-127-8-altmaier-will-haertere-strafen-bei-verstoessen-gegen-die-corona-regeln/"]

        item = Item()
        item = item_handler.create_item(item, session)

        url_handler.prepare_and_store_urls(item, str_urls, session)
        assert item.urls == []
        assert item.status != 'Unsafe'

def test_prepare_and_store_urls_localhost_url_skipped():
    with Session() as session:
        str_urls = ["http://localhost:8080/index.html", "https://www.google.de/" ]

        item = Item()
        item = item_handler.create_item(item, session)

        url_handler.prepare_and_store_urls(item, str_urls, session)
        assert len(item.urls) == 1
        for str_url in ["https://www.google.de/"]:
            verify_and_get_url(item, str_url, session)

        assert item.status != 'Unsafe'

def verify_and_get_url(item, str_url, session):
    url = url_handler.get_url_by_content(str_url, session)
    itemurl = url_handler.get_itemurl_by_url_and_item_id(url.id, item.id, session)
    domain = urlparse(str_url).hostname
    claimant = claimant_handler.get_claimant_by_name(domain, session)
    assert url.url == str_url
    assert itemurl.id is not None
    assert claimant.claimant == domain
    assert url.claimant_id is not None
    return url
