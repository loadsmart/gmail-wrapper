import json

import pytest


@pytest.fixture
def secrets_string():
    return json.dumps(
        {
            "web": {
                "redirect_uris": ["https://foo-bar.loadsmart.io"],
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "client_id": "foo-app.apps.googleusercontent.com",
                "client_secret": "JohnDoeCries",
                "project_id": "my-project",
                "refresh_token": "MyRefresh",
            }
        }
    )


@pytest.fixture
def raw_incomplete_message():
    return {"id": 123, "internalDate": "1566398665"}


@pytest.fixture
def raw_complete_message():
    return {
        "internalDate": "1566398665",
        "historyId": 123,
        "payload": {
            "body": {
                "data": "I am caught up in a meeting. Can you run an urgent errand for me?",
                "attachmentId": "CCX456",
                "size": 65,
            },
            "mimeType": "text/plain",
            "partId": "BB789",
            "filename": "",
            "headers": [
                {"name": "To", "value": "foo@loadsmart.com"},
                {"name": "From", "value": "john@doe.com"},
                {"name": "Subject", "value": "Urgent errand"},
            ],
            "parts": [
                {
                    "body": {
                        "data": "I am caught up in a meeting. Can you run an urgent errand for me?",
                        "attachmentId": "CCX456",
                        "size": 65,
                    },
                    "mimeType": "text/plain",
                    "partId": "BB789",
                    "filename": "",
                },
                {
                    "body": {"data": "", "attachmentId": "CCX457", "size": 60},
                    "mimeType": "text/plain",
                    "partId": "BB790",
                    "filename": "fox.txt",
                },
            ],
        },
        "snippet": "I am caught up in a meeting. Can you run an urgent errand for me?",
        "sizeEstimate": 125,
        "threadId": "AA121212",
        "labelIds": ["phishing"],
        "id": "123AAB",
    }


@pytest.fixture
def raw_attachment_body():
    return {
        "data": "VGhlIFF1aWNrIEJyb3duIEZveCBKdW1wcyBPdmVyIFRoZSBMYXp5IERvZw==",
        "attachmentId": "CCX457",
        "size": 60,
    }
