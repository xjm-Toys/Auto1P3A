from datetime import datetime
from time import sleep
import captcha
import os
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions as selexception
import platform
import uuid
import json
from PIL import Image
from pathlib import Path
import os
import urllib
import sys

# selenium (https://www.selenium.dev/documentation/en/webdriver/browser_manipulation/)


class ChromeDriverManager():
    def __init__(self, driver, wait, logger):
        self.driver, self.wait, self.logger = driver, wait, logger

    def get_cracked_string_by_xpath(self, xpath):
        self.logger.debug(f"start to capture capcha image")
        CAPTCHA_IMG_PATH = f"capcha_{datetime.now().strftime('%m-%d %H:%M:%S')}.png"
        # CAPTCHA_IMG_PATH = f"capcha_data/capcha_{datetime.now().strftime('%m-%d %H:%M:%S')}.png"
        # Path(CAPTCHA_IMG_PATH).parent.mkdir(parents=True, exist_ok=True)
        sleep(2)
        captcha_img_element = self.wait.until(
            ec.visibility_of_element_located((By.XPATH, xpath)))
        captcha_img_element.location_once_scrolled_into_view
        self.logger.debug(f"captcha_img_element: {captcha_img_element}")
        with open(CAPTCHA_IMG_PATH, "wb") as f:
            f.write(captcha_img_element.screenshot_as_png)
        self.logger.debug(f"start to convert capcha to string")
        captcha_str = captcha.captcha_to_string(Image.open(CAPTCHA_IMG_PATH))
        self.logger.debug(f"captcha convert result: {captcha_str}")
        return captcha_str

    def find_and_click_by_xpath(self, xpath):
        try:
            element = self.wait.until(
                ec.visibility_of_element_located((By.XPATH, xpath)))
            # element = self.driver.find_element_by_xpath(xpath)
            self.driver.execute_script("arguments[0].click();", element)
        except:
            raise


