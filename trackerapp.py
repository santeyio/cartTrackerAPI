import json
import uuid

import falcon
from falcon import HTTPError
from celery import Celery

from data.models import Cart, Item
from data.db import Session

CELERY_APP = Celery('trackerapp', broker='pyamqp://guest@localhost')


class ItemResource(object):
    """ Falcon API Resource for tracking carts """

    def on_get(self, req, resp):
        """ GET not allowed """
        raise HTTPError(status="405 GET not allowed")

    def on_post(self, req, resp):
        """ Handle new Items and Item updates """
        item = parse_item(req)
        cart_id = item.get('cart_id', req.cookies.get('cart_id'))
        if not cart_id:
            cart_id = str(uuid.uuid4())
            item['new_cart'] = True
        item['cart_id'] = cart_id
        save_item_task.delay(item)
        resp.set_cookie('cart_id', item.get('cart_id'))
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.body = json.dumps(item)


def parse_item(req):
    """
    Do some validation on the request and decode the json
    :param req: a falcon request object
    :return: item dictionary
    """
    if not req.content_length:
        raise HTTPError(status="400 no content found")
    try:
        item = json.load(req.stream)
    except ValueError:
        raise HTTPError(status="400 invalid JSON")
    if 'cart_id' in item and not is_valid_cart_id(item.get('cart_id')):
        raise HTTPError(status="400 invalid cart_id")
    if 'cart_id' in req.cookies and not is_valid_cart_id(req.cookies.get('cart_id')):
        raise HTTPError(status="400 invalid cart_id")
    if 'external_id' not in item:
        raise HTTPError(status="400 external_id is required")
    return item


def is_valid_cart_id(cart_id):
    """
    Make sure that a cart_id is a valid UUID
    :param cart_id: string 
    :return: boolean
    """
    try:
        uuid.UUID(cart_id)
    except ValueError:
        return False
    return True


@CELERY_APP.task
def save_item_task(item):
    """ Delegate database inserts to celery """
    save_item(item)


def save_item(item, session=None):
    """
    Insert an item into the database
    :param item: item dictionary
    :param session: session object (testing util)
    """
    if not session:
        session = Session()
    if item.get('new_cart'):
        session.add(Cart(id=item.get('cart_id')))
    session.add(Item(
        external_id=item.get('external_id'),
        cart_id=item.get('cart_id'),
        name=item.get('name'),
        value=item.get('value')
    ))
    # errors should be caught in celery logs
    session.commit()


def create():
    """ Returns a falcon.API() object with an item resource """
    return APP


APP = falcon.API()
TRACKER = ItemResource()
APP.add_route('/api/v1/item', TRACKER)
