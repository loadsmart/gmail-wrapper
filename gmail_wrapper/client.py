import base64
import json
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
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

    def __init__(self, email, secrets_json_string, scopes=None):
        self.email = email
        self._client = self._make_client(secrets_json_string, scopes)

    def _make_client(self, secrets_json_string, scopes):
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
        return discovery.build("gmail", "v1", credentials=credentials)

    def _messages_resource(self):
        return self._client.users().messages()

    def get_raw_messages(self, query="", limit=None):
        return (
            self._messages_resource()
            .list(userId=self.email, q=query, maxResults=limit)
            .execute()
        )

    def get_messages(self, query="", limit=None):
        raw_messages = self.get_raw_messages(query, limit)

        if "messages" not in raw_messages:
            return []

        return [Message(self, raw_message) for raw_message in raw_messages["messages"]]

    def get_raw_message(self, id):
        return self._messages_resource().get(userId=self.email, id=id).execute()

    def get_message(self, id):
        raw_message = self.get_raw_message(id)

        return Message(self, raw_message)

    def modify_raw_message(self, id, add_labels=None, remove_labels=None):
        return (
            self._messages_resource()
            .modify(
                userId=self.email,
                id=id,
                body={
                    "addLabelIds": add_labels if add_labels else [],
                    "removeLabelIds": remove_labels if remove_labels else [],
                },
            )
            .execute()
        )

    def modify_message(self, id, add_labels=None, remove_labels=None):
        raw_modified_message = self.modify_raw_message(id, add_labels, remove_labels)

        return Message(self, raw_modified_message)

    def get_raw_attachment_body(self, id, message_id):
        return (
            self._messages_resource()
            .attachments()
            .get(userId=self.email, id=id, messageId=message_id)
            .execute()
        )

    def get_attachment_body(self, id, message_id):
        raw_attachment_body = self.get_raw_attachment_body(id, message_id)

        return AttachmentBody(raw_attachment_body)

    def _make_sendable_message(self, subject, html_content, to, cc, bcc):
        message = MIMEText(html_content, "html")
        message["subject"] = subject
        message["from"] = self.email
        message["to"] = to
        message["cc"] = ",".join(cc)
        message["bcc"] = ",".join(bcc)
        return {"raw": base64.urlsafe_b64encode(bytes(message.as_string(), "utf-8"))}

    def send_raw(self, subject, html_content, to, cc=None, bcc=None):
        sendable = self._make_sendable_message(
            subject, html_content, to, cc if cc else [], bcc if bcc else []
        )

        return self._messages_resource().send(sendable).execute()

    def send(self, subject, html_content, to, cc=None, bcc=None):
        raw_sent_message = self.send_raw(subject, html_content, to, cc, bcc)

        return Message(self, raw_sent_message)
