# Expenses

## Setup

- Create a private group in telegram.
- Use TelegramSms android app to forward all smses coming to your phone to this group. See setup instructions for that.
- Create a telegram bot using botfather. Turn off group privacy in bot settings.
- Run this code using the telegram token given to you.

```bash
docker build -t expenses .
source .env  # make sure this sets TG_TOKEN
docker run --user "$(id -u):$(id -g)" --detach -v $PWD:/src --restart always  -e TG_TOKEN expenses
```

## Features

- Replies to each message and marks it as recorded.
- Asks person to mark expenses with tags.
