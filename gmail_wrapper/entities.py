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
        data = self._raw.get("data")
        if not data:
            return None

        return base64.urlsafe_b64decode(data.encode("UTF-8"))


class Attachment:
    def __init__(self, message_id, client, raw_part):
        self._raw = raw_part
        self._client = client
        self._body = AttachmentBody(raw_part["body"])
        self.message_id = message_id

    @property
    def id(self):
        return self._body.id

    @property
    def filename(self):
        return self._raw.get("filename")

    @property
    def content(self):
        if not self._body.content:
            self._body = self._client.get_attachment_body(self.id, self.message_id)

        return self._body.content


class Message:
    def __init__(self, client, raw_message):
        self._raw = raw_message
        self._client = client

    @property
    def _payload(self):
        if "payload" not in self._raw:
            self._raw = self._client.get_raw_message(self.id)

        return self._raw["payload"]

    @property
    def headers(self):
        headers = {}
        for header in self._payload.get("headers"):
            headers[header["name"]] = header["value"]
        return headers

    @property
    def id(self):
        return self._raw.get("id")

    @property
    def subject(self):
        return self.headers["Subject"]

    @property
    def date(self):
        ms_in_seconds = 1000
        date_in_seconds = int(self._raw.get("internalDate")) / ms_in_seconds
        return datetime.utcfromtimestamp(date_in_seconds)

    @property
    def attachments(self):
        return [
            Attachment(self.id, self._client, part)
            for part in self._payload.get("parts")
            if part["filename"]
        ]

    def __str__(self):
        return "Gmail message: {}".format(self.id)
