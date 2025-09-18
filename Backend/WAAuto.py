import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class WhatsAppController:
    def __init__(self, driver_path=None, browser='chrome'):
        """
        Initializes the WhatsApp controller
        :param driver_path: Path to web driver executable
        :param browser: Browser type ('chrome' or 'firefox')
        """
        self.driver = None
        self.browser = browser.lower()
        self.driver_path = driver_path
        self.wait_timeout = 30

    def initialize_driver(self):
        """Initialize the WebDriver based on browser selection"""
        if self.browser == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-notifications')
            options.add_argument('--user-agent=Mozilla/5.0')
            if self.driver_path:
                self.driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
        elif self.browser == 'firefox':
            options = webdriver.FirefoxOptions()
            options.set_preference('dom.webnotifications.enabled', False)
            if self.driver_path:
                self.driver = webdriver.Firefox(executable_path=self.driver_path, options=options)
            else:
                self.driver = webdriver.Firefox(options=options)
        else:
            raise ValueError("Unsupported browser. Choose 'chrome' or 'firefox'")
        
        self.driver.maximize_window()

    def login(self):
        """
        Logs into WhatsApp Web and waits for user to scan QR code
        """
        if not self.driver:
            self.initialize_driver()
            
        self.driver.get('https://web.whatsapp.com/')
        print("Please scan QR code within 60 seconds")
        
        # Wait for login completion
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@title="New chat"]'))
            )
            print("Login successful!")
            time.sleep(3)  # Additional stabilization time
            return True
        except TimeoutException:
            print("Login timed out. QR code not scanned.")
            return False

    def _select_contact(self, contact_name):
        """
        Internal method to select a contact
        :param contact_name: Name of contact to select
        """
        search_box = WebDriverWait(self.driver, self.wait_timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@title,"Search input textbox")]'))
        )
        search_box.click()
        search_box.send_keys(contact_name)
        
        try:
            contact = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[@title="{contact_name}"]'))
            )
            contact.click()
            return True
        except TimeoutException:
            print(f"Contact '{contact_name}' not found")
            return False

    def send_message(self, contact_name, message):
        """
        Sends a message to specified contact
        :param contact_name: Name of contact
        :param message: Message text to send
        """
        if not self._select_contact(contact_name):
            return False
            
        input_box = WebDriverWait(self.driver, self.wait_timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@title="Type a message"]'))
        )
        input_box.send_keys(message)
        input_box.send_keys('\n')
        time.sleep(1)  # Ensure message is sent
        return True

    def read_notifications(self):
        """
        Reads unread notifications/messages
        :return: List of unread notifications
        """
        notifications = []
        try:
            unread_indicators = self.driver.find_elements(
                By.XPATH, '//div[@class="_akbu"]//div[@aria-label="Unread"]'
            )
            
            for indicator in unread_indicators:
                contact = indicator.find_element(By.XPATH, './ancestor::div[@role="row"]')
                contact_name = contact.find_element(By.XPATH, './/span[@title]').get_attribute('title')
                preview = contact.find_element(By.XPATH, './/span[@class="_akct"]').text
                notifications.append({'contact': contact_name, 'preview': preview})
                
        except NoSuchElementException:
            pass
            
        return notifications

    def reply_notification(self, contact_name, message):
        """
        Replies to the latest notification from a contact
        :param contact_name: Contact name
        :param message: Reply message
        """
        return self.send_message(contact_name, message)

    def make_voice_call(self, contact_name):
        """
        Initiates a voice call to specified contact
        :param contact_name: Contact name
        """
        if not self._select_contact(contact_name):
            return False
            
        try:
            call_button = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@title="Voice call"]'))
            )
            call_button.click()
            time.sleep(3)  # Wait for call initialization
            return True
        except TimeoutException:
            print("Voice call button not found")
            return False

    def make_video_call(self, contact_name):
        """
        Initiates a video call to specified contact
        :param contact_name: Contact name
        """
        if not self._select_contact(contact_name):
            return False
            
        try:
            video_button = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@title="Video call"]'))
            )
            video_button.click()
            time.sleep(3)  # Wait for call initialization
            return True
        except TimeoutException:
            print("Video call button not found")
            return False

    def end_call(self):
        """
        Ends current active call
        """
        try:
            end_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="End call"]'))
            )
            end_button.click()
            time.sleep(2)  # Wait for call termination
            return True
        except (NoSuchElementException, TimeoutException):
            print("No active call found")
            return False

    def close(self):
        """Closes the browser session"""
        if self.driver:
            self.driver.quit()
            self.driver = None

# Example usage
if __name__ == "__main__":
    # Initialize controller
    wa = WhatsAppController(browser='chrome')
    
    if wa.login():
        # Send message
        wa.send_message("John Doe", "Hello from Python!")
        
        # Read notifications
        print("Unread notifications:", wa.read_notifications())
        
        # Make calls (uncomment to use)
        # wa.make_voice_call("John Doe")
        # time.sleep(5)
        # wa.end_call()
        
        # wa.make_video_call("John Doe")
        # time.sleep(5)
        # wa.end_call()
        
        wa.close()