class AutoManager():
    def __init__(self, logger, address, local_config_file_path, capcha_try_limit=20, capcha_delay=4):
        self.logger, self.capcha_try_limit = logger, capcha_try_limit
        self.driver, self.wait = self.get_chrome_driver(address)
        self.driver_manager = ChromeDriverManager(
            self.driver, self.wait, logger)
        self.username, self.password = self.get_user_config(
            local_config_file_path)
        with open("question_list.json") as f:
            self.question2answer = json.load(f)
        self.capcha_delay = capcha_delay

    def zoom_page(self):
        return
        # self.driver.execute_script("document.body.style.zoom = '10%'")

    def get_chrome_driver(self, address):
        # * init webdriver, using chrome
        # 设置为执行操作时，不需要等待页面完全加载
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"
        chrome_driver = Chrome(desired_capabilities=caps)
        chrome_driver.get(address)
        # (https://stackoverflow.com/questions/28111539/can-we-zoom-the-browser-window-in-python-selenium-webdriver)
        # chrome_driver.get("chrome://settings/")
        # chrome_driver.execute_script(
        #     "chrome.settingsPrivate.setDefaultZoom(0.4);")
        chrome_driver.maximize_window()
        webdriver_wait = WebDriverWait(chrome_driver, 3)
        return chrome_driver, webdriver_wait

    def get_user_config(self, local_config_file_path):
        # * get credential info locally or from cloud
        self.logger.debug(f"Started to get username and password")
        username, password = None, None
        if "USERNAME" in os.environ:
            self.logger.info("Load user account info from heroku config")
            [username, password] = [os.environ.get(
                "USERNAME"), os.environ.get("PASSWORD")]
        else:
            self.logger.info("Get user account info from local file")
            with open(local_config_file_path) as config:
                user_config = json.load(config)
                [username, password] = [
                    user_config["USERNAME"], user_config["PASSWORD"]]
        self.logger.info(f"username:{username}, password:{password}")
        return [username, password]

    def login_1p3a(self):
        try:
            self.driver_manager.driver.get('https://www.1point3acres.com/bbs/')
            self.zoom_page()
            self.logger.info("started to login")
            # * fill in username & password
            self.logger.debug(f'start fill in username: {self.username}')
            self.wait.until(ec.visibility_of_element_located(
                (By.XPATH, '//*[@id="ls_username"]'))).send_keys(self.username)
            # self.driver_manager.driver.find_element_by_css_selector(
            #     )
            self.logger.debug(f'start to fill in password: {self.password}')
            self.wait.until(ec.visibility_of_element_located(
                (By.XPATH, '//*[@id="ls_password"]'))).send_keys(self.password)
            # * click login and wait until page loaded
            self.driver_manager.find_and_click_by_xpath("//em[text()='登录']")
            # FIXME: figure why after remove `sleep`, then wait.until not working below
            sleep(2)
            self.wait.until(ec.presence_of_element_located(
                (By.XPATH, '//a[text()="退出"]')))
        except selexception.TimeoutException as e:
            self.logger.debug(
                'Daily award should now be done?(no required element detected)')
        self.logger.info("Login success!")

    def is_logged_in_success(self):
        self.logger.debug(f'start to go to main page')
        self.driver_manager.driver.get('https://www.1point3acres.com/bbs/')
        self.zoom_page()
        sleep(3)
        try:
            self.logger.debug(f'try to find 退出')
            self.driver.find_element_by_xpath(
                "//*[contains(text(), '退出')]")
            self.logger.debug(f'element: 退出 found, meaning is logged in')
            self.driver.back()
            return True
        except selexception.NoSuchElementException:
            self.logger.debug(f'element: 退出 found, meaning is not logged in')
            self.driver.back()
            return False

    def is_daily_award_success(self):
        self.logger.debug(f'start to go to daily award page')
        self.driver_manager.driver.get(
            'https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign')
        self.zoom_page()
        sleep(3)
        try:
            self.logger.debug(f'try to find "您今天已经签到过了或者签到时间还未开始"')
            self.driver.find_element_by_xpath(
                "//*[contains(text(), '您今天已经签到过了或者签到时间还未开始')]")
            self.logger.debug(
                f'element:您今天已经签到过了或者签到时间还未开始 found, meaning daily award is gotten')
            self.driver.back()
            return True
        except selexception.NoSuchElementException:
            self.logger.debug(
                f'element:您今天已经签到过了或者签到时间还未开始 not found, meaning daily award is not gotten')
            self.driver.back()
            return False

    def is_daily_question_success(self):
        self.logger.debug(f'start to go to main page')
        self.driver_manager.driver.get(
            'https://www.1point3acres.com/bbs/')
        self.zoom_page()
        # TODO: better way?
        sleep(3)
        try:
            self.logger.debug(f'try to click and reveal question ')
            self.driver_manager.find_and_click_by_xpath(
                '//*[@id="um"]/p[3]/a[1]/img')
            # TODO: better way?
            sleep(3)
            self.logger.debug(f'try to find "提交答案"')
            self.driver.find_element_by_xpath("//*[contains(text(), '提交答案')]")
            self.logger.debug(
                f'element:提交答案 found, meaning daily question is completed')
            self.driver.back()
            return False
        except selexception.NoSuchElementException:
            self.logger.debug(
                f'element:提交答案 not found, meaning daily question is not completed')
            self.driver.back()
            return True

    def is_logged_in_success(self):
        self.driver_manager.driver.get('https://www.1point3acres.com/bbs/')
        self.zoom_page()
        sleep(3)
        try:
            self.driver.find_element_by_xpath(
                "//*[contains(text(), '退出')]")
            self.driver.back()
            return True
        except selexception.NoSuchElementException:
            self.driver.back()
            return False

    def crack_daily_award(self):
        # * click form items: “开心” and  “快速留言”
        self.logger.debug("start to go to 签到领奖 page")
        self.driver_manager.driver.get(
            'https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign')
        self.zoom_page()
        sleep(5)
        self.logger.debug("start to select 心情")
        self.driver_manager.find_and_click_by_xpath(
            '//*[@id="kx"]/center/img')
        self.logger.debug("start to click 选择快速留言")
        self.driver_manager.find_and_click_by_xpath(
            "//*[contains(text(), '快速选择')]")  # change capcha
        # * crack captcha and click submit
        self.logger.debug("start to crack captcha and click submit")
        # 4. change capcha
        self.logger.debug("start to select 换一个")
        self.driver_manager.find_and_click_by_xpath(
            '//*[contains(text(), "换一个")]')
        sleep(self.capcha_delay)
        # 2. get result
        result_str = self.driver_manager.get_cracked_string_by_xpath(
            '//*[@id="seccode_S00"]/img')

        # 3. fill in result and click submit
        self.logger.debug("start to fill in result")
        self.driver.find_element_by_xpath(
            '//*[@id="seccodeverify_S00"]').send_keys(result_str)
        self.logger.debug("start to click submit")
        self.driver_manager.find_and_click_by_xpath(
            '//*[@id="ct"]/div[1]/div[1]/form/table[4]/tbody/tr/td/div/input')

    def get_1p3a_daily_award(self):
        # NOTE: use chrome to find element by xpath: `$x('PATH')`
        self.logger.info("start to get daily award")

        for i in range(self.capcha_try_limit):
            self.logger.debug(f'start: ({i}) attamptation on cracking captcha')
            try:
                self.crack_daily_award()
                sleep(5)
            except selexception.TimeoutException as e:
                self.logger.debug(
                    'Daily award should now be done(no required element detected)')
                break

        # 等待签到框消失
        # self.wait.until(ec.invisibility_of_element_located((By.XPATH, "//div[@id='fwin_dsu_paulsign']")))

        # 等待 “签到领奖！” 链接消失
        # wait.until(ec.invisibility_of_element_located((By.XPATH, "//font[text()='签到领奖!']")))

        self.logger.info("Getting daily award successfully completed")

    def query_question_bank(self, question):
        self.logger.debug(f"start query on question: ({question})")
        return self.question2answer[question]

    def get_1p3a_daily_question(self):
        self.logger.debug("start to get daily question")

        def reveal_question():
            self.driver_manager.find_and_click_by_xpath(
                '//*[@id="um"]/p[3]/a[1]/img')
            # sleep(5)

        def get_right_option():
            # * query for right answers
            # question_body = self.driver.find_element_by_xpath(
            #     '//*[@id="myform"]/div[1]/span').text[5:]
            question_body = self.wait.until(
                ec.presence_of_element_located((By.XPATH, '//*[@id="myform"]/div[1]/span'))).text[5:]
            try:
                right_answers = self.query_question_bank(question_body)
            except KeyError:
                self.logger.error(
                    f"{question_body} not found in question bank")
                raise
            # * get available options
            options = [element.text.strip(
            ) for element in self.driver.find_elements_by_xpath("//div[@class='qs_option']")]
            self.logger.debug(f'options: {options}, answers: {right_answers}')
            # python note(https://stackoverflow.com/questions/9979970/why-does-python-use-else-after-for-and-while-loops)
            # * find right option
            for option in options:
                if option in right_answers:
                    return option
            else:
                self.logger.error(
                    f'no option found in answer list, options: {options}, right_answers:{right_answers}')
                raise ValueError

        def crack_daily_question():
            # 1. reveal question
            reveal_question()

            # 2. click right option
            self.driver_manager.find_and_click_by_xpath(
                f'//*[contains(text(), "{right_option}")]')

            # sleep(3)
            # 3. get captcha result
            self.driver_manager.find_and_click_by_xpath(
                "//*[contains(text(), '换一个')]")  # change capcha
            sleep(4)
            result_str = self.driver_manager.get_cracked_string_by_xpath(
                '//*[@id="seccode_SA00"]/img')
            # 4. fill in result
            self.driver.find_element_by_xpath(
                '//*[@id="seccodeverify_SA00"]').send_keys(result_str)
            # 5. click submit
            self.driver_manager.find_and_click_by_xpath(
                "//*[contains(text(), '提交答案')]")

        reveal_question()
        try:
            right_option = get_right_option()
        except KeyError as e:
            # * question not found in question bank
            return
        except ValueError:
            # * option not found in right_answers
            return
        for i in range(self.capcha_try_limit):
            self.logger.debug(f'start: ({i}) attamptation on cracking captcha')
            try:
                crack_daily_question()
                # sleep(5)
            except selexception.TimeoutException as option:
                self.logger.debug(
                    'Daily award should now be done(no required element detected)')
                # FIXME: dev only
                pass
                # break

    def find_and_click_by_xpath(driver, wait, xpath):
        element = wait.until(
            ec.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].click();", element)

    def fill_captcha(driver, wait):

        res_text = ""
        correct_res = "https://www.1point3acres.com/bbs/static/image/common/check_right.gif"
        wrong_res = "https://www.1point3acres.com/bbs/static/image/common/check_error.gif"

        sleep(4)
        # cap_input_element = wait.until(ec.visibility_of_element_located((By.XPATH, "//input[@name='seccodeverify']")))
        cap_input_element = driver.find_element_by_xpath(
            "//input[@name='seccodeverify']")
        trial = 1

        while res_text == "" or res_text != correct_res:  # 验证码解码错误

            if trial >= 20:
                return

            self.logger.debug(f"开始破解图形验证码，第{trial}次尝试...")
            # 重新获取验证码

            sleep(3)
            # get_new_captcha = wait.until(ec.visibility_of_element_located((By.XPATH, "//a[text()='换一个']")))
            find_and_click_by_xpath("//a[text()='换一个']")

            sleep(3)
            # captcha_img_element = wait.until(ec.visibility_of_element_located((By.XPATH, "//span[text()='输入下图中的字符']//img")))
            captcha_img_element = driver.find_element_by_xpath(
                '//*[@id="seccode_S00"]/img')
            # src = captcha_img_element.get_attribute("src")

            # NOTE: for whole screen
            # driver.save_screenshot('screenshot.png')
            # * capture img
            # loc = captcha_img_element.location
            # size = captcha_img_element.size
            # left, right = loc['x'], loc['x'] + size['width']
            # top, bottom = loc['y'], loc['y'] + size['height']
            # captcha_img = scrsht.crop((left, top, right, bottom))
            # captcha_img.save("captcha.png")

            # * test
            captcha_img = cap_input_element.screenshot_as_png
            with open("captcha.png", "wb") as f:
                f.write(captcha_img_element.screenshot_as_png)

            # * image -> captcha
            captcha_text = captcha.captcha_to_string(Image.open("captcha.png"))
            logger.debug(f"图形验证码破解结果: {captcha_text}")

            cap_input_element.send_keys(captcha_text)

            # 选择答案以激活正确或错误图标
            answer_element = driver.find_element_by_xpath(
                "//input[@name='answer'][@value='1']")
            answer_element.click()

            # 等待错误或正确图标出现，为的是检验刚才输入的验证码是否正确
            # wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "img[src='static/image/common/check_right.gif'], img[src='static/image/common/check_error.gif']")) )
            sleep(4)

            check_image_element = driver.find_element_by_xpath(
                "//span[@id='checkseccodeverify_SA00']//img")
            res_text = check_image_element.get_attribute("src")
            print(res_text)

            if res_text == correct_res:
                logger.debug("验证码输入正确 ^_^ ")
            else:
                logger.debug("验证码输入错误！")
                trial += 1
