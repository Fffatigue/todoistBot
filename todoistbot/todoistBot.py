import argparse
from configparser import RawConfigParser

import telebot
from expiringdict import ExpiringDict
from todoist_api_python.api import TodoistAPI

parser = argparse.ArgumentParser(description='Telegram bot for Todoist.')
parser.add_argument('--config', dest='conf', help='Config destination', required=True)

args = parser.parse_args()

config = RawConfigParser()
config.read(args.conf)

bot = telebot.TeleBot(config.get('tokensSection', 'telegram.token'))
api = TodoistAPI(config.get('tokensSection', 'todoist.token'))

tg_uid = config.getint('settingsSection', 'telegram.user_id')

cache = ExpiringDict(max_len=100, max_age_seconds=600)


def markdown_task(t):
    return '• ' + t.content


def test_access(m):
    return tg_uid is None or m.chat.id == tg_uid


def find_inbox_project_id():
    projects = api.get_projects()
    for project in projects:
        if project.is_inbox_project:
            return project.id


@bot.message_handler(func=test_access, commands=["start"])
def start(m):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("/notSortedList")
    markup.add(button)
    bot.send_message(m.chat.id, 'Todoist bot started.', reply_markup=markup)


@bot.message_handler(func=test_access, commands=["notSortedList"])
def not_sorted_list(m):
    tasks = api.get_tasks(project_id=inbox_project_id)
    bot.send_message(m.chat.id, '\n'.join(map(markdown_task, tasks)))


@bot.message_handler(func=test_access, content_types=["text"])
def handle_text(m):
    task = api.add_task(content=m.text)
    cache[m.id] = task.id


@bot.edited_message_handler(func=test_access, content_types=["text"])
def handle_text(m):
    task_id = cache[m.id]
    if task_id is None:
        bot.send_message(m.chat.id, 'Is too late for editing message')
        return
    api.update_task(task_id=task_id, content=m.text)


inbox_project_id = find_inbox_project_id()

bot.polling(none_stop=True, interval=0)
