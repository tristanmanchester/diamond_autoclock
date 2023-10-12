from playwright.async_api import async_playwright
import keyring
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timezone
from getpass import getpass


async def login(page, context, update, status_flag):
    """
    Authenticates the user on a specific website using Playwright.

    Args:
        page (Page): The Playwright page object representing the current browser tab.
        context: Telegram bot context for sending messages.
        update: Telegram update object containing the message data.
        status_flag (dict): A dictionary to store the status of the login attempt.

    Returns:
        None: The function updates the status_flag dictionary in place.
    """
    try:
        # Navigate to the login page of the website
        await page.goto("https://selfservice.diamond.ac.uk/Login.aspx")
        await page.wait_for_load_state("load")

        # Attempt to locate the login button on the webpage
        login_button = await page.query_selector("#btnLogin")

        if login_button:
            # Notify the user that login is being attempted
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Not logged in. Logging in...")

            # Retrieve stored password from keyring
            password = keyring.get_password("autoclock", "qps56811")

            # Populate the username and password fields
            await page.fill("#txtUsr", "qps56811")
            await page.fill("#txtPwd", password)

            # Execute the login by clicking the login button
            await page.click("#btnLogin")

            await page.wait_for_load_state("load")

            # Check for the presence of a button that indicates successful login
            clocking_page_button = await page.query_selector("#ContentPlaceHolder1_repShortcuts_lblShortcut_1")

            if clocking_page_button:
                # Notify the user of successful login
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Successfully logged in.")

                # Update status flag to indicate successful login
                status_flag["login_success"] = True
            else:
                # Notify the user of failed login
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to log in.")

                # Update status flag to indicate failed login
                status_flag["login_success"] = False
    except Exception as e:
        # Notify the user if an exception occurs during the login process
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {e}. Please retry.")

        # Update status flag to indicate an error occurred
        status_flag["login_success"] = False

        # Close the browser in case of an exception
        await page.context.browser.close()


async def navigate_to_clocking_page(page, status_flag):
    """
    Directs the browser to the clocking page of a specific website.

    Args:
        page: The Playwright page object representing the current browser tab.
        status_flag (dict): A dictionary for tracking the success status of navigation.

    Returns:
        str: A message that describes the outcome of the navigation attempt.
    """
    try:
        # Query the webpage to find the button that leads to the clocking page
        clocking_page_button = await page.query_selector("#ContentPlaceHolder1_repShortcuts_lblShortcut_1")

        if clocking_page_button:
            # Navigate to the clocking page by clicking the found button
            await page.click("#ContentPlaceHolder1_repShortcuts_lblShortcut_1")

            # Update the status flag to indicate successful navigation
            status_flag["navigation_success"] = True

            return "Successfully navigated to clocking page."
        else:
            # Close the browser if the navigation button is not found
            await page.context.browser.close()

            # Update the status flag to indicate failed navigation
            status_flag["navigation_success"] = False

            return "Error: Clocking page button not found. Please retry."

    except Exception as e:
        # Close the browser in the event of an exception and update the status flag
        await page.context.browser.close()

        # Update the status flag to indicate an error occurred during navigation
        status_flag["navigation_success"] = False

        return f"An error occurred: {e}. Please retry."


