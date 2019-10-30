import base64

import pytest
from googleapiclient.errors import HttpError

from gmail_wrapper import GmailClient
from gmail_wrapper.entities import Message, AttachmentBody
from gmail_wrapper.exceptions import (
    MessageNotFoundError,
    AttachmentNotFoundError,
    GmailError,
)
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

    def test_it_encapsulates_gmail_exceptions(self, mocker):
        server_error_response = mocker.MagicMock(status=500)
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(
                mocker, list_effect=HttpError(server_error_response, b"Content")
            ),
        )

        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        with pytest.raises(GmailError):
            client.get_raw_messages()


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

    @pytest.mark.parametrize(
        "error_code,exception_expected",
        [(500, GmailError), (404, MessageNotFoundError)],
    )
    def test_it_encapsulates_gmail_exceptions(
        self, mocker, error_code, exception_expected
    ):
        error_response = mocker.MagicMock(status=error_code)
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(
                mocker, get_effect=HttpError(error_response, b"Content")
            ),
        )

        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        with pytest.raises(exception_expected):
            client.get_raw_message("123AAB")


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

    @pytest.mark.parametrize(
        "error_code,exception_expected",
        [(500, GmailError), (404, AttachmentNotFoundError)],
    )
    def test_it_encapsulates_gmail_exceptions(
        self, mocker, error_code, exception_expected
    ):
        error_response = mocker.MagicMock(status=error_code)
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(
                mocker, attachment_effect=HttpError(error_response, b"Content")
            ),
        )

        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        with pytest.raises(exception_expected):
            client.get_raw_attachment_body(id="CCX457", message_id="123AAB")


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

    @pytest.mark.parametrize(
        "error_code,exception_expected",
        [(500, GmailError), (404, MessageNotFoundError)],
    )
    def test_it_encapsulates_gmail_exceptions(
        self, mocker, error_code, exception_expected
    ):
        error_response = mocker.MagicMock(status=error_code)
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(
                mocker, modify_effect=HttpError(error_response, b"Content")
            ),
        )

        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        with pytest.raises(exception_expected):
            client.modify_raw_message(
                id="CCX457", add_labels=["processed"], remove_labels=["phishing"]
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


class TestModifyMultipleMessages:
    def test_it_modifies_multiple_messages_and_returns_nothing(self, client):
        ids_to_modify = ["ABC123", "DEF432"]
        labels_to_insert = ["Label_123", "Label_432"]
        labels_to_remove = ["Label_567", "Label_789"]
        client.modify_multiple_messages(
            ids_to_modify, labels_to_insert, labels_to_remove
        )
        client._messages_resource().batchModify.assert_called_once_with(
            userId="foo@bar.com",
            body={
                "ids": ids_to_modify,
                "addLabelIds": labels_to_insert,
                "removeLabelIds": labels_to_remove,
            },
        )

    def test_it_can_do_a_noop(self, client):
        client.modify_multiple_messages([])
        client._messages_resource().batchModify.assert_called_once_with(
            userId="foo@bar.com",
            body={"ids": [], "addLabelIds": [], "removeLabelIds": []},
        )


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
            "Hi there!", "<html><p>Hey</p></html>", "john@doe.com"
        )
        assert sent_message == raw_complete_message
        client._messages_resource().send.assert_called_once_with(
            userId="foo@bar.com",
            body={
                "raw": base64.urlsafe_b64encode(
                    b'Content-Type: text/html; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nsubject: Hi there!\nfrom: foo@bar.com\nto: john@doe.com\ncc: \nbcc: \n\n<html><p>Hey</p></html>'
                ).decode("utf-8")
            },
        )


class TestSend:
    def test_it_returns_the_sent_message(self, client, mocker, raw_complete_message):
        mocked_send_raw_message = mocker.patch(
            "gmail_wrapper.client.GmailClient.send_raw",
            return_value=raw_complete_message,
        )
        sent_message = client.send(
            subject="Hi there!",
            html_content="<html><p>Hey</p></html>",
            to="foo@bar.com",
        )
        mocked_send_raw_message.assert_called_once_with(
            "Hi there!", "<html><p>Hey</p></html>", "foo@bar.com", None, None
        )
        assert isinstance(sent_message, Message)
        assert sent_message.id == raw_complete_message["id"]
