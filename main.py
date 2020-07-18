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


# @ logger.catch
def main():
    task2status = {task: False for task in [
        "login", "daily_award", "daily_question"]}
    auto_manager = AutoManager(
        logger, BBS_ADDRESS, LOCAL_USER_CONFIG_FILE_PATH)
    try:
        auto_manager.login_1p3a()
        task2status['login'] = True

        auto_manager.get_1p3a_daily_award()
        task2status['daily_award'] = True

        auto_manager.get_1p3a_daily_question()
        task2status["daily_question"] = True

    except selexception.TimeoutException:
        logger.error(
            "Failed to login, may caused by incorrect username and password")
    except selexception.NoSuchElementException:
        logger.info(f"No such element -- Already got daily award?")
        task2status['daily_award'] = True
    except Exception:
        logger.debug("Unexpected exception")
    finally:
        info = "\t".join(
            f"{task} {'succeeded' if status else 'failed'}" for task, status in task2status.items())
        logger.info(info)
        auto_manager.driver.quit()
        exit(0)


if __name__ == "__main__":
    main()
