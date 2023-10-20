
# Autoclock Bot for Diamond Light Source

## Introduction

The Autoclock Bot automates the process of clocking in and out on the Diamond Light Source's internal self-service system. It allows you to clock in or out by sending a Telegram message from your phone. The bot is implemented using Python and employs the `playwright` library for web automation and the `python-telegram-bot` library for Telegram bot functionality.


## Security

Your username, password, and Telegram bot token are securely stored on your local machine using the `keyring` library. 

| OS      | Storage Location                         |
|---------|------------------------------------------|
| Windows | Windows Credential Locker                |
| macOS   | macOS Keychain                            |
| Linux   | Secret Service API (e.g., GNOME Keyring or KWallet)|

During the bot's operation, a temporary Chromium browser instance is launched on your local machine. Your credentials are retrieved from the secure storage provided by `keyring` and used to authenticate you on the Diamond Light Source's internal self-service system. This is similar to how Google Chrome's Autofill feature operates. Importantly, your credentials are decrypted only when necessary and are never sent to any external locations. Access to these credentials requires you to be logged in to your computer, and the bot will only perform actions when it receives messages from an authorised Telegram account (yours).



## How to Use

### Prerequisites

- A Telegram account

### Initial Setup

1. Clone the GitHub repository.
2. Install the required Python packages by running `pip install -r requirements.txt`.
3. Open Telegram and start a chat with "BotFather", a built-in bot that helps you create and manage other bots.
4. Create a new bot: Send `/newbot` to BotFather, who will guide you through the setup. You could name your bot `autoclock_bot_{your_username}` or something similar.
5. Get the token: BotFather will provide a token for your new bot upon its creation. Make sure to note this token as it is needed for API authentication.
6. Run the script using `python autoclock.py`. During the first run, you will be prompted to enter your Diamond Light Source username and password, along with the Telegram bot token. These credentials are securely stored in your system's keyring.
7. Locate your bot on Telegram and start a chat by sending the `/start` command.

The program saves the chat ID of the first message it receives, effectively authorising only your Telegram account for clocking in or out. Any other users who initiate a chat with your bot will be denied access.

### Usage

1.  Run the script to start the bot.
2.  Send `in` to the Telegram bot to clock in.
3.  Send `out` to the bot to clock out.
