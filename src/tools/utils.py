import os
import string
import random
from dotenv import load_dotenv
from configparser import ConfigParser


def load_config():
    FILE_PATH = os.path.dirname(os.path.realpath(__file__))
    load_dotenv(dotenv_path=FILE_PATH + '/../../.env')


def randomword(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))
