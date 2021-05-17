import json
from datetime import datetime
from time import sleep

from loguru import logger
from PIL import Image
from playwright.sync_api import BrowserContext, Page
import captcha

# selenium (https://www.selenium.dev/documentation/en/webdriver/browser_manipulation/)


class AutoManager:
    capcha_try_limit: int = 20
    capcha_delay: int = 4
    question2answer: dict = json.load(open("question_list.json"))

    def zoom_page(self):
        return
        # self.driver.execute_script("document.body.style.zoom = '10%'")

    @classmethod
    def login_1p3a(cls, page: Page, username: str, password: str):
        page.click("#um >> text=登录")
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button:has-text("登录")')

    @classmethod
    def get_daily_awards(cls, page: Page):
        # page.goto("https://www.1point3acres.com/bbs/dsu_paulsign-sign.html")
        # page.wait_for_selector("text=签到领奖")
        page.click(
            "text=开心难过郁闷无聊怒擦汗奋斗慵懒衰 今日最想说模式 自己填写 快速选择 我今天最想说 限制最少3个,最多50个中文字数 快速语句选择 今天把论坛帖子介绍给好基友了 >> img"
        )

        page.click("text=快速选择")
        img_path = f"capcha/{datetime.now().strftime('%m-%d %H:%M:%S')}.png"
        # page.click("text=请输入下面动画图片中的字符 >> img")
        sleep(3)
        page.wait_for_selector("text=请输入下面动画图片中的字符 >> img")
        capcha_element = page.query_selector("text=请输入下面动画图片中的字符 >> img")
        if not capcha_element:
            raise Exception("[capcha] capcha element not found")
        capcha_element.screenshot(path=img_path)
        capcha_result = cls.crack_capcha(img_path)
        page.fill('input[name="seccodeverify"]', capcha_result)

        with page.expect_navigation():
            page.click('input[type="submit"]')

    @staticmethod
    def crack_capcha(img_path: str) -> str:
        logger.debug(f"[crack] start: {img_path}")
        captcha_str = captcha.captcha_to_string(Image.open(img_path))
        logger.debug(f"[crack] result: {captcha_str}")
        return captcha_str

    def get_1p3a_daily_award(self):
        # NOTE: use chrome to find element by xpath: `$x('PATH')`
        logger.info("start to get daily award")

        for i in range(self.capcha_try_limit):
            logger.debug(f"start: ({i}) attamptation on cracking captcha")
            self.crack_daily_award()
            sleep(5)

    def query_question_bank(self, question):
        logger.debug(f"start query on question: ({question})")
        return self.question2answer[question]

    def get_1p3a_daily_question(self):
        logger.debug("start to get daily question")

        def reveal_question():
            self.driver_manager.find_and_click_by_xpath('//*[@id="um"]/p[3]/a[1]/img')
            # sleep(5)

        def get_right_option():
            # * query for right answers
            # question_body = self.driver.find_element_by_xpath(
            #     '//*[@id="myform"]/div[1]/span').text[5:]
            question_body = self.wait.until(
                ec.presence_of_element_located(
                    (By.XPATH, '//*[@id="myform"]/div[1]/span')
                )
            ).text[5:]
            try:
                right_answers = self.query_question_bank(question_body)
            except KeyError:
                logger.error(f"{question_body} not found in question bank")
                raise
            # * get available options
            options = [
                element.text.strip()
                for element in self.driver.find_elements_by_xpath(
                    "//div[@class='qs_option']"
                )
            ]
            logger.debug(f"options: {options}, answers: {right_answers}")
            # python note(https://stackoverflow.com/questions/9979970/why-does-python-use-else-after-for-and-while-loops)
            # * find right option
            for option in options:
                if option in right_answers:
                    return option
            else:
                logger.error(
                    f"no option found in answer list, options: {options}, right_answers:{right_answers}"
                )
                raise ValueError

        def crack_daily_question():
            # 1. reveal question
            reveal_question()

            # 2. click right option
            self.driver_manager.find_and_click_by_xpath(
                f'//*[contains(text(), "{right_option}")]'
            )

            # sleep(3)
            # 3. get captcha result
            self.driver_manager.find_and_click_by_xpath(
                "//*[contains(text(), '换一个')]"
            )  # change capcha
            sleep(4)
            result_str = self.driver_manager.get_cracked_string_by_xpath(
                '//*[@id="seccode_SA00"]/img'
            )
            # 4. fill in result
            self.driver.find_element_by_xpath(
                '//*[@id="seccodeverify_SA00"]'
            ).send_keys(result_str)
            # 5. click submit
            self.driver_manager.find_and_click_by_xpath("//*[contains(text(), '提交答案')]")

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
            logger.debug(f"start: ({i}) attamptation on cracking captcha")
            try:
                crack_daily_question()
                # sleep(5)
            except selexception.TimeoutException as option:
                logger.debug(
                    "Daily award should now be done(no required element detected)"
                )
                # FIXME: dev only
                pass
                # break

    # def find_and_click_by_xpath(driver, wait, xpath):
    #     element = wait.until(ec.presence_of_element_located((By.XPATH, xpath)))
    #     driver.execute_script("arguments[0].click();", element)

    def fill_captcha(self, driver, wait):
        res_text = ""
        correct_res = (
            "https://www.1point3acres.com/bbs/static/image/common/check_right.gif"
        )
        wrong_res = (
            "https://www.1point3acres.com/bbs/static/image/common/check_error.gif"
        )

        sleep(4)
        # cap_input_element = wait.until(ec.visibility_of_element_located((By.XPATH, "//input[@name='seccodeverify']")))
        cap_input_element = driver.find_element_by_xpath(
            "//input[@name='seccodeverify']"
        )
        trial = 1

        while res_text == "" or res_text != correct_res:  # 验证码解码错误

            if trial >= 20:
                return

            logger.debug(f"开始破解图形验证码，第{trial}次尝试...")
            # 重新获取验证码

            sleep(3)
            # get_new_captcha = wait.until(ec.visibility_of_element_located((By.XPATH, "//a[text()='换一个']")))
            find_and_click_by_xpath("//a[text()='换一个']")

            sleep(3)
            # captcha_img_element = wait.until(ec.visibility_of_element_located((By.XPATH, "//span[text()='输入下图中的字符']//img")))
            captcha_img_element = driver.find_element_by_xpath(
                '//*[@id="seccode_S00"]/img'
            )
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
                "//input[@name='answer'][@value='1']"
            )
            answer_element.click()

            # 等待错误或正确图标出现，为的是检验刚才输入的验证码是否正确
            # wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "img[src='static/image/common/check_right.gif'], img[src='static/image/common/check_error.gif']")) )
            sleep(4)

            check_image_element = driver.find_element_by_xpath(
                "//span[@id='checkseccodeverify_SA00']//img"
            )
            res_text = check_image_element.get_attribute("src")
            print(res_text)

            if res_text == correct_res:
                logger.debug("验证码输入正确 ^_^ ")
            else:
                logger.debug("验证码输入错误！")
                trial += 1
