import time

import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from engines import check_attribute

PATH = r'C:\Program Files (x86)\chromedriver.exe'


class ChatGPT:
    """

    """

    URL = 'https://chat.openai.com/chat'

    def __init__(self,
                 sleep_time=5,
                 silent=False,
                 *driver_options):
        self.sleep_time = sleep_time
        self.silent = silent
        self._paragraph_len = 0

        self.driver = uc.Chrome(service=Service(ChromeDriverManager().install()))

    def __repr__(self):
        return self.__class__.__name__

    def _find_element(self, pattern: tuple):
        return WebDriverWait(self.driver,
                             self.sleep_time).until(EC.presence_of_element_located(pattern))

    def _click_button(self, text):
        elem = self._find_element((By.XPATH, f'//button[normalize-space()="{text}"]'))
        elem.click()

    def _close_windows(self):
        self._click_button('Next')
        self._click_button('Next')
        self._click_button('Done')

    def _parse_answer(self, prefix):
        # parse answers paragraph
        paragraphs = self.driver.find_elements(By.TAG_NAME, 'p')[self._paragraph_len:-1]
        # update control state
        self._paragraph_len += len(paragraphs)
        # return formatted answer
        answer = ''.join([p.text + prefix for p in paragraphs])
        return answer

    def connect(self):
        self.driver.get(ChatGPT.URL)
        self._connected = True
        return True

    @check_attribute('_connected')
    def login(self,
              email,
              password):
        # open login form
        self._click_button('Log in')
        # insert username
        username_element = self._find_element((By.ID, 'username'))
        username_element.send_keys(email)
        self._click_button('Continue')
        # insert password
        password_element = self._find_element((By.ID, 'password'))
        password_element.send_keys(password)
        self._click_button('Continue')
        # close initial window
        self._close_windows()
        self._logged = True
        return True

    @check_attribute('_logged', '_connected')
    def reset_thread(self):
        self._click_button('Reset Thread')
        # reset control attributes
        delattr(self, '_first_call')
        self._paragraph_len = 0
        return True

    @check_attribute('_logged', '_connected')
    def __len__(self):
        return len(self.driver.find_elements(By.TAG_NAME, 'p')) - 1

    @check_attribute('_is_logged', '_connected')
    def log_out(self):
        self._click_button('Log out')
        self._logged = False
        return True

    @check_attribute('_logged', '_connected')
    def __call__(self,
                 prompt,
                 answer_wait_time=15,
                 format_paragraph=False,
                 sleep_time=None):
        # format for the answer
        prefix = '\n ' if format_paragraph else ''
        # send prompt
        self.driver.find_element(By.TAG_NAME, 'textarea').send_keys(prompt)

        buttons = self.driver.find_elements(By.TAG_NAME, 'button')
        try:
            buttons[-1].click()
        except:
            pass
        # update control state
        self._first_call = True
        # wait for answer
        time.sleep(answer_wait_time)
        # parse answer
        answer = self._parse_answer(prefix)
        print(answer)
        return answer

    @check_attribute('_logged', '_connected', '_first_call')
    def try_again(self,
                  answer_wait_time=10,
                  format_paragraph=False):
        prefix = '\n ' if format_paragraph else ''
        # update control state
        self._first_call = False
        self._click_button('Try again')
        # wait for answer
        time.sleep(answer_wait_time)
        # parse answer
        answer = self._parse_answer(prefix)
        return answer

    def quit(self):
        self.driver.quit()
