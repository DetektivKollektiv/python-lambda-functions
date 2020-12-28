import re
import logging
import urllib.request
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def extract_claim(event, context):
    """extracts claim from item content
    Parameters
    ----------
    event: dict, required
        item
    context: object, required
        Lambda Context runtime methods and attributes
    Returns
    ------
    urls: list of urls in item, first entry is "" for item content
    titles: list of url titles, first entry is "" for item content
    text: list of url paragraphs, first entry is item content
    concatenation: Text: concatenation of all paragraphs
    """

    logger.info('Calling extract_claim with event')
    logger.info(event)

    # Use UTF-8 encoding for comprehend
    if 'item' in event:
        if 'content' in event['item']:
            item_content = str(event['item']['content'])
        else:
            logger.error("The item has no content!")
            raise Exception('Please provide an item with content!')
        if 'id' not in event['item']:
            logger.error("The item has no ID!")
            raise Exception('Please provide an item with an ID!')
    else:
        logger.error("There is no item!")
        raise Exception('Please provide an item!')

    # extract all urls from item_content
    urls = re.findall(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', item_content)
    # remove urls from item_content
    for url in urls:
        item_content = item_content.replace(url, '')

    # titles contains as first entry a placeholder for item_content
    # titles = ["", ]
    title = ""
    # text contains as first entry a placeholder for item_content
    # text = [item_content, ]
    allText = item_content+' '

    # open all urls and extract the paragraphs
    for url in urls:
        # do not accept urls referencing localhost
        try:
            if re.search('127\.', url) or re.search('localhost', url, re.IGNORECASE):
                continue
        except (AttributeError, TypeError):
            continue
        # set headers for a web browser
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        }
        resp = requests.get(url, headers=headers)
        read_content = resp.content
        read_content_hidden = read_content.replace(b'<!--', b'')
        soup = BeautifulSoup(read_content_hidden, 'html.parser')
        # get the title of the web page
        titles = soup.find_all('title')  
        title = ""
        if len(titles) > 0:
            title = '{} '.format(titles[0].text)
        # get the description of the web page
        description = soup.find("meta",  {"name":"description"})
        page_description = ""
        if description:
            page_description = description["content"]
        # get all paragraphs of the web page
        pAll = soup.find_all('p')
        paragraphs = ''

        # concatenate all paragraphs for each url
        for t in pAll:
            paragraphs += '{} '.format(t.text)
            # As more paragraphs are appended as higher is the probability that the paragraphs do not belong to the
            # main article
            if len(paragraphs) > 50:
                break
        # use only title as claim, maybe this enhances the quality of entities and phrases
        allText += title + "\n" + page_description
        if len(allText) < 50:
            allText += paragraphs

    if len(allText) >= 4800:
        allText = allText[:4799]

    return {
        "urls": urls,
        "title": title,
        # "text": text,
        "concatenation": {
            "Text": allText
        }
    }
