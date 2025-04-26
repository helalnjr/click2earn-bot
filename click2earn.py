
import telebot
import json
import os

# Bot Token
TOKEN = '7394382530:AAHRIemlpqw2Lryt9Aot24mhaPLddrE7qsk'
bot = telebot.TeleBot(TOKEN)

# Files
USER_DATA_FILE = 'users.json'
TASKS_FILE = 'tasks.json'

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

@bot.message_handler(commands=['start'])
def start(message):
    users = load_users()
    user_id = str(message.from_user.id)

    if user_id not in users:
        ref_code = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
        users[user_id] = {
            'work_balance': 0,
            'refer_balance': 0,
            'refer_count': 0,
            'joined_by': ref_code,
            'custom_id': 786 + len(users)
        }
        if ref_code:
            for uid, info in users.items():
                if str(info['custom_id']) == ref_code:
                    info['refer_balance'] += 50
                    info['refer_count'] += 1
                    break
        save_users(users)

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('🚀 Register Now')
    markup.row('📝 Tasks', '💰 Balance')
    markup.row('🏦 Withdraw', '👥 Refer Link')

    bot.send_message(message.chat.id, f"Welcome to Click2Earn Bot!\n\nYour ID: {users[user_id]['custom_id']}\n\nChoose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    if message.text == '🚀 Register Now':
        start(message)
    elif message.text == '📝 Tasks':
        send_tasks(message)
    elif message.text == '💰 Balance':
        send_balance(message)
    elif message.text == '🏦 Withdraw':
        withdraw_request(message)
    elif message.text == '👥 Refer Link':
        users = load_users()
        user_id = str(message.from_user.id)
        refer_link = f"https://t.me/Click2EarnBot?start={users[user_id]['custom_id']}"
        bot.send_message(message.chat.id, f"Your Refer Link:\n{refer_link}")

@bot.message_handler(commands=['tasks'])
def send_tasks(message):
    tasks = load_tasks()
    if not tasks:
        bot.send_message(message.chat.id, "No tasks available now. Please check later!")
        return
    for idx, task_link in enumerate(tasks, 1):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Go to Task", url=task_link))
        markup.add(telebot.types.InlineKeyboardButton("Done", callback_data=f"task_done_{idx}"))
        bot.send_message(message.chat.id, f"Task {idx}: Complete this task.", reply_markup=markup)

@bot.message_handler(commands=['balance'])
def send_balance(message):
    users = load_users()
    user_id = str(message.from_user.id)
    work = users[user_id]['work_balance']
    refer = users[user_id]['refer_balance']
    bot.send_message(message.chat.id, f"Work Balance: {work} ৳\nRefer Balance: {refer} ৳")

@bot.message_handler(commands=['withdraw'])
def withdraw_request(message):
    users = load_users()
    user_id = str(message.from_user.id)
    if users[user_id]['work_balance'] >= 300 or users[user_id]['refer_count'] >= 20:
        bot.send_message(message.chat.id, "You are eligible for withdraw! Please contact admin.")
    else:
        bot.send_message(message.chat.id, "You are not eligible for withdraw yet.\nMinimum 300 ৳ task balance or 20 referrals required.")

@bot.message_handler(commands=['addlink'])
def add_link(message):
    if str(message.from_user.id) != '7063876305':
        bot.send_message(message.chat.id, "You are not authorized to add links.")
        return
    msg = bot.send_message(message.chat.id, "Send the task link:")
    bot.register_next_step_handler(msg, save_new_task)

def save_new_task(message):
    tasks = load_tasks()
    tasks.append(message.text)
    save_tasks(tasks)
    bot.send_message(message.chat.id, "Task link added successfully!")

@bot.callback_query_handler(func=lambda call: True)
def task_done(call):
    users = load_users()
    user_id = str(call.from_user.id)
    users[user_id]['work_balance'] += 10
    save_users(users)
    bot.answer_callback_query(call.id, "10৳ Added for completing the task!")

print("Bot is Running...")
bot.polling()
