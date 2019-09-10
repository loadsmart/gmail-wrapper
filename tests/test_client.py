import base64

from gmail_wrapper import GmailClient
from gmail_wrapper.entities import Message, AttachmentBody
from tests.utils import make_gmail_client


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


class TestModifyRawMessage:
    def test_it_modifies_and_return_a_raw_message(self, mocker, raw_complete_message):
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(mocker, modify_return=raw_complete_message),
        )
        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        modified_message = client.modify_raw_message(
            id="CCX457", add_labels=["processed"], remove_labels=["phishing"]
        )
        assert modified_message == raw_complete_message
        client._messages_resource().modify.assert_called_once_with(
            userId="foo@bar.com",
            id="CCX457",
            body={"addLabelIds": ["processed"], "removeLabelIds": ["phishing"]},
        )


class TestModifyMessage:
    def test_it_returns_a_modified_message(self, client, mocker, raw_complete_message):
        mocked_modify_raw_message = mocker.patch(
            "gmail_wrapper.client.GmailClient.modify_raw_message",
            return_value=raw_complete_message,
        )
        modified_message = client.modify_message(
            id="CCX457", add_labels=["foo"], remove_labels=["bar"]
        )
        mocked_modify_raw_message.assert_called_once_with("CCX457", ["foo"], ["bar"])
        assert isinstance(modified_message, Message)
        assert modified_message.id == raw_complete_message["id"]


class TestSendRaw:
    def test_it_creates_a_proper_sendable_message(self, client):
        subject = "Hi there!"
        content = "<html><p>Hi there!</p></html>"
        to = "bob.dylan@loadsmart.com"
        cc = ["agostinho.carrara@loadsmart.com", "jon.maddog@loadsmart.com"]
        bcc = []
        sendable = client._make_sendable_message(subject, content, to, cc, bcc)
        decoded = base64.urlsafe_b64decode(sendable["raw"]).decode("utf-8")
        assert decoded.startswith("Content-Type: text/html;")
        assert f"subject: {subject}\n" in decoded
        assert f"to: {to}\n" in decoded
        assert f"cc: {cc[0]},{cc[1]}\n" in decoded
        assert f"bcc: \n" in decoded
        assert content in decoded

    def test_it_send_and_return_a_raw_message(self, mocker, raw_complete_message):
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(mocker, send_return=raw_complete_message),
        )
        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        sent_message = client.send_raw(
            "Hi there!", "<html><p>Hey</p></html>", "foo@bar.com"
        )
        assert sent_message == raw_complete_message
        client._messages_resource().send.assert_called_once_with(
            {
                "raw": base64.urlsafe_b64encode(
                    b'Content-Type: text/html; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nsubject: Hi there!\nfrom: foo@bar.com\nto: foo@bar.com\ncc: \nbcc: \n\n<html><p>Hey</p></html>'
                )
            }
        )
