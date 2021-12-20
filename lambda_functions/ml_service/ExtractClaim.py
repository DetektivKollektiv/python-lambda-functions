import logging
import requests
from bs4 import BeautifulSoup
from core_layer.handler import item_handler
from core_layer.db_handler import Session

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
    titles: list of url titles, first entry is "" for item content
    text: list of url paragraphs, first entry is item content
    concatenation: Text: concatenation of all paragraphs
    """

    logger.info('Calling extract_claim with event')
    logger.info(event)
    
    with Session() as session:
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
                # extract item
                item_id = event['item']['id']
                item = item_handler.get_item_by_id(item_id, session)
                if item is None:
                    raise Exception('Couldn\'t load item with id: ' + item_id)
        else:
            logger.error("There is no item!")
            raise Exception('Please provide an item!')   

        # remove urls from item_content        
        for itemUrl in item.urls:
            item_content = item_content.replace(itemUrl.url.url, '')

        # titles contains as first entry a placeholder for item_content
        # titles = ["", ]
        title = ""
        # text contains as first entry a placeholder for item_content
        # text = [item_content, ]
        allText = item_content

        # open all urls and extract the paragraphs+
        first_title = ""
        for itemUrl in item.urls:
            url = itemUrl.url.url
            # set headers for a web browser
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
            }
            resp = requests.get(url, headers=headers)
            read_content = resp.content
            # read_content_hidden = read_content.replace(b'<!--', b'<!')
            soup = BeautifulSoup(read_content, 'html.parser')
            # get the title of the web page
            titles = soup.find_all('title')
            title = ""
            if len(titles) > 0:
                title = '{} '.format(titles[0].text)
            # get the description of the web page
            description = soup.find("meta", {"name": "description"})
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

            # use the title of the first URL as "title" attribute later
            if first_title == "":
                first_title = title
            # use only title as claim, maybe this enhances the quality of entities and phrases
            allText += "\n" + title
            if len(allText) < 50:
                allText += "\n" + page_description
            if len(allText) < 50:
                allText += "\n" + paragraphs

        if len(allText) >= 4800:
            allText = allText[:4799]

        return {
            "title": first_title,
            # "text": text,
            "concatenation": {
                "Text": allText
            }
        }
