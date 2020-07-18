import unittest
from loguru import logger
# simple_solver(https://github.com/ptigas/simple-CAPTCHA-solver)
from captcha_decoder import decoder
from captcha import captcha_to_string
from PIL import Image
from auto_manager import AutoManager
from main import BBS_ADDRESS, LOCAL_USER_CONFIG_FILE_PATH

path2expected = {
    'capcha_07-12 00:33:15.png': 'CTCH',
    'capcha_07-12 00:28:33.png': 'CP8F',
    'capcha_07-12 00:26:43.png': 'CWJB',
    'capcha_07-11 23:34:23.png': 'CQ3R'
}


def format_captcha_result(expected, actual):
    result = "True" if expected == actual else "False"
    return f"{result} {expected} {actual}"


class TestAutoManager(unittest.TestCase):
    def setUp(self):
        self.auto_manager = AutoManager(
            logger, BBS_ADDRESS, LOCAL_USER_CONFIG_FILE_PATH)

    def test_simple_solver(self):
        solver = decoder
        print("\n".join(format_captcha_result(answer, solver(path)) for path,
                        answer in path2expected.items()))

    def test_solver(self):
        def solver(path):
            return captcha_to_string(Image.open(path))
        print("\n".join(format_captcha_result(expected, solver(path)) for path,
                        expected in path2expected.items()))

    def test_query_question_bank(self):
        questions = ['回答别人的私信提问还需要消耗我5大米怎么办',
                     "Apollo 11是哪一年登月的？", "下面哪个说法错误？"]
        for q in questions:
            try:
                print(self.auto_manager.query_question_bank(q))
            except KeyError:
                print(f"question: {q} not in question bank!")
#


if __name__ == '__main__':
    unittest.main()
