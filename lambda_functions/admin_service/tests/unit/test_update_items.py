from uuid import uuid4
from core_layer.model import Item
from core_layer.db_handler import Session
from admin_service.update_item import update_item


def get_item():
    item = Item()
    item.id = str(uuid4())
    item.content = "Item Content"
    item.language = "de"
    return item
    

def get_event(item_id, attribute, value):
    return {
        'pathParameters': {
            'item_id': item_id
        },
        'body': {
            attribute: value
        }
    }


def test_update_item():
    with Session() as session:

        item = get_item()
        session.add(item)
        session.commit()
        item = session.query(Item).one()
        
        assert item.status == 'unconfirmed'       
        item_count = session.query(Item).count()
        assert item_count == 1      
              
        # good request 1, updating status
        event = get_event(item.id, 'status', 'open')
        response = update_item(event, None)
        item = session.query(Item).one()
        assert item.status == 'open'
        assert item.language == 'de'
        assert response['statusCode'] == 200

        # good request 2, updating language = "en"
        event = get_event(item.id, 'language', 'en')
        response = update_item(event, None)
        item = session.query(Item).one()
        assert item.language == 'en'
                
        # item does not exist
        event = get_event('NotAnItemId', 'status', 'open')
        response = update_item(event, None)
        assert response['statusCode'] == 404
         
        # bad request
        event = get_event(item.id, 'NotAnItemAttribute', 'open')
        response = update_item(event, None)
        item = session.query(Item).one()
        assert response['statusCode'] == 400    
    