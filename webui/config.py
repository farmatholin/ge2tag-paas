from pymongo import MongoClient

WTF_CSRF_ENABLED = True
SECRET_KEY = 'olaComradeSecret'
DB_NAME = 'gtbaas'

DATABASE = MongoClient()[DB_NAME]
CONTAINERS_COLLECTION = DATABASE.containers
USERS_COLLECTION = DATABASE.users
STATISTIC_COLLECTION = DATABASE.statistic

DEBUG = True

TOOL_SERVER = "g2tbaas.loc"
TOOL_PORT = 8000