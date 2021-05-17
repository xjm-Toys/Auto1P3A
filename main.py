import asyncio

# from playwright.async_api import async_playwright
import os
from time import sleep
from typing import Optional, Tuple

from loguru import logger
from playwright.sync_api import sync_playwright

from auto_manager import AutoManager
from local_config import LocalConfig

# # NOTE: config loguru
# logger.remove()
# logger.add("info.log", filter=lambda record: record["level"].name == "DEBUG")
# logger.add(sys.stderr, level = 'INFO')
# logger.add("info.log", filter=lambda record: record["level"].name == "INFO")


def get_user_config(local_config) -> Tuple[Optional[str], Optional[str]]:
    # * get credential info locally or from cloud
    logger.debug(f"[get_config] started")
    username, password = None, None
    if "USERNAME" in os.environ:
        logger.info("[get_config] from Heroku")
        username, password = os.environ.get("USERNAME"), os.environ.get("PASSWORD")
    else:
        logger.info("[get_config] from local file")
        username, password = local_config.username, local_config.password
    logger.info(f"[get_config] username:{username}, password:{password}")
    return username, password


@logger.catch
def main():
    username, password = get_user_config(LocalConfig)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.set_default_timeout(20 * 1000)

        page.goto("https://www.1point3acres.com/bbs/", wait_until="domcontentloaded")
        AutoManager.login_1p3a(page=page, username=username, password=password)
        sleep(5)

        page.goto("https://www.1point3acres.com/bbs/dsu_paulsign-sign.html")
        # page.click("text=签到领奖")
        for i in range(10):
            logger.debug(f"[daily signin] start {i} attempt")
            if not page.is_visible('input[type="submit"]'):
                logger.info("[daily signin] done!!")
                break
            AutoManager.get_daily_awards(page=page)
        else:
            logger.info("[daily signin] maximum attempts failed")


if __name__ == "__main__":
    main()
