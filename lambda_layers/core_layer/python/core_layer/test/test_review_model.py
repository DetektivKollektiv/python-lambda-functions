from core_layer.db_handler import Session
from core_layer.model.review_model import Review
from core_layer.model.user_model import User
from core_layer.model.item_model import Item
from core_layer.model.tag_model import Tag, ItemTag
from core_layer.model import Level
from uuid import uuid4


def test_tags_to_dict():
    with Session() as session:
        user = User(id=str(uuid4()), name='user1')
        level = Level(id=1, description='beginner')

        item = Item(id=str(uuid4()), content='item')

        tag1 = Tag(id=str(uuid4()), tag='tag1')
        tag2 = Tag(id=str(uuid4()), tag='tag2')
        tag3 = Tag(id=str(uuid4()), tag='tag3')

        review = Review()
        review.id = str(uuid4())
        review.is_peer_review = False
        review.user_id = user.id
        review.item_id = item.id

        session.add_all([user, item, tag1, tag2, tag3, review, level])
        session.commit()

        review_dict = review.to_dict(with_tags=True, with_user=True)
        assert 'tags' in review_dict
        assert len(review_dict['tags']) == 0

        item_tag1 = ItemTag(id=str(uuid4()), item_id=item.id, tag_id=tag1.id,
                            review_id=review.id)
        session.add(item_tag1)
        session.commit()
        session.refresh(review)

        review_dict = review.to_dict(with_tags=True, with_user=True)
        assert 'tags' in review_dict
        assert len(review_dict['tags']) == 1
        assert review_dict['tags'][0] == 'tag1'

        item_tag2 = ItemTag(id=str(uuid4()), item_id=item.id, tag_id=tag2.id,
                            review_id=review.id)
        session.add(item_tag2)
        session.commit()
        session.refresh(review)

        review_dict = review.to_dict(with_tags=True, with_user=True)
        assert 'tags' in review_dict
        assert len(review_dict['tags']) == 2
        assert 'tag2' in review_dict['tags']

        session.delete(item_tag1)
        session.commit()
        session.refresh(review)
        review_dict = review.to_dict(with_tags=True, with_user=True)
        assert 'tags' in review_dict
        assert len(review_dict['tags']) == 1
        assert review_dict['tags'][0] == 'tag2'
