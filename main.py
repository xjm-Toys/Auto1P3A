import selenium.webdriver as webdriver
from config import CONFIG_INFO
from loguru import logger
from auto_manager import AutoManager
from selenium.common import exceptions as selexception

# # NOTE: config loguru
# logger.remove()
# logger.add("info.log", filter=lambda record: record["level"].name == "DEBUG")
# logger.add(sys.stderr, level = 'INFO')
# logger.add("info.log", filter=lambda record: record["level"].name == "INFO")

BBS_ADDRESS, LOCAL_USER_CONFIG_FILE_PATH = [
    CONFIG_INFO[k] for k in ('BBS_ADDRESS', 'LOCAL_USER_CONFIG_FILE_PATH')]


@logger.catch
def main():
    task2status = {task: False for task in [
        "login", "daily_award", "daily_question"]}
    auto_manager = AutoManager(
        logger, BBS_ADDRESS, LOCAL_USER_CONFIG_FILE_PATH)
    try:
        auto_manager.login_1p3a()
        auto_manager.get_1p3a_daily_award()
        # FIXME: captcha not captured
        # auto_manager.get_1p3a_daily_question()

    except selexception.TimeoutException as e:
        logger.exception(e)
    except selexception.NoSuchElementException:
        logger.exception(f"No such element -- Already got daily award?")
        task2status['daily_question'] = True
    except Exception as e:
        logger.exception(e)
    finally:
        try:
            logger.debug(f'start to check login status')
            task2status['login'] = auto_manager.is_logged_in_success()
            logger.debug(f'start to check daily award status')
            task2status['daily_award'] = auto_manager.is_daily_award_success()
            logger.debug(f'start to check daily question status')
            task2status["daily_question"] = auto_manager.is_daily_question_success()
            info = "\t".join(
                f"{task} {'success' if status else 'failed'}" for task, status in task2status.items())
            logger.info(info)
            auto_manager.driver.quit()
            exit(0)
        except Exception as e:
            logger.exception(e)


if __name__ == "__main__":
    main()
