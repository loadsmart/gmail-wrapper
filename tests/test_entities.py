import datetime

from gmail_wrapper.entities import Message, Attachment, AttachmentBody


class TestMessage:
    def test_it_has_basic_properties_without_additional_fetch(
        self, mocker, client, raw_incomplete_message
    ):
        mocked_get_raw_message = mocker.patch(
            "gmail_wrapper.client.GmailClient.get_raw_message"
        )
        incomplete_message = Message(client, raw_incomplete_message)
        assert incomplete_message.id == raw_incomplete_message["id"]
        assert incomplete_message.date == datetime.datetime(
            1970, 1, 19, 3, 6, 38, 665000
        )
        mocked_get_raw_message.assert_not_called()

    def test_it_fetch_additional_information_when_needed(
        self, mocker, client, raw_incomplete_message, raw_complete_message
    ):
        mocked_get_raw_message = mocker.patch(
            "gmail_wrapper.client.GmailClient.get_raw_message",
            return_value=raw_complete_message,
        )
        incomplete_message = Message(client, raw_incomplete_message)
        assert incomplete_message.thread_id == raw_complete_message["threadId"]
        assert (
            incomplete_message.subject
            == raw_complete_message["payload"]["headers"][2]["value"]
        )
        assert (
            incomplete_message.headers["To"]
            == raw_complete_message["payload"]["headers"][0]["value"]
        )
        mocked_get_raw_message.assert_called_once_with(raw_incomplete_message["id"])

    def test_it_return_none_if_no_subject_header(self, client, raw_complete_message):
        del raw_complete_message["payload"]["headers"][2]
        message = Message(client, raw_complete_message)
        assert message.subject is None

    def test_get_labels(
        self, mocker, raw_complete_message, client, raw_incomplete_message
    ):
        mocked_get_raw_message = mocker.patch(
            "gmail_wrapper.client.GmailClient.get_raw_message",
            return_value=raw_complete_message,
        )
        incomplete_message = Message(client, raw_incomplete_message)
        assert incomplete_message.labels == raw_complete_message["labelIds"]
        mocked_get_raw_message.assert_called_once_with(raw_incomplete_message["id"])

    def test_as_str(self, client, raw_incomplete_message):
        message = Message(client, raw_incomplete_message)
        assert str(message) == "Gmail message: {}".format(raw_incomplete_message["id"])

    def test_it_generates_attachment_objects(self, client, raw_complete_message):
        complete_message = Message(client, raw_complete_message)
        assert all(
            [
                isinstance(attachment, Attachment) and attachment.filename
                for attachment in complete_message.attachments
            ]
        )

    def test_it_does_not_generate_attachment_objects_for_attachments_without_id(
        self, client, raw_complete_message
    ):
        complete_message = Message(client, raw_complete_message)
        raw_complete_message["payload"]["parts"].append(
            {
                "body": {"size": 0, "data": ""},
                "filename": "invalid.pdf",
                "partId": "BB710",
                "mimeType": "application/pdf",
            }
        )
        assert len(complete_message.attachments) == 1
        assert complete_message.attachments[0].id
        assert complete_message.attachments[0].filename != "invalid.pdf"

    def test_it_returns_empty_list_if_no_attachments(
        self, client, raw_complete_message
    ):
        raw_complete_message["payload"]["parts"] = None
        complete_message = Message(client, raw_complete_message)
        assert complete_message.attachments == []

    def test_it_modifies_a_message(
        self, mocker, client, raw_incomplete_message, raw_complete_message
    ):
        mocked_modify_raw_message = mocker.patch(
            "gmail_wrapper.client.GmailClient.modify_raw_message",
            return_value=raw_complete_message,
        )
        message = Message(client, raw_incomplete_message)
        message.modify(add_labels=["phishing"], remove_labels=["oklahoma"])
        mocked_modify_raw_message.assert_called_once_with(
            raw_incomplete_message["id"],
            add_labels=["phishing"],
            remove_labels=["oklahoma"],
        )
        assert message.labels == raw_complete_message["labelIds"]

    def test_it_archives_a_method(self, mocker, client, raw_complete_message):
        mocked_modify_raw_message = mocker.patch(
            "gmail_wrapper.client.GmailClient.modify_raw_message",
            return_value=raw_complete_message,
        )
        message = Message(client, raw_complete_message)
        message.archive()
        mocked_modify_raw_message.assert_called_once_with(
            raw_complete_message["id"], add_labels=None, remove_labels=["INBOX"]
        )


class TestAttachment:
    def test_it_has_basic_properties_without_additional_fetch(
        self, mocker, client, raw_complete_message
    ):
        mocked_get_attachment_body = mocker.patch(
            "gmail_wrapper.client.GmailClient.get_attachment_body"
        )
        raw_attachment = raw_complete_message["payload"]["parts"][1]
        incomplete_attachment = Attachment("123AAB", client, raw_attachment)
        assert incomplete_attachment.id == raw_attachment["body"]["attachmentId"]
        assert incomplete_attachment.filename == raw_attachment["filename"]
        mocked_get_attachment_body.assert_not_called()

    def test_it_fetch_additional_information_when_needed(
        self, mocker, client, raw_complete_message, raw_attachment_body
    ):
        mocked_get_attachment_body = mocker.patch(
            "gmail_wrapper.client.GmailClient.get_attachment_body",
            return_value=AttachmentBody(raw_attachment_body),
        )
        incomplete_attachment = Attachment(
            "123AAB", client, raw_complete_message["payload"]["parts"][1]
        )
        assert incomplete_attachment.content
        mocked_get_attachment_body.assert_called_once_with(
            raw_attachment_body["attachmentId"], "123AAB"
        )


class TestAttachmentBody:
    def test_it_has_basic_properties_without_additional_fetch(
        self, raw_complete_message
    ):
        body = raw_complete_message["payload"]["parts"][1]["body"]
        incomplete_attachment_body = AttachmentBody(body)
        assert incomplete_attachment_body.id == body["attachmentId"]
        assert incomplete_attachment_body.size == body["size"]

    def test_it_returns_none_when_no_data(self, raw_complete_message):
        body = raw_complete_message["payload"]["parts"][1]["body"]
        incomplete_attachment_body = AttachmentBody(body)
        assert not incomplete_attachment_body.content

    def test_it_decodes_base64_data(self, raw_attachment_body):
        complete_attachment_body = AttachmentBody(raw_attachment_body)
        assert (
            complete_attachment_body.content
            == b"The Quick Brown Fox Jumps Over The Lazy Dog"
        )
