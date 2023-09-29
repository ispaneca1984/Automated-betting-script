from telethon import events
import asyncio
import threading
import sys
import sentry_sdk
import re
import time
from telethon.sync import TelegramClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import logging
from selenium.common.exceptions import NoSuchElementException  


# Initialize the TelegramClient and start it
api_id = '23317846'
api_hash = '12d80397ff6d8314ec87573648141263'
phone = '+359896351507'
channel_username = 'BetPracticeStudioBot'

client = TelegramClient(phone, api_id, api_hash)
processed_message_ids = set()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fetch_telegram_text(client):
    extracted_text = ""
    async for message in client.iter_messages(channel_username, limit=1):  # Use async for here
        last_message_text = message.text
        lines = last_message_text.split('\n')
        if len(lines) > 1:
            second_line = lines[1]
            match = re.search(r': (.*?)\(', second_line)
            if match:
                extracted_text = match.group(1)
                print(f"Extracted Text: {extracted_text}")
    return extracted_text


async def new_message_handler(event):
    logging.info(f"New message received: {event.text}")

    # Check if the message is already processed
    if event.message.id in processed_message_ids:
        logging.info(f"Message with ID {event.message.id} already processed. Skipping...")
        return

    # Check if the first line of the message contains '4.5'
    lines = event.text.split('\n')
    if lines:
        if '4.5' in lines[0]:
            # Extract the required text from the second line
            if len(lines) > 1:
                second_line = lines[1]
                match = re.search(r': (.*?)\(', second_line)
                if match:
                    text_between_colon_and_parentheses = match.group(1)
                    # Find the largest word in the extracted text
                    largest_word = find_largest_word(text_between_colon_and_parentheses)
                    logging.info(f"Largest Word: {largest_word}")
        else:
            # Handle the case when '4.5' is not in the first line
            logging.info("The first line does not contain '4.5'.")
    else:
        # Handle the case when there are no lines in the message
        logging.info("The message is empty or does not contain any lines.")

    finished_event = threading.Event()
    t = threading.Thread(target=selenium_thread, args=(finished_event, largest_word))
    t.start()
    finished_event.wait()

    # Add the message ID to the set of processed messages
    processed_message_ids.add(event.id)

    # Mark the message as read
    await event.message.mark_read()

def find_largest_word(text):
    words = text.split()
    if words:
        largest_word = max(words, key=len)
        return largest_word
    else:
        return None


async def main():
    # Initialize the Telethon client here in the main thread:
    async with TelegramClient(phone, api_id, api_hash) as client:
        client.add_event_handler(new_message_handler, events.NewMessage(chats=channel_username))
        await client.run_until_disconnected()


 
