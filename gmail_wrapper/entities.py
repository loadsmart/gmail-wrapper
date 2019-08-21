import base64
from datetime import datetime


class AttachmentBody:
    def __init__(self, raw_body):
        self._raw = raw_body
        self._content = None

    @property
    def id(self):
        return self._raw.get("attachmentId")

    @property
    def size(self):
        return self._raw.get("size")

    @property
    def content(self):
        if not self._content:
            if "data" not in self._raw:
                return None

            self._content = base64.urlsafe_b64decode(
                self._raw.get("data").encode("UTF-8")
            )

        return self._content


class Attachment:
    def __init__(self, message_id, client, raw_part):
        self._raw = raw_part
        self._client = client
        self._body = AttachmentBody(raw_part["body"])
        self.message_id = message_id

    def _fetch_body_if_needed(self):
        if not self._body.content:
            self._body = self._client.get_attachment_body(self.id, self.message_id)

    @property
    def id(self):
        return self._body.id

    @property
    def filename(self):
        return self._raw.get("filename")

    @property
    def content(self):
        self._fetch_body_if_needed()
        return self._body.content


class Message:
    def __init__(self, client, raw_message):
        self._raw = raw_message
        self._client = client
        self._date = None
        self._headers = None
        self._attachments = None

    def _fetch_if_needed(self):
        if "payload" not in self._raw:
            self._raw = self._client.get_raw_message(self.id)

    def _make_headers(self):
        self._headers = []
        for header in self._payload.get("headers"):
            self._headers[header["name"]] = header["value"]

    @property
    def _payload(self):
        return self._raw["payload"]

    @property
    def id(self):
        return self._raw.get("id")

    @property
    def subject(self):
        if not self._headers:
            self._fetch_if_needed()
            self._make_headers()

        return self._headers["Subject"]

    @property
    def date(self):
        if not self._date:
            self._fetch_if_needed()
            ms_in_seconds = 1000
            date_in_seconds = int(self._raw["internalDate"]) / ms_in_seconds
            self._date = datetime.utcfromtimestamp(date_in_seconds)

        return self._date

    @property
    def attachments(self):
        if not self._attachments:
            self._fetch_if_needed()
            self._attachments = [
                Attachment(self.id, self._client, part)
                for part in self._payload.get("parts")
                if part["filename"]
            ]

        return self._attachments

    def __str__(self):
        return "Gmail message: {}".format(self.id)
