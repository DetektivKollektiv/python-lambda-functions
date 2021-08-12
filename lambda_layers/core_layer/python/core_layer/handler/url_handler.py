from uuid import uuid4
import re
from core_layer.model import URL, ItemURL, Item, Claimant

from core_layer.db_handler import Session, update_object
from . import url_threatcheck, claimant_handler
from urllib.parse import urlparse
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_url_by_content(content, session):
    """Returns an url with the specified content from the database

        Returns
        ------
        url: URL
            An url referenced in an item
        Null, if no url was found
        """
    url = session.query(URL).filter(URL.url == content).first()
    if url is None:
        raise Exception("No url found.")
    return url


def get_itemurl_by_url_and_item_id(url_id, item_id, session):
    """Returns the itemurl for an item and url

        Returns
        ------
        itemurl: ItemURL
        Null, if no itemurl was found
        """
    itemurl = session.query(ItemURL).filter(ItemURL.url_id == url_id,
                                            ItemURL.item_id == item_id).first()
    if itemurl is None:
        raise Exception("No ItemURL found.")
    return itemurl

def prepare_and_store_urls(item: Item, urls:[], session):
    """ prepares the urls (extract the claimant and perform threat check) and stores urls in the item

    Parameters
    ----------
    item:
        Item, required

    urls:
        string [], required

    session:
        Session, required

    Returns
    ------
        item:
            Item

    """
    unsafe_urls = False
    # Store all urls referenced in the item
    for str_url in urls:
        # do not accept urls referencing localhost
        try:
            if str_url == "" or re.search('127\.', str_url) or re.search('localhost', str_url, re.IGNORECASE):
                continue
        except (AttributeError, TypeError):
            continue

        # store claimant derived from url
        domain = urlparse(str_url).hostname
        claimant = Claimant()
        # claimant already exists?
        try:
            claimant = claimant_handler.get_claimant_by_name(domain, session)
        except Exception:
            # store claimant in database
            claimant.id = str(uuid4())
            claimant.claimant = domain
            try:
                update_object(claimant, session)
            except Exception as e:
                logger.error(
                    "Could not store claimant. Exception: %s", e, exc_info=True)
                raise

        url = URL()
        # get or create URL item
        try:
            url = get_url_by_content(str_url, session)
        except Exception:
            # create and store url in database
            url.id = str(uuid4())
            url.url = str_url
            url.claimant_id = claimant.id
            ## check the URL for malware etc.
            url.unsafe = url_threatcheck.threatcheck(str_url);
            if (url.unsafe != None):
                unsafe_urls = True

            try:
                update_object(url, session)
            except Exception as e:
                logger.error("Could not store urls. Exception: %s",
                             e, exc_info=True)
                raise
        itemurl =  ItemURL()
        # get or create itemUrl
        try:
            itemurl = get_itemurl_by_url_and_item_id(url.id, item.id, session)
        except Exception:
            # store itemurl in database
            itemurl.id = str(uuid4())
            itemurl.item_id = item.id
            itemurl.url_id = url.id
            itemurl.unsafe = url.unsafe
            try:
                update_object(itemurl, session)
            except Exception as e:
                logger.error("Could not store itemurls. Exception: %s", e, exc_info=True)
                raise

    if unsafe_urls is True:
        item.status = 'Unsafe'
        update_object(item, session)

    return item