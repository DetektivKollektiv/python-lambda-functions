import re
import logging
import urllib.request
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def extract_claim(event, context):
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

    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', item_content)

    content = urllib.request.urlopen(urls[0])
    read_content = content.read()

    soup = BeautifulSoup(read_content, 'html.parser')
    text = soup.find_all(text=True)
    title = soup.find('title').text  # get the title of the web page
    pAll = soup.find_all('p')  # get all paragraphs of the web page
    paragraphs = ''

    for t in pAll:
        paragraphs += '{} '.format(t.text)

    return title, paragraphs
