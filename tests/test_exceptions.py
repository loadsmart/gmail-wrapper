import pytest
from googleapiclient.errors import HttpError

from gmail_wrapper import GmailClient
from gmail_wrapper.exceptions import (
    MessageNotFoundError,
    AttachmentNotFoundError,
    GmailError,
)
from tests.utils import make_gmail_client


class TestGmailError:

    def test_exceptions_gmail_error(self, mocker):
        server_error_response = mocker.MagicMock(status=500)
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(
                mocker, list_effect=HttpError(server_error_response, b"Content")
            ),
        )

        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        with pytest.raises(GmailError) as error:
            raise client.get_raw_messages()
        assert str(error.value) == "GmailError: Gmail returned an internal server error"


class TestMessageNotFoundError:
    def test_exceptions_message_not_found(self, mocker):
        error_response = mocker.MagicMock(status=404)
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(
                mocker, get_effect=HttpError(error_response, b"Content")
            ),
        )

        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        message_id = "123AAB"
        with pytest.raises(MessageNotFoundError) as error:
            raise client.get_raw_message(message_id)
        assert str(error.value) == f"MessageNotFoundError: Gmail returned 404 when attempting to get message {message_id}"


class TestAttachmentNotFoundError:
    def test_exceptions_attachment_not_found(self, mocker):
        error_response = mocker.MagicMock(status=404)
        mocker.patch(
            "gmail_wrapper.client.GmailClient._make_client",
            return_value=make_gmail_client(
                mocker, attachment_effect=HttpError(error_response, b"Content")
            ),
        )

        client = GmailClient(email="foo@bar.com", secrets_json_string="{}")
        message_id = "123AAB"
        attachment_id = "CCX457"
        with pytest.raises(AttachmentNotFoundError) as error:
            raise client.get_attachment_body(id=attachment_id, message_id=message_id)
        assert str(error.value) == f"AttachmentNotFoundError: Gmail returned 404 when attempting to get attachment {attachment_id} of message {message_id}"
