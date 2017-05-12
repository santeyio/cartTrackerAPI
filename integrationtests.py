import uuid
import unittest
import mock
import json

from falcon import testing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import trackerapp
from data.models import Base

class TrackerTestCase(testing.TestCase):

    def setUp(self):
        super(TrackerTestCase, self).setUp()
        
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)

        self.app = trackerapp.create()


class TrackerTest(TrackerTestCase):

    def test_if_tracker(self):
        req = trackerapp.ItemResource()
        self.failUnless(req)

    def test_if_post_returns_json(self):
        response = self.simulate_post('/api/v1/item')
        self.failUnless(response.json)

    @mock.patch('trackerapp.Session')
    @mock.patch('trackerapp.save_item_task')        
    def test_if_post_creates_cart_id_if_none_provided(self, m_save_item_task, m_session):
        m_save_item_task.delay = trackerapp.save_item
        m_session.return_value = self.session()
        request = {"external_id": "123123",
                    "name": "Peeps",
                    "value": 200}
        response = self.simulate_post('/api/v1/item', body=json.dumps(request))
        self.assertIn('cart_id', response.json)

    @mock.patch('trackerapp.Session')
    @mock.patch('trackerapp.save_item_task')        
    def test_if_post_returns_correct_cart_id_if_provided(self, m_save_item_task, m_session):
        m_save_item_task.delay = trackerapp.save_item
        m_session.return_value = self.session()
        request = {"cart_id": str(uuid.uuid4()),
                    "external_id": "321321",
                    "name": "Malt Eggs",
                    "value": 300}
        response = self.simulate_post('/api/v1/item', body=json.dumps(request))
        self.assertEqual(response.json.get('cart_id'), request.get('cart_id'))

    @mock.patch('trackerapp.Session')
    @mock.patch('trackerapp.save_item_task')        
    def test_if_post_generates_unique_new_cart_ids(self, m_save_item_task, m_session):
        m_save_item_task.delay = trackerapp.save_item
        m_session.return_value = self.session()
        request = {"external_id": "123123",
                    "name": "Twizzlers",
                    "value": 400}
        response1 = self.simulate_post('/api/v1/item', body=json.dumps(request))
        response2 = self.simulate_post('/api/v1/item', body=json.dumps(request))
        self.assertNotEqual(response1.json['cart_id'], response2.json['cart_id'])
    
    @mock.patch('trackerapp.Session')
    @mock.patch('trackerapp.save_item_task')        
    def test_if_error_on_no_external_id(self, m_save_item_task, m_session):
        m_save_item_task.delay = trackerapp.save_item
        m_session.return_value = self.session()
        request = {"something": "123123",
                    "name": "Nabeyaki Udon",
                    "value": 12200}
        response = self.simulate_post('/api/v1/item', body=json.dumps(request))
        error = 'external_id is a mandatory field'
        self.failUnless(response.status == '400 external_id is required')
        
    @mock.patch('trackerapp.Session')
    @mock.patch('trackerapp.save_item_task')        
    def test_if_success_on_creating_new_cart(self, m_save_item_task, m_session):
        m_save_item_task.delay = trackerapp.save_item
        m_session.return_value = self.session()
        request = {"external_id": "123123",
                    "name": "Pizaz",
                    "value": 22200}
        response = self.simulate_post('/api/v1/item', body=json.dumps(request))
        self.failUnless(response.status == '200 OK')
        self.failUnless('cart_id' in response.json)

    @mock.patch('trackerapp.Session')
    @mock.patch('trackerapp.save_item_task')        
    def test_if_error_on_incorrect_cart_id(self, m_save_item_task, m_session):
        m_save_item_task.delay = trackerapp.save_item
        m_session.return_value = self.session()
        request = {"external_id": "nonexistentid",
                   "cart_id": "someid",
                   "name": "Pizzaaa!!",
                   "value": 300000}
        response = self.simulate_post('/api/v1/item', body=json.dumps(request))
        self.failUnless(response.status == '400 invalid cart_id')

    @mock.patch('trackerapp.Session')
    @mock.patch('trackerapp.save_item_task')        
    def test_if_success_on_updating_cart(self, m_save_item_task, m_session):
        m_save_item_task.delay = trackerapp.save_item
        m_session.return_value = self.session()
        request = {"external_id": "123123",
                    "name": "Cheetos",
                    "value": 200}
        response = self.simulate_post('/api/v1/item', body=json.dumps(request))
        request2 = {"external_id": "44444444",
                    "cart_id": response.json['cart_id'],
                    "name": "Jenkyness",
                    "value": 223400}
        response2 = self.simulate_post('/api/v1/item', body=json.dumps(request2))
        self.failUnless(response2.status == '200 OK')


def main():
    unittest.main()

if __name__ == '__main__':
    main()
