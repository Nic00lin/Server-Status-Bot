import telebot
import paramiko
from telebot import types
from settings import API
from ssh_functions import *

bot = telebot.TeleBot(API)

users_credentials = {}

welcome_message = """
Привет! Я бот для подключения по SSH к удаленной системе.
"""

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('Подключиться к удаленному хосту')
    bot.send_message(message.from_user.id, welcome_message, reply_markup=user_markup)

@bot.message_handler(func=lambda message: message.text == "Подключиться к удаленному хосту")
def start_ssh_connection(message):
    bot.send_message(message.chat.id, "Для начала подключения по SSH, введите IP адрес сервера:")
    bot.register_next_step_handler(message, ask_ip)

def ask_ip(message):
    chat_id = message.chat.id
    users_credentials[chat_id] = {'ip': message.text}
    bot.reply_to(message, "Введите порт:")
    bot.register_next_step_handler(message, ask_port)

def ask_port(message):
    chat_id = message.chat.id
    users_credentials[chat_id]['port'] = int(message.text)
    bot.reply_to(message, "Введите имя пользователя:")
    bot.register_next_step_handler(message, ask_username)

def ask_username(message):
    chat_id = message.chat.id
    users_credentials[chat_id]['username'] = message.text
    bot.reply_to(message, "Введите пароль:")
    bot.register_next_step_handler(message, ask_password)

def ask_password(message):
    chat_id = message.chat.id
    users_credentials[chat_id]['password'] = message.text

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(users_credentials[chat_id]['ip'], port=users_credentials[chat_id]['port'],
                    username=users_credentials[chat_id]['username'], password=users_credentials[chat_id]['password'])

        bot.reply_to(message, "Подключение по SSH успешно установлено! Выберите команду для выполнения:",
                     reply_markup=generate_commands_markup())
    except Exception as e:
        bot.reply_to(message, f"Ошибка при подключении: {str(e)}")

def generate_commands_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('/info', '/free', '/ports', '/services', '/reboot', '/list')
    markup.row('Перезапустить бота')
    return markup


@bot.message_handler(func=lambda message: message.text == "Перезапустить бота")
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('Перезапуск бота')
    bot.send_message(message.from_user.id, welcome_message, reply_markup=user_markup)
    user_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    user_markup.row('Подключиться к удаленному хосту')

@bot.message_handler(commands=['ports'])
def get_used_ports_command(message):
    chat_id = message.chat.id
    if chat_id not in users_credentials:
        bot.reply_to(message, "Сначала выполните команду /ssh для подключения к удаленной системе.")
        return

    output = get_used_ports(users_credentials[chat_id]['ip'],
                            users_credentials[chat_id]['port'],
                            users_credentials[chat_id]['username'],
                            users_credentials[chat_id]['password'])
    bot.reply_to(message, f"Информация об используемых портах: {output}")
    bot.send_message(chat_id, "Выберите действие:", reply_markup=generate_actions_markup())

@bot.message_handler(commands=['reboot'])
def reboot_server_command(message):
    chat_id = message.chat.id
    if chat_id not in users_credentials:
        bot.reply_to(message, "Сначала выполните команду /ssh для подключения к удаленной системе.")
        return

    output = reboot_server(users_credentials[chat_id]['ip'],
                           users_credentials[chat_id]['port'],
                           users_credentials[chat_id]['username'],
                           users_credentials[chat_id]['password'])
    bot.reply_to(message, f"Команда перезагрузки выполнена: {output}")
    bot.send_message(chat_id, "Выберите действие:", reply_markup=generate_actions_markup())

@bot.message_handler(commands=['services'])
def get_running_services_command(message):
    chat_id = message.chat.id
    if chat_id not in users_credentials:
        bot.reply_to(message, "Сначала выполните команду /ssh для подключения к удаленной системе.")
        return

    output = get_running_services(users_credentials[chat_id]['ip'],
                                  users_credentials[chat_id]['port'],
                                  users_credentials[chat_id]['username'],
                                  users_credentials[chat_id]['password'])
    bot.reply_to(message, f"Информация о запущенных сервисах: {output}")
    bot.send_message(chat_id, "Выберите действие:", reply_markup=generate_actions_markup())

@bot.message_handler(commands=['free'])
def get_available_memory_command(message):
    chat_id = message.chat.id
    if chat_id not in users_credentials:
        bot.reply_to(message, "Сначала выполните команду /ssh для подключения к удаленной системе.")
        return

    output = get_available_memory(users_credentials[chat_id]['ip'],
                                  users_credentials[chat_id]['port'],
                                  users_credentials[chat_id]['username'],
                                  users_credentials[chat_id]['password'])
    bot.reply_to(message, f"Доступная память: \n{output}")
    bot.send_message(chat_id, "Выберите действие:", reply_markup=generate_actions_markup())

bot.polling()

@bot.message_handler(commands=['info'])
def get_system_info_command(message):
    chat_id = message.chat.id
    if chat_id not in users_credentials:
        bot.reply_to(message, "Сначала выполните команду /ssh для подключения к удаленной системе.")
        return

    output = get_system_info(users_credentials[chat_id]['ip'],
                             users_credentials[chat_id]['port'],
                             users_credentials[chat_id]['username'],
                             users_credentials[chat_id]['password'])
    bot.reply_to(message, f"Команда получения информации выполнена: {output}")
    bot.send_message(chat_id, "Выберите действие:", reply_markup=generate_actions_markup())

@bot.message_handler(commands=['list'])
def list_files_command(message):
    chat_id = message.chat.id
    if chat_id not in users_credentials:
        bot.reply_to(message, "Сначала выполните команду /ssh для подключения к удаленной системе.")
        return

    try:
        output = list_files_and_directories(users_credentials[chat_id]['ip'],
                                             users_credentials[chat_id]['port'],
                                             users_credentials[chat_id]['username'],
                                             users_credentials[chat_id]['password'])
        bot.reply_to(message, f"Список файлов и каталогов: \n{output}")
        bot.send_message(chat_id, "Выберите действие:", reply_markup=generate_actions_markup())
    except Exception as e:
        bot.reply_to(message, f"Ошибка при выполнении команды просмотра файлов: {str(e)}")

def generate_actions_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Подключиться к другому серверу', 'Выбрать другую команду')
    return markup

@bot.message_handler(func=lambda message: message.text == "Подключиться к другому серверу")
def connect_to_another_server(message):
    del users_credentials[message.chat.id]
    start_ssh_connection(message)

@bot.message_handler(func=lambda message: message.text == "Выбрать другую команду")
def choose_another_command(message):
    bot.send_message(message.chat.id, "Выберите команду для выполнения:", reply_markup=generate_commands_markup())

bot.polling()
