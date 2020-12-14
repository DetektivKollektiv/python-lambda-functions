from core_layer.connection_handler import get_db_session
from core_layer.model.sentiment_model import Sentiment, ItemSentiment


def get_sentiment_by_content(content, is_test, session):
    """Returns the sentiment with the specified content from the database

        Returns
        ------
        sentiment: Sentiment
            The sentiment of an item
        Null, if no sentiment was found
        """
    session = get_db_session(is_test, session)
    sentiment = session.query(Sentiment).filter(
        Sentiment.sentiment == content).first()
    if sentiment is None:
        raise Exception("No sentiment found.")
    return sentiment


def get_itemsentiment_by_sentiment_and_item_id(sentiment_id, item_id, is_test, session):
    """Returns the itemsentiment for an item and sentiment

        Returns
        ------
        itemsentiment: ItemSentiment
        Null, if no itemsentiment was found
    """
    session = get_db_session(is_test, session)
    itemsentiment = session.query(ItemSentiment).filter(ItemSentiment.sentiment_id == sentiment_id,
                                                        ItemSentiment.item_id == item_id).first()
    if itemsentiment is None:
        raise Exception("No Item Sentiment found.")
    return itemsentiment
