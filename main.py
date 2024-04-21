import telebot
import paramiko
from settings import API

bot = telebot.TeleBot(API)


users_credentials = {}


welcome_message = """
Привет! Я бот для подключения по SSH к удаленной системе.
Чтобы начать, отправьте команду /start.
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

    bot.send_message(message.chat.id, "Пожалуйста, введите данные для подключения по SSH:", reply_markup=telebot.types.ReplyKeyboardRemove())
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

        bot.reply_to(message, "Подключение по SSH успешно установлено! Выберите команду для выполнения: /reboot, /free")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при подключении: {str(e)}")

@bot.message_handler(commands=['reboot'])
def reboot_command(message):
    chat_id = message.chat.id
    if chat_id not in users_credentials:
        bot.reply_to(message, "Сначала выполните команду /ssh для подключения к удаленной системе.")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(users_credentials[chat_id]['ip'], port=users_credentials[chat_id]['port'],
                    username=users_credentials[chat_id]['username'], password=users_credentials[chat_id]['password'])

        stdin, stdout, stderr = ssh.exec_command("sudo reboot")
        output = stdout.read().decode()
        bot.reply_to(message, f"Команда перезагрузки выполнена: {output}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при выполнении команды перезагрузки: {str(e)}")
    finally:
        ssh.close()

@bot.message_handler(commands=['free'])
def free_command(message):
    chat_id = message.chat.id
    if chat_id not in users_credentials:
        bot.reply_to(message, "Сначала выполните команду /ssh для подключения к удаленной системе.")
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(users_credentials[chat_id]['ip'], port=users_credentials[chat_id]['port'],
                    username=users_credentials[chat_id]['username'], password=users_credentials[chat_id]['password'])

        stdin, stdout, stderr = ssh.exec_command("free -h")
        output = stdout.read().decode()
        bot.reply_to(message, f"Доступная память: \n{output}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при выполнении команды просмотра памяти: {str(e)}")
    finally:
        ssh.close()

bot.polling()
