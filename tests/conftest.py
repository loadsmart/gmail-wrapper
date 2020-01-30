import json

import pytest

from gmail_wrapper import GmailClient
from tests.utils import make_gmail_client


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
    return {"id": "123AAB", "internalDate": "1566398665"}


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
                {"name": "Message-ID", "value": "<BY5PR15MB353717D866FC27FEE4DB4EC7F77E0@BY5PR15MB3537.namprd15.prod.outlook.com>"},
            ],
            "parts": [
                {
                    "body": {
                        "data": "I am Dr. Bakare Tunde, the cousin of Nigerian Astronaut, Air Force Major Abacha Tunde. He was the first African in space when he made a secret flight to the Salyut 6 space station in 1979.",
                        "attachmentId": "CCX456",
                        "size": 188,
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
                {
                    "body": {"size": 0},
                    "mimeType": "multipart/mixed",
                    "partId": "BB791",
                    "parts": [
                        {
                            "body": {"data": "someRandomDataHere", "size": 18},
                            "mimeType": "text/html",
                            "partId": "BB791.0",
                            "filename": "",
                        },
                        {
                            "body": {"attachmentId": "CCX458", "size": 95},
                            "mimeType": "application/pdf",
                            "partId": "BB791.1",
                            "filename": "tigers.pdf",
                        }
                    ],
                },
            ],
        },
        "snippet": "I am Dr. Bakare Tunde, the cousin of Nigerian Astronaut, Air Force Major Abacha Tunde.",
        "sizeEstimate": 361,
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


@pytest.fixture
def client(mocker):
    mocker.patch(
        "gmail_wrapper.client.GmailClient._make_client",
        return_value=make_gmail_client(mocker),
    )
    return GmailClient(email="foo@bar.com", secrets_json_string="{}")
