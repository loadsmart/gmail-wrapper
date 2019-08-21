from gmail_wrapper import GmailClient
from gmail_wrapper.entities import Message, AttachmentBody
from gmail_wrapper.tests.utils import make_gmail_client


class TestGetRawMessages:
    def test_it_returns_raw_messages(self, mocker, raw_incomplete_message):
        raw_response = [{"messages": [raw_incomplete_message, raw_incomplete_message]}]
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(mocker, list_return=raw_response),
        )
        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        assert client.get_raw_messages() == raw_response


class TestGetMessages:
    def test_it_returns_a_message_list(self, mocker, client, raw_incomplete_message):
        mocked_get_raw_messages = mocker.patch(
            "gmail_wrapper.client.GmailClient.get_raw_messages",
            return_value=[
                {"messages": [raw_incomplete_message, raw_incomplete_message]}
            ],
        )
        messages = client.get_messages(query="filename:pdf", limit=5)
        mocked_get_raw_messages.assert_called_once_with("filename:pdf", 5)
        assert all([isinstance(message, Message) for message in messages])
        assert all([message.id is not None for message in messages])

    def test_it_doesnt_break_when_no_results(self, mocker):
        raw_response = {"resultSizeEstimate": 0}
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(mocker, list_return=raw_response),
        )
        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        messages = client.get_messages()
        assert messages == []


class TestGetRawMessage:
    def test_it_returns_a_raw_message(self, mocker, raw_complete_message):
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(mocker, get_return=raw_complete_message),
        )
        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        message = client.get_raw_message("123AAB")
        assert message == raw_complete_message


class TestGetMessage:
    def test_it_returns_a_message(self, mocker, client, raw_complete_message):
        mocked_get_raw_message = mocker.patch(
            "gmail_wrapper.client.GmailClient.get_raw_message",
            return_value=raw_complete_message,
        )
        message = client.get_message("123AAB")
        mocked_get_raw_message.assert_called_once_with("123AAB")
        assert isinstance(message, Message)
        assert message.id == raw_complete_message["id"]


class TestGetRawAttachmentBody:
    def test_it_returns_a_raw_attachment_body(self, mocker, raw_attachment_body):
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(
                mocker, attachment_return=raw_attachment_body
            ),
        )
        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        attachment_body = client.get_raw_attachment_body(
            id="CCX457", message_id="123AAB"
        )
        assert attachment_body == raw_attachment_body


class TestGetAttachmentBody:
    def test_it_returns_an_attachment_body(self, mocker, client, raw_attachment_body):
        mocked_get_raw_attachment_body = mocker.patch(
            "gmail_wrapper.client.GmailClient.get_raw_attachment_body",
            return_value=raw_attachment_body,
        )
        attachment_body = client.get_attachment_body(id="CCX457", message_id="123AAB")
        mocked_get_raw_attachment_body.assert_called_once_with("CCX457", "123AAB")
        assert isinstance(attachment_body, AttachmentBody)
        assert attachment_body.id == raw_attachment_body["attachmentId"]
