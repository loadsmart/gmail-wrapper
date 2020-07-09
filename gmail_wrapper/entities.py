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
    def labels(self):
        if "labelIds" not in self._raw:
            self._raw = self._client.get_raw_message(self.id)

        return self._raw.get("labelIds", [])

    @property
    def id(self):
        return self._raw.get("id")

    @property
    def subject(self):
        return self.headers.get("Subject")

    @property
    def from_address(self):
        return self.headers.get("From")

    @property
    def reply_to(self):
        return self.headers.get("Reply-To")

    @property
    def message_id(self):
        """
        While self.id is the user-bound id of the message, self.message_id
        is the global id of the message, valid for every user on the thread.
        """
        return self.headers.get("Message-ID", self.headers.get("Message-Id"))

    @property
    def thread_id(self):
        if "threadId" not in self._raw:
            self._raw = self._client.get_raw_message(self.id)

        return self._raw.get("threadId")

    @property
    def date(self):
        ms_in_seconds = 1000
        date_in_seconds = int(self._raw.get("internalDate")) / ms_in_seconds
        return datetime.utcfromtimestamp(date_in_seconds)

    def _extract_attachments_from_parts(self, parts):
        attachments = []
        for part in parts:
            if part.get("filename") and part.get("body", {}).get("attachmentId"):
                attachments.append(Attachment(self.id, self._client, part))
            if part.get("parts"):
                attachments += self._extract_attachments_from_parts(part.get("parts"))

        return attachments

    @property
    def attachments(self):
        parts = self._payload.get("parts")

        if not parts:
            return []

        return self._extract_attachments_from_parts(parts)

    def modify(self, add_labels=None, remove_labels=None):
        self._raw = self._client.modify_raw_message(
            self.id, add_labels=add_labels, remove_labels=remove_labels
        )

    def reply(self, html_content, use_reply_to=True):
        to = self.reply_to if (self.reply_to and use_reply_to) else self.from_address

        return self._client.send(
            subject=f"Re:{self.subject}",
            html_content=html_content,
            to=to,
            references=[self.message_id],
            in_reply_to=[self.message_id],
            thread_id=self.thread_id,
        )

    def archive(self):
        self.modify(remove_labels=["INBOX"])

    def __str__(self):
        return "Gmail message: {}".format(self.id)