async def clock_in(page):
    """
    Executes the clock-in operation on the specified webpage.

    Args:
        page: The Playwright page object to interact with.

    Returns:
        str: A message describing the success or failure of the clock-in operation.
    """

    try:
        # Query for the element that displays the current clocking status
        clocking_status = await page.query_selector("#ContentPlaceHolder1_lblClockingStatus")

        # Query for the element that displays the current time on the clock
        clock = await page.query_selector("#ContentPlaceHolder1_divClock")

        if clocking_status:
            # Retrieve the initial text indicating the clocking status
            initial_status_text = await clocking_status.text_content()

            # Retrieve the current time displayed on the clock or set it to "Unknown time" if the element is not found
            clock_time = await clock.text_content() if clock else "Unknown time"

            # Determine if the user is already clocked in
            if "clocked in" in initial_status_text.lower():
                return f"Already clocked in. Time: {clock_time}"

            # Trigger the clock-in action by clicking the submit button
            await page.click("#ContentPlaceHolder1_btnSubmit")

            # Wait for the clocking status text to change
            await page.wait_for_selector(
                f"#ContentPlaceHolder1_lblClockingStatus:not(:has-text('{initial_status_text}'))")

            # Re-query the clocking status to get the updated status text
            clocking_status = await page.query_selector("#ContentPlaceHolder1_lblClockingStatus")
            new_status_text = await clocking_status.text_content()

            # Evaluate the success of the clock-in operation based on the updated status text
            if "clocked in" in new_status_text.lower():
                return f"Successfully clocked in at time {clock_time}"
            else:
                return "Failed to clock in. Please retry."
        else:
            return "Clocking status element not found. Please retry."
    except Exception as e:
        return f"An error occurred: {e}. Please retry."


async def clock_out(page):
    """
    Executes the clock-out operation on the specified webpage.

    Args:
        page: The Playwright page object to interact with.

    Returns:
        str: A message describing the success or failure of the clock-out operation.
    """

    try:
        # Query for the element displaying the current clocking status
        clocking_status = await page.query_selector("#ContentPlaceHolder1_lblClockingStatus")

        # Query for the element displaying the current time on the clock
        clock = await page.query_selector("#ContentPlaceHolder1_divClock")

        if clocking_status:
            # Retrieve the initial text indicating the clocking status
            initial_status_text = await clocking_status.text_content()

            # Retrieve the current time displayed on the clock or set to "Unknown time" if not found
            clock_time = await clock.text_content() if clock else "Unknown time"

            # Determine if the user is already clocked out
            if "clocked out" in initial_status_text.lower():
                return f"Already clocked out. Time: {clock_time}"

            # Trigger the clock-out action by clicking the submit button
            await page.click("#ContentPlaceHolder1_btnSubmit")

            # Wait for the clocking status text to change
            await page.wait_for_selector(
                f"#ContentPlaceHolder1_lblClockingStatus:not(:has-text('{initial_status_text}'))")

            # Re-query the clocking status to get the updated status text
            clocking_status = await page.query_selector("#ContentPlaceHolder1_lblClockingStatus")
            new_status_text = await clocking_status.text_content()

            # Evaluate the success of the clock-out operation based on updated status text
            if "clocked out" in new_status_text.lower():
                return f"Successfully clocked out at time {clock_time}"
            else:
                return "Failed to clock out. Please retry."
        else:
            return "Clocking status element not found. Please retry."
    except Exception as e:
        return f"An error occurred: {e}. Please retry."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processes incoming Telegram messages to perform clock-in and clock-out operations.

    Args:
        update (Update): Object containing the Telegram update data, such as the message text.
        context (ContextTypes.DEFAULT_TYPE): Bot context for interacting with Telegram API.

    Side Effects:
        Sends response messages to the user and modifies browser state.
    """
    global start_time
    print(f'Start time: {datetime.fromtimestamp(start_time)}')
    # Retrieve the message's UNIX timestamp
    message_time = update.message.date.timestamp()
    print(f'Message received at {datetime.fromtimestamp(message_time)}.')
    # Ignore messages before the start time
    if message_time < start_time:
        print("Ignoring message before start time.")
        return

    # Retrieve the chat ID from the incoming update
    incoming_chat_id = str(update.effective_chat.id)
    print("Incoming message from chat ID:", incoming_chat_id)

    # Fetch the authorized chat ID from keyring
    authorized_chat_id = keyring.get_password("autobot", "chat_id")

    # Initialise flags to keep track of login and navigation success
    status_flag = {"login_success": False, "navigation_success": False}

    # Check if the incoming chat ID is authorized to execute commands
    if incoming_chat_id == authorized_chat_id:
        # Start a new Playwright session and launch a Chromium browser
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            webpage = await browser.new_page()
            message = update.message.text.lower()

            if message == 'in' or message == 'out':
                # Navigate to the login page and attempt to login
                await context.bot.send_message(chat_id=incoming_chat_id, text="Navigating to login page...")
                await login(webpage, context, update, status_flag)

                # Close the browser if login was unsuccessful
                if not status_flag["login_success"]:
                    await browser.close()
                    return

                # Navigate to the clocking page and check the result
                await context.bot.send_message(chat_id=incoming_chat_id, text="Navigating to clocking page...")
                nav_result = await navigate_to_clocking_page(webpage, status_flag)
                await context.bot.send_message(chat_id=incoming_chat_id, text=nav_result)

                # Close the browser if navigation to the clocking page was unsuccessful
                if not status_flag["navigation_success"]:
                    await browser.close()
                    return

                await webpage.wait_for_load_state("load")

                # Handle clocking commands based on the received message
                if message == 'in':
                    clock_result = await clock_in(webpage)
                    await context.bot.send_message(chat_id=incoming_chat_id, text=clock_result)
                elif message == 'out':
                    clock_result = await clock_out(webpage)
                    await context.bot.send_message(chat_id=incoming_chat_id, text=clock_result)

                await browser.close()
            else:
                await context.bot.send_message(chat_id=incoming_chat_id, text="Invalid command.")
    else:
        # Send a message if the user is not authorized
        await context.bot.send_message(chat_id=incoming_chat_id, text="Unauthorized user.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Initializes the bot by storing the chat ID in the keyring.
    If a chat ID already exists, it skips the initialization.

    Args:
        update (Update): Object containing the Telegram update data, such as the message text.
        context (ContextTypes.DEFAULT_TYPE): Bot context for interacting with Telegram API.

    Side Effects:
        Sets or retrieves chat ID in the keyring, and sends response messages to the user.
    """

    # Retrieve the effective chat ID from the incoming update
    chat_id = update.effective_chat.id

    # Try to retrieve an existing chat ID from the keyring
    existing_chat_id = keyring.get_password("autobot", "chat_id")

    # Check if an existing chat ID was found
    if not existing_chat_id:
        print("No existing chat ID found. Initializing...")

        # Store the chat ID in the keyring for future use
        keyring.set_password("autobot", "chat_id", str(chat_id))

        # Notify the user that the bot has been initialized
        await context.bot.send_message(chat_id=chat_id, text="Bot initialized.")
    else:
        print("Existing chat ID found. Skipping initialization.")

        # Notify the user that the bot is already initialized
        await context.bot.send_message(chat_id=chat_id, text="Bot already initialized.")


