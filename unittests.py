import unittest
import uuid
import json
from StringIO import StringIO

from falcon import testing
from falcon import HTTPError
import mock

import trackerapp
from trackerapp import ItemResource, parse_item, is_valid_cart_id, save_item


class ItemTestCase(testing.TestCase):

    def setUp(self):
        super(ItemTestCase, self).setUp()

        self.app = trackerapp.create()


class ItemResourceTest(ItemTestCase):
    
    @mock.patch('trackerapp.save_item_task')
    @mock.patch('trackerapp.parse_item')
    def test_if_cart_id_in_request_then_new_cart_set(self, m_parse_item, m_save_item_task):
        m_parse_item.return_value = {
            'external_id': 'some_valid_id'}
        m_request = mock.Mock()
        m_request.cookies = {}
        m_response = mock.Mock()
        m_ItemResource = mock.Mock(spec=ItemResource)
        ItemResource.on_post(m_ItemResource, m_request, m_response)
        resp = json.loads(m_response.body)
        self.assertTrue(resp.get('new_cart'))

    @mock.patch('trackerapp.save_item_task')
    @mock.patch('trackerapp.parse_item')
    def test_if_no_cart_id_in_request_then_new_cart_set(self, m_parse_item, m_save_item_task):
        m_parse_item.return_value = {
            'external_id': 'some_valid_id',
            'cart_id': str(uuid.uuid4())}
        m_request = mock.Mock()
        m_request.cookies = {}
        m_response = mock.Mock()
        m_ItemResource = mock.Mock(spec=ItemResource)
        ItemResource.on_post(m_ItemResource, m_request, m_response)
        resp = json.loads(m_response.body)
        self.assertFalse(resp.get('new_cart'))
    

class ParseItemTest(ItemTestCase):

    def test_if_no_content_raises_http_error(self):
        mock_request = mock.Mock()
        mock_request.content_length = 0
        def call_parse_item():
            parse_item(mock_request)
        self.assertRaises(HTTPError, call_parse_item)

    def test_if_invalid_json_raises_http_error(self):
        mock_request = mock.Mock()
        mock_request.content_length = 1
        mock_request.stream = StringIO('invalid json blah')
        try:
            parse_item(mock_request)
        except HTTPError as e:
            error_message = e.status
        self.assertIn('invalid JSON', error_message)

    def test_if_invalid_cart_raises_http_error(self):
        mock_request = mock.Mock()
        mock_request.content_length = 1
        mock_request.stream = StringIO('{"cart_id": "tempura soba"}')
        try:
            parse_item(mock_request)
        except HTTPError as e:
            error_message = e.status
        self.assertIn('invalid cart_id', error_message)

    def test_if_no_external_id_raises_http_error(self):
        mock_request = mock.Mock()
        mock_request.content_length = 1
        mock_request.cookies = {}
        mock_request.stream = StringIO('{"tempura soba": "oishi"}')
        try:
            parse_item(mock_request)
        except HTTPError as e:
            error_message = e.status
        self.assertIn('external_id is required', error_message)
        
    def test_if_valid_item_returns_valid_item(self):
        mock_request = mock.Mock()
        mock_request.content_length = 1
        mock_request.cookies = {}
        valid_item = {"external_id": "a5wEet1DftW"}
        mock_request.stream = StringIO(json.dumps(valid_item))
        return_item = parse_item(mock_request)
        self.assertEqual(valid_item, return_item)


class IsValidCartIdTest(ItemTestCase):

    def test_if_invalid_uuid_returns_false(self):
        cart_id = 'an invalid uuid'
        self.assertFalse(is_valid_cart_id(cart_id))

    def test_if_valid_uuid_returns_true(self):
        cart_id = str(uuid.uuid4())
        self.assertTrue(is_valid_cart_id(cart_id))


class SaveItemTest(ItemTestCase):

    def test_if_new_cart_in_item_calls_add_method_twice(self):
        item = {
            'new_cart': True,
            'cart_id': 'some_id'
            }
        mock_session = mock.Mock()
        save_item(item, mock_session)
        self.assertEqual(mock_session.add.call_count, 2)

    def test_if_no_new_cart_in_item_calls_add_method_once(self):
        item = {
            'cart_id': 'some_id'
            }
        mock_session = mock.Mock()
        save_item(item, mock_session)
        self.assertEqual(mock_session.add.call_count, 1)

    def test_if_valid_item_calls_commit_once(self):
        item = {
            'new_cart': True,
            'cart_id': 'some_id'
            }
        mock_session = mock.Mock()
        save_item(item, mock_session)
        self.assertEqual(mock_session.commit.call_count, 1)
        

def main():
    unittest.main()

if __name__ == '__main__':
    main()
