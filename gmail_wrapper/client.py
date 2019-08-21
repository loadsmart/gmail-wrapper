import json

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient import discovery

from gmail_wrapper.entities import Message, AttachmentBody


class GmailClient:
    SCOPE_LABELS = "https://www.googleapis.com/auth/gmail.labels"
    SCOPE_SEND = "https://www.googleapis.com/auth/gmail.send"
    SCOPE_READONLY = "https://www.googleapis.com/auth/gmail.readonly"
    SCOPE_COMPOSE = "https://www.googleapis.com/auth/gmail.compose"
    SCOPE_INSERT = "https://www.googleapis.com/auth/gmail.insert"
    SCOPE_MODIFY = "https://www.googleapis.com/auth/gmail.modify"
    SCOPE_METADATA = "https://www.googleapis.com/auth/gmail.metadata"

    def __init__(self, email, secrets_json_string, scopes = None):
        google_secrets_data = json.loads(secrets_json_string)["web"]
        credentials = Credentials(
            None,
            refresh_token=google_secrets_data["refresh_token"],
            client_id=google_secrets_data["client_id"],
            client_secret=google_secrets_data["client_secret"],
            token_uri=google_secrets_data["token_uri"],
            scopes=scopes if scopes else [GmailClient.SCOPE_READONLY],
        )
        credentials.refresh(Request())
        self._client = discovery.build("gmail", "v1", credentials=credentials)
        self.email = email

    def _make_query(
        self,
        from_email=None,
        with_subject=None,
        with_attachment_type=None,
        with_labels=None,
        without_labels=None,
    ):
        query = []
        if from_email:
            query.append("from:{}".format(from_email))
        if with_subject:
            query.append("subject:{}".format(with_subject))
        if with_attachment_type:
            query.append("filename:{}".format(with_attachment_type))
        for label in with_labels if with_labels else []:
            query.append("label:{}".format(label))
        for label in without_labels if without_labels else []:
            query.append("-label:{}".format(label))

        return query

    def _messages_resource(self):
        return self._client.users().messages()

    def get_messages(
        self,
        from_email=None,
        with_subject=None,
        with_attachment_type=None,
        with_labels=None,
        without_labels=None,
        limit=None,
        as_raw=False,
    ):
        query = self._make_query(
            from_email, with_subject, with_attachment_type, with_labels, without_labels
        )
        raw_messages = (
            self._messages_resource()
            .list(userId=self.email, q=query, maxResults=limit)
            .execute()
        )

        if as_raw:
            return raw_messages

        if "messages" not in raw_messages:
            return []

        return [Message(self, raw_message) for raw_message in raw_messages["messages"]]

    def get_message(self, id, as_raw=False):
        raw_message = self._messages_resource().get(userId=self.email, id=id).execute()

        if as_raw:
            return raw_message

        return Message(self, raw_message)

    def get_attachment_body(self, id, message_id, as_raw=False):
        raw_attachment_body = (
            self._messages_resource()
            .attachments()
            .get(userId=self.email, id=id, messageId=message_id)
            .execute()
        )

        if as_raw:
            return raw_attachment_body

        return AttachmentBody(raw_attachment_body)
