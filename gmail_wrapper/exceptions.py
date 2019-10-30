class GmailError(Exception):
    def __str__(self):
        return f"GmailError: Gmail returned an internal server error"


class MessageNotFoundError(Exception):
    def __init__(self, message_id):
        self.message_id = message_id

    def __str__(self):
        return f"MessageNotFoundError: Gmail returned 404 when attempting to get message {self.message_id}"


class AttachmentNotFoundError(Exception):
    def __init__(self, message_id, attachment_id):
        self.message_id = message_id
        self.attachment_id = attachment_id

    def __str__(self):
        return f"AttachmentNotFoundError: Gmail returned 404 when attempting to get attachment {self.attachment_id} of message {self.message_id}"
