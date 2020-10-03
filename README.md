# Expenses
  A Telegram bot that helps you keep a track of your spending. 
  
## Features

- Replies to each message and marks it as recorded.
- Asks person to mark expenses with tags.
  
## Pre-requisites
- **Python**
      - Install Python from [here](https://www.python.org/). 
- **Pip**
      - Install pip from [here](https://pip.pypa.io/en/stable/installing/).
  
## Setup
**1.** Fork [this](https://github.com/theSage21/expenses.git) repository.

**2.** Clone the forked repository.

```bash
git clone https://github.com/<your-github-username>/expenses.git
```
**3.** Navigate to the project directory.

```bash
cd expenses
```
**4.** Create virtual environment. 

```
python -m virtualenv venv
```
**5.** Activate the virtual environment. 

```
source venv/bin/activate
```

**6.** Create a private group in telegram. 

**7.** Create a telegram bot using botfather. Turn off group privacy in bot settings.

**8.** Run this code using the telegram token given to you.

```
python -m expenses --tgtoken <paste-your-token> --dburl 'sqlite:///db.sql'

```

> Use TelegramSms android app to forward all smses coming to your phone to this group. See setup instructions for that.

## Docker setup 

```bash
docker build -t expenses .
source .env  # make sure this sets TG_TOKEN
docker run --user "$(id -u):$(id -g)" --detach -v $PWD:/src --restart always  -e TG_TOKEN expenses
```

