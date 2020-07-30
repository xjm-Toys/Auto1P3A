import captcha
from auto_manager import AutoManager
from loguru import logger
from config import CONFIG_INFO
import selenium.webdriver as webdriver
from datetime import datetime
from time import sleep
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
caps = DesiredCapabilities().CHROME
# driver = Chrome(desired_capabilities=caps)
# # driver.get("https://www.1point3acres.com/bbs/")
# wait = WebDriverWait(driver, 3)
# driver.maximize_window()
# driver.execute_script("document.body.style.zoom='50%'")
# driver.get("chrome://settings/")
# driver.execute_script("chrome.settingsPrivate.setDefaultZoom(0.4);")

# def expand_shadow_element(element):
#     shadow_root = driver.execute_script(
#         'return arguments[0].shadowRoot', element)
#     return shadow_root


# def test_chrome_setting_zoom():
#     driver.get('chrome://settings/')

#     root1 = driver.find_element_by_xpath("*//settings-ui")
#     shadow_root1 = expand_shadow_element(root1)
#     container = shadow_root1.find_element_by_id("container")

#     root2 = container.find_element_by_css_selector("settings-main")
#     shadow_root2 = expand_shadow_element(root2)

#     root3 = shadow_root2.find_element_by_css_selector("settings-basic-page")

#     shadow_root3 = expand_shadow_element(root3)
#     basic_page = shadow_root3.find_element_by_id("basicPage")

#     settings_section = basic_page.find_element_by_xpath(
#         ".//settings-section[@section='appearance']")

#     root4 = settings_section.find_element_by_css_selector(
#         "settings-appearance-page")
#     shadow_root4 = expand_shadow_element(root4)

#     settings_animated_pages = shadow_root4.find_element_by_id("pages")
#     neon_animatable = settings_animated_pages.find_element_by_css_selector(
#         "neon-animatable")

#     zoomLevel = neon_animatable.find_element_by_xpath(
#         ".//select[@id='zoomLevel']/option[@value='0.5']")
#     zoomLevel.click()


# def test_body_zoom():
#     driver.get("https://www.google.co.uk/")
#     driver.execute_script("document.body.style.zoom = '20%'")
#     take_screen_shot()



BBS_ADDRESS, LOCAL_USER_CONFIG_FILE_PATH = [
    CONFIG_INFO[k] for k in ('BBS_ADDRESS', 'LOCAL_USER_CONFIG_FILE_PATH')]

auto_manager = AutoManager(logger, BBS_ADDRESS, LOCAL_USER_CONFIG_FILE_PATH)


auto_manager.driver_manager.driver.get('https://www.1point3acres.com/bbs/')
auto_manager.logger.info("started to login")
# * fill in username & password
auto_manager.logger.debug(
    f'start fill in username: {auto_manager.username}')
auto_manager.wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="ls_username"]'))).send_keys(auto_manager.username)
# auto_manager.driver_manager.driver.find_element_by_css_selector(
#     )
auto_manager.logger.debug(
    f'start to fill in password: {auto_manager.password}')
auto_manager.wait.until(ec.visibility_of_element_located(
    (By.XPATH, '//*[@id="ls_password"]'))).send_keys(auto_manager.password)
# * click login and wait until page loaded
auto_manager.driver_manager.find_and_click_by_xpath("//em[text()='登录']")
# FIXME: figure why after remove `sleep`, then wait.until not working below
sleep(2)
auto_manager.wait.until(ec.presence_of_element_located(
    (By.XPATH, '//a[text()="退出"]')))

auto_manager.logger.debug("start to go to 签到领奖 page")
auto_manager.driver_manager.driver.get(
    'https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign')
sleep(5)
auto_manager.logger.debug("start to select 心情")
auto_manager.driver_manager.find_and_click_by_xpath(
    '//*[@id="kx"]/center/img')
auto_manager.logger.debug("start to click 选择快速留言")
auto_manager.driver_manager.find_and_click_by_xpath(
    "//*[contains(text(), '快速选择')]")  # change capcha
# * crack captcha and click submit
auto_manager.logger.debug("start to crack captcha and click submit")
# 4. change capcha
auto_manager.logger.debug("start to select 换一个")
auto_manager.driver_manager.find_and_click_by_xpath(
    '//*[contains(text(), "换一个")]')
auto_manager.driver.execute_script("window.scrollTo(0, Y)")

auto_manager.driver.get_screenshot_as_file('test_setting.png')

captcha_img_element = auto_manager.wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="seccode_S00"]/img')))

captcha_img_element.location_once_scrolled_into_view