if __name__ == '__main__':
    # Record the bot's start time (convert it to a UNIX timestamp)
    global start_time
    start_time = datetime.now(timezone.utc).timestamp()

    # Check if a keyring entry for autoclock exists
    if not keyring.get_credential("autoclock", None):
        username = str(input('Enter your username: '))
        password = getpass('Enter your password: ')
        keyring.set_password("autoclock", username, password)
        print("Username and password stored in keyring.")

        # Clear the password variable
        password = None
    else:
        print("Username and password found in keyring.")

    # Check if a bot token is already stored in the keyring
    if not keyring.get_password("autobot", "bot_token"):
        # Prompt the user for the bot token
        new_token = str(input("Please enter your Telegram bot token: "))

        # Store the new bot token in the keyring
        keyring.set_password("autobot", "bot_token", new_token)
        print("Bot token stored in keyring.")
    else:
        print("Bot token found in keyring.")

    # Initialise message handler for non-command text messages
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)

    # Initialise command handler for the '/start' command
    start_handler = CommandHandler('start', start)

    # Retrieve the bot token from keyring and create an ApplicationBuilder instance
    bot_token = keyring.get_password("autobot", "bot_token")
    application = ApplicationBuilder().token(bot_token).build()

    # Register handlers with the bot application
    application.add_handler(message_handler)
    application.add_handler(start_handler)

    # Start the bot and enter the event-polling loop
    print("Bot started.")
    application.run_polling()
