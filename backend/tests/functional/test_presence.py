"""
This file (test_profile.py) contains the functional tests which
test create profile and view profile.

"""
# pylint: disable = line-too-long, too-many-lines, no-name-in-module, import-error, multiple-imports, pointless-string-statement, wrong-import-order
from bson.objectid import ObjectId

import pytest
import os
import sys
from flask import jsonify, request, json
from datetime import datetime
import random
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
PARENT_ROOT = os.path.abspath(os.path.join(SITE_ROOT, os.pardir))
GRANDPAPA_ROOT = os.path.abspath(os.path.join(PARENT_ROOT, os.pardir))
sys.path.insert(0, GRANDPAPA_ROOT)
from project import create_app

profilename = "Profile B"


@pytest.fixture
def test_client():
    flask_app = create_app('test')
    flask_app.config['TESTING'] = True

    with flask_app.test_client() as testing_client:
        yield testing_client


class TestPool:

    def test_for_adding_presence_for_pool(self, test_client):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/addPresence' page is requested (POST)
        THEN check that request has email address
        """
        random_userid =random.randint(99, 999999)
        random_profileid = random.randint(99, 99999)
        data = {
            "profileName": profilename,
            "user_id": random_userid,
            "profile_id": random_profileid,
            "state": "PA",
            "zip": "19000",
            "city": "Philadelphia",
            "email": "test@test.com",
            "profileImg": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
            "first_name": "Test",
            "last_name": "User",
            "position": "Developer",
            "aboutMe": "Hello World",
            "education": [
                {
                    "school": "Drexel",
                    "degree": "MA",
                    "major": "SE",
                    "eduStartDate": "0001-01",
                    "eduEndDate": "0001-01",
                    "gpa": "3"
                }
            ],
            "experience": [
                {
                    "title": "Developer",
                    "company": "ABC",
                    "location": "PH",
                    "expStartDate": "0001-01",
                    "expEndDate": "0001-01"
                }
            ],
            "reviewed_by": [
                {
                    "reviewed_by":"",
                    "reviewed_on":"",
                    "status":""
                }
            ],
            "added_on": datetime.utcnow()
        }
        response = test_client.post(
            '/api/v1/addPresence/', data=json.dumps(data), headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        assert response != 'null'

    def test_for_validating_presence_existance(self, test_client):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/addPresence' page is requested (POST)
        THEN check that request has email address
        """
        data = {
            "profileName": profilename,
            "user_id": 1,
            "profile_id": 9,
            "state": "PA",
            "zip": "19000",
            "city": "Philadelphia",
            "email": "test@test.com",
            "profileImg": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",
            "first_name": "Test",
            "last_name": "User",
            "position": "Developer",
            "aboutMe": "Hello World",
            "education": [
                {
                    "school": "Drexel",
                    "degree": "MA",
                    "major": "SE",
                    "eduStartDate": "0001-01",
                    "eduEndDate": "0001-01",
                    "gpa": "3"
                }
            ],
            "experience": [
                {
                    "title": "Developer",
                    "company": "ABC",
                    "location": "PH",
                    "expStartDate": "0001-01",
                    "expEndDate": "0001-01"
                }
            ],
            "reviewed_by": [
                {
                    "reviewed_by":"",
                    "reviewed_on":"",
                    "status":""
                }
            ],
            "added_on": datetime.utcnow()
        }
        response = test_client.post(
            '/api/v1/addPresence/', data=json.dumps(data), headers={'Content-Type': 'application/json'})
        assert response.status_code == 403
        assert response.data == b'{"code":4,"error":"User presence already exists"}\n'


    def test_get_all_presence_to_be_reviewed(self, test_client):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/api/v1/getAllPresence/' page is requested (POST)
        THEN check that the response is valid
        """
        response = test_client.get('/api/v1/getAllPresence/7/', headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        assert response.data != b'{"code":4,"error":"No presence found"}\n'


    def test_save_presence_feedback(self, test_client):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/api/v1/getAllPresence/' page is requested (POST)
        THEN check that the response is valid
        """
        data =   {
            "profile_id":"9",
            "user_id":"1",
            "feedback" :{
                "reviewer_id": "4",
                "reviewed_on": "1122",
                "status":"rejected"
                }
        }
        response = test_client.patch('/api/v1/savePresenceReview/', data=json.dumps(data), headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        assert response.data != b'{"code":4,"error":"No presence found"}\n'

    def test_validating_save_presence_feedback(self, test_client):
        """
        GIVEN a Flask application configured for testing
        WHEN the '/api/v1/getAllPresence/' page is requested (POST)
        THEN check that the response is valid
        """
        data =   {
            "profile_id":"93",
            "user_id":"71",
            "feedback" :{
                "reviewer_id": "4",
                "reviewed_on": "1122",
                "status":"rejected"
                }
        }
        response = test_client.patch('/api/v1/savePresenceReview/', data=json.dumps(data), headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        assert response.data == b'{"code":4,"error":"User presence not found"}\n'
