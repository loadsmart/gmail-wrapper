import datetime

from gmail_wrapper.entities import Message, Attachment


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
        assert (
            incomplete_message.subject
            == raw_complete_message["payload"]["headers"][2]["value"]
        )
        assert (
            incomplete_message.headers["To"]
            == raw_complete_message["payload"]["headers"][0]["value"]
        )
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
