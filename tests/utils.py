def make_gmail_client(
    mocker, list_return=None, get_return=None, attachment_return=None
):
    return mocker.MagicMock(
        users=mocker.MagicMock(
            return_value=mocker.MagicMock(
                messages=mocker.MagicMock(
                    return_value=mocker.MagicMock(
                        list=mocker.MagicMock(
                            return_value=mocker.MagicMock(
                                execute=mocker.MagicMock(return_value=list_return)
                            )
                        ),
                        get=mocker.MagicMock(
                            return_value=mocker.MagicMock(
                                execute=mocker.MagicMock(return_value=get_return)
                            )
                        ),
                        attachments=mocker.MagicMock(
                            return_value=mocker.MagicMock(
                                get=mocker.MagicMock(
                                    return_value=mocker.MagicMock(
                                        execute=mocker.MagicMock(
                                            return_value=attachment_return
                                        )
                                    )
                                )
                            )
                        ),
                    )
                )
            )
        )
    )