def selenium_thread(finished_event, extracted_text):
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    
    def highlight(element):
        driver.execute_script("arguments[0].setAttribute('style', 'background: yellow; border: 2px solid red;');", element)
        time.sleep(2)  # Pause for 2 seconds to observe the highlight
        driver.execute_script("arguments[0].setAttribute('style', '');", element)
    
    try:
        logging.info("selenium process started")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        driver_service = webdriver.chrome.service.Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=driver_service, options=options)

        # Open the website
        driver.get("https://black.betinasia.com/")

        # Login process
        login_button_xpath = '//*[@id="app"]/div/div/div[2]/div/div/button/span[1]'
        login_button = driver.find_element(By.XPATH, login_button_xpath)
        login_button.click()

        username_xpath = '//*[@id="app"]/div/div/div[2]/div/div/div[2]/div/input'
        password_xpath = '//*[@id="app"]/div/div/div[2]/div/div/div[3]/div/input'
        username_field = driver.find_element(By.XPATH, username_xpath)
        password_field = driver.find_element(By.XPATH, password_xpath)

        username_field.send_keys("Ispaneca1984")
        password_field.send_keys("Edsl@v0v")
        password_field.send_keys(Keys.RETURN)
        time.sleep(6)

       

        search_button_xpath = '//*[@id="app"]/div/div[1]/div[3]/button/div'

        # Use JavaScript to click the search button
        search_button_element = driver.find_element(By.XPATH, search_button_xpath)
        driver.execute_script("arguments[0].click();", search_button_element)

        # Send the extracted_text
        actions = ActionChains(driver)
        actions.send_keys(extracted_text)
        actions.perform()


        # Search for all elements that have the specific class 'elements__EventSearchResultDisplayElement-sc-1qok243-5 hwXwxC'
        containers = driver.find_elements(By.XPATH, "//*[@class='elements__EventSearchResultDisplayElement-sc-1qok243-5 hwXwxC']")
        print(f"Found {len(containers)} containers with class 'elements__EventSearchResultDisplayElement-sc-1qok243-5 hwXwxC'.")



        # Check if there are no containers
        if not containers:
            logging.error("Found 0 containers. Exiting the program.")
            sys.exit(1)

        element_found = False  # Flag to track if the desired element was found

        for container in containers:
            try:
                # Check if the container has a sub-element representing the red dot
                has_red_dot = False
                try:
                    red_dot_element = container.find_element(By.XPATH, ".//*[contains(@class, 'fSLvIR')]")
                    has_red_dot = True
                    logging.info("Found a sub-element representing the red dot.")
                except NoSuchElementException:
                    pass

                # Check if the container has a sub-element representing date or time
                has_date_or_time = False
                try:
                    date_or_time_element = container.find_element(By.XPATH, ".//*[contains(@class, 'flyWdD')]")
                    if "'" in date_or_time_element.text:
                        has_date_or_time = True
                        logging.info("Found the minute sign `'` in the element representing date or time.")
                except NoSuchElementException:
                    pass

                # Ensure at least one of the conditions is true
                if has_red_dot or has_date_or_time:
                    # Check if the container has a sub-element representing the event name
                    event_name_element = container.find_element(By.XPATH, ".//*[contains(@class, 'kNuQRS')]")
                    
                   # Check if the extracted text is present in the event name element (case-insensitive)
                    if extracted_text.lower() in event_name_element.text.lower():
                        logging.info(f"Extracted text '{extracted_text}' is present in the event name element: {event_name_element.text}.")

                        
                        # Click on the All Prices button element inside the container
                        all_prices_button_element = container.find_element(By.XPATH, ".//*[contains(@class, '1qok243-3')]")
                        driver.execute_script("arguments[0].click();", all_prices_button_element)
                        logging.info("Clicked on the All Prices button element inside one of the containers.")
                         
                        element_found = True  # Set the flag to True since the desired element was found
                        logging.info("EVENT FOUND!!")
                        break
                    else:
                        logging.info("Extracted text is not present in the event name element. Moving to the next container.")
                else:
                    logging.info("Neither conditions met. Moving to the next container.")
                    
            except Exception as e:
                logging.error(f"Error in container: {e}")

        time.sleep(3)


        # Locate the scroll bar element
        element = driver.find_element(By.CSS_SELECTOR, ".elements__SportContainerElement-sc-1kbbldw-0")
        highlight(element)
        logging.info("Located and highlighted the target element for scrolling actions.")


        try:
            # Click on the expand button on asian lines
            offer_group_element = driver.find_element(By.CSS_SELECTOR, ".elements__OfferGroupContainerElement-sc-1kbbldw-5:nth-child(3) .Icon__Icon2-sc-1dq4ptk-0")
            highlight(offer_group_element)
            offer_group_element.click()
            logging.info("Clicked on and highlighted the expand button at Asian Lines.")
            print("Clicked on the expand button at Asian Lines.")

        except Exception as e:
            logging.error(f"Error occurred: {e}")




        MAX_SCROLL_ATTEMPTS = 10  # Define a maximum number of scroll attempts to avoid infinite loop
        scroll_attempts = 0
        goalLine_found = False

        while scroll_attempts < MAX_SCROLL_ATTEMPTS:
            # Find all goalLines with the specified class
            goalLines = driver.find_elements(By.XPATH, "//*[contains(@class, 'elements__OfferLineOfferDisplayElement-sc-1kbbldw-16 bqbnod handicap')]")
            
            for goalLine in goalLines:
                if goalLine.text.strip() == '4.5':  # Check for exact match
                    goalLine_found = True
                    highlight(goalLine)  # Highlight the goalLine
                    # Scroll to the goalLine using scrollIntoView
                    driver.execute_script("arguments[0].scrollIntoView(true);", goalLine)
                    time.sleep(2)  # Wait for 2 seconds after scrolling
                    
                    # Find the second sibling's first child of the goalLine
                    second_sibling_first_child = goalLine.find_element(By.XPATH, "following-sibling::span[2]/*[1]")  # This targets the first child of the second sibling
                    highlight(second_sibling_first_child)  # Highlight the element
                    
                    try:
                        value = float(second_sibling_first_child.text)
                        if 1.2 <= value <= 1.5:
                            highlight(second_sibling_first_child)  # Highlight the child of the second sibling
                            driver.execute_script("arguments[0].click();", second_sibling_first_child)  # Click using JS
                            break
                        print("Odd out of range")
                    except ValueError:
                        continue
                    
                    break
            
            if goalLine_found:
                print("Found the goalLine with the exact value 4.5 and clicked on the first child of the second sibling!")
                break
            else:
                # If not found, scroll a bit to load more content
                driver.execute_script("window.scrollBy(0, 200);")  # Scroll down by 200 pixels
                time.sleep(2)  # Wait for 2 seconds after each scroll
                scroll_attempts += 1

        if not goalLine_found:
            print("Did not find the goalLine with the exact value 4.5 after scrolling multiple times.")
            pass
        

        # Switch to the new tab
        main_window_handle = driver.current_window_handle
        time.sleep(2)  # Wait for the new tab to open
        for handle in driver.window_handles:
            if handle != main_window_handle:
                driver.switch_to.window(handle)
                break
        logging.info("Switched to the new tab.")

        # Input "2" into the field
        actions = ActionChains(driver)
        actions.send_keys("2")
        actions.perform()
        logging.info("Entered '2' into the field.")

        # Press the TAB key to switch to the next field
        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB)
        actions.perform()
        logging.info("Pressed the TAB key.")

        # Input "1.2" into the next field
        actions = ActionChains(driver)
        actions.send_keys("1.2")
        actions.perform()
        logging.info("Entered '25' into the next field.")

        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB)
        actions.perform()
        logging.info("Pressed the TAB key.")

        actions = ActionChains(driver)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        logging.info("Pressed the Enter key.")

        # Switch to the new tab
        main_window_handle = driver.current_window_handle
        time.sleep(2)  # Wait for the new tab to open; you can also use WebDriverWait
        for handle in driver.window_handles:
            if handle != main_window_handle:
                driver.switch_to.window(handle)
                break
        logging.info("Switched to the new tab.")

        # Click on the next specified element using CSS_SELECTOR
        driver.find_element(By.CSS_SELECTOR, ".gYsAIl > .sc-gtsrHT").click()
        logging.info("Bet Done!!!")

         
    except Exception as e:
        logging.error(f"Selenium thread encountered an error: {e}")
    finally:
        # Signal that the selenium_thread has completed its execution
        finished_event.set()

        # Close the browser window and WebDriver tab
        driver.quit()
        logging.info("Closed the browser window and WebDriver tab.")

        # Step 2: Close the event loop
        new_loop.close()
    
if __name__ == "__main__":
    logging.info("Script started")
    asyncio.get_event_loop().set_debug(True)
    asyncio.run(main())
















