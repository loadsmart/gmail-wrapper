# Gmail Wrapper

[![CircleCI](https://circleci.com/gh/loadsmart/gmail-wrapper/tree/master.svg?style=svg&circle-token=110f54407b50c79865fe1f9b4352e213bc68504b)](https://circleci.com/gh/loadsmart/gmail-wrapper/tree/master)
[![codecov](https://codecov.io/gh/loadsmart/gmail-wrapper/branch/master/graph/badge.svg?token=Ciq3QScb0L)](https://codecov.io/gh/loadsmart/gmail-wrapper)

Because scrapping Gmail data doesn't have to be a [pain](https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.html).

## Installing

```sh
pip install gmail-wrapper
```

## Developing

Create your [venv](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments)

```sh
virtualenv .venv
source .venv/bin/activate
```

Then you can install the dependencies

```sh
pip install -e .
```

## Testing

Simply run

```sh
make test
```

## Basic Usage

- Setup the client

```python
from gmail_wrapper import GmailClient

email_account = "john.doe@gmail.com"
credentials_string = "{...}" # You must generate this on your Google account
scopes = [GmailClient.SCOPE_READONLY]
client = GmailClient(email_account, secrets_json_string=credentials_string, scopes=scopes)
```

- Fetch messages

```python
import sys

def print_message_data(message):
    print("-- MESSAGE {} --".format(message.id))
    print("SUBJECT: {}".format(message.subject))
    print("DATE: {}".format(message.date))
    for attachment in message.attachments:
        print("\t-- ATTACHMENT {} --".format(attachment.id))
        print("\t\tFILENAME: {}".format(attachment.filename))
        print("\t\tDECODED SIZE: {}".format(sys.getsizeof(attachment.content)))

# Get a message list
query = "filename:pdf label:friends" # Check Gmail query docs: https://support.google.com/mail/answer/7190
messages = client.get_messages(query=query, limit=10)
for message in messages:
    print_message_data(message)

# ...Or get a single message
message_id = "..."
message = client.get_message(message_id)
print_message_data(message)
```

## Need more help?

Reach `#eng-accounting` Slack channel.
