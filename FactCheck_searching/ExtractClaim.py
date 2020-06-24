import re
import logging
import urllib.request
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
            item_content = str(event['item']['content'].encode(errors="ignore"))
        else:
            logger.error("The item has no content!")
            raise Exception('Please provide an item with content!')
        if 'id' in event['item']:
            item_id = str(event['item']['id'].encode(errors="ignore"))
        else:
            logger.error("The item has no ID!")
            raise Exception('Please provide an item with an ID!')
    else:
        logger.error("There is no item!")
        raise Exception('Please provide an item!')

    # extract all urls from item_content
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', item_content)
    # titles contains as first entry a placeholder for item_content
    titles = ["", ]
    # text contains as first entry a placeholder for item_content
    text = [item_content, ]
    allText = item_content

    # open all urls and extract the paragraphs
    for url in urls:
        content = urllib.request.urlopen(url)
        read_content = content.read()

        soup = BeautifulSoup(read_content, 'html.parser')
        titles.append(soup.find('title').text)  # get the title of the web page
        pAll = soup.find_all('p')  # get all paragraphs of the web page
        paragraphs = ''

        # concatenate all paragraphs for each url
        for t in pAll:
            paragraphs += '{} '.format(t.text)
        text.append(paragraphs)
        allText += paragraphs

    # add as first entry a placeholder for item_content
    urls.insert(0, "")

    return {
        "urls": urls,
        "titles": titles,
        "text": text,
        "concatenation": {
            "Text": allText
        }
    }
