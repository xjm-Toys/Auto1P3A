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
# # driver.get_screenshot_as_file('test_setting.png')

driver = Chrome(desired_capabilities=caps)
def expand_shadow_element(element):
    shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
    return shadow_root


driver.get('chrome://settings/')

root1=driver.find_element_by_xpath("*//settings-ui")
shadow_root1 = expand_shadow_element(root1)
container= shadow_root1.find_element_by_id("container")

root2= container.find_element_by_css_selector("settings-main")
shadow_root2 = expand_shadow_element(root2)

root3=shadow_root2.find_element_by_css_selector("settings-basic-page")

shadow_root3 = expand_shadow_element(root3)
basic_page = shadow_root3.find_element_by_id("basicPage")

settings_section= basic_page.find_element_by_xpath(".//settings-section[@section='appearance']")

root4= settings_section.find_element_by_css_selector("settings-appearance-page")
shadow_root4=expand_shadow_element(root4)

settings_animated_pages= shadow_root4.find_element_by_id("pages")
neon_animatable=settings_animated_pages.find_element_by_css_selector("neon-animatable")

zoomLevel= neon_animatable.find_element_by_xpath(".//select[@id='zoomLevel']/option[@value='0.5']")
zoomLevel.click()


driver.get("https://www.google.co.uk/")