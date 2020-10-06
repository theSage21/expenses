# Expenses

  A Telegram bot that helps you keep a track of your spending. 
  
## Features

- Replies to each message and marks it as recorded.
- Automatically tags messages with information found in the sms so that you can quickly search for it later on in telegram.
- You can import Walnut expense reports to backfill your database.
- `/report` returns monthly totals
  
## Pre-requisites

  - Install Python from [python.org](https://www.python.org/). 
  - Install pip from [pip.pypa.io](https://pip.pypa.io/en/stable/installing/).
  
## Setup

1. Fork [this](https://github.com/theSage21/expenses.git) repository.
2. Clone the forked repository locally using `git clone https://github.com/<your-github-username>/expenses.git`
3. Navigate to the project directory.  `cd expenses`
4. Create virtual environment.  `python -m virtualenv venv`
5. Activate the virtual environment. `source venv/bin/activate`
6. Create a private group in telegram. 
7. Create a telegram bot using botfather. Turn off group privacy in bot settings.
8. Run this code using the telegram token given to you by botfather.
   ```
   python -m expenses --tgtoken <paste-your-token>
   ```
9. Use TelegramSms android app to forward all smses coming to your phone to this group. See setup instructions for that.
10. Set up a user bot to echo messages received from the sms bot since bots cannot see each other's messages.

## Docker setup 

```bash
# Assuming you have docker, git installed already
git clone https://github.com/<your-github-username>/expenses.git
cd expenses
docker build -t expenses .
echo "export TG_TOKEN='<your-tg-bot-token>'" > .env
(source .env && docker run --user "$(id -u):$(id -g)" --detach -v $PWD:/src --restart always  -e TG_TOKEN expenses)
```
