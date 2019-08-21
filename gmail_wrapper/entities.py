import base64
from datetime import datetime


class AttachmentBody:
    def __init__(self, body):
        self._raw = body
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

            self._content = base64.urlsafe_b64decode(self._raw.get("data").encode("UTF-8"))

        return self._content


class Attachment:
    def __init__(self, message_id, client, part):
        self._raw = part
        self._client = client
        self._body = AttachmentBody(part["body"])
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
    def __init__(self, client, message):
        self._raw = message
        self._client = client
        self._subject = None
        self._date = None
        self._attachments = None

    def _fetch_if_needed(self):
        if "payload" not in self._raw:
            self._raw = self._client.get_message(self.id, as_raw=True)

    @property
    def _payload(self):
        return self._raw["payload"]

    @property
    def id(self):
        return self._raw.get("id")

    @property
    def subject(self):
        if not self._subject:
            self._fetch_if_needed()
            self._subject = next(
                (
                    header
                    for header in self._payload.get("headers")
                    if header["name"] == "Subject"
                ),
                None,
            ).get("value")

        return self._subject

    @property
    def date(self):
        if not self._date:
            self._fetch_if_needed()
            self._date = datetime.utcfromtimestamp(
                int(self._raw["internalDate"]) / 1000
            )

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
        return "<Gmail message: {}>".format(self.id)
