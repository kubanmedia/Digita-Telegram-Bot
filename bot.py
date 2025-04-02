import os
import telebot
from groq import Groq
from collections import defaultdict
from flask import Flask
from threading import Thread

# Flask app for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Получаем токен бота из переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
    exit(1)

# Получаем API ключ Groq из переменных окружения
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("No Groq API key provided. Set the GROQ_API_KEY environment variable.")
    exit(1)

# Инициализация Groq клиента
client = Groq(api_key=GROQ_API_KEY)

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения истории сообщений по пользователям
conversation_history = defaultdict(list)
# Максимальное количество сообщений в истории для одного пользователя
MAX_HISTORY = 10

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Очищаем историю сообщений при старте нового диалога
    user_id = message.from_user.id
    conversation_history[user_id] = []
    text = "Привет! Я бот с Groq API и моделью Llama 3. Используй /help для списка команд или просто пиши мне! Я помню наш разговор для лучшего контекста."
    bot.reply_to(message, text)

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    text = "Доступные команды:\n/start - Начать работу и очистить историю диалога\n/help - Показать это сообщение\n/clear - Очистить историю сообщений\nЛюбой текст - получить ответ от Llama 3"
    bot.reply_to(message, text)

# Обработчик команды /clear
@bot.message_handler(commands=['clear'])
def clear_history(message):
    user_id = message.from_user.id
    conversation_history[user_id] = []
    text = "История сообщений очищена. Начинаем диалог с чистого листа!"
    bot.reply_to(message, text)

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Проверяем, что это не команда
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id

    try:
        # Добавляем сообщение пользователя в историю
        conversation_history[user_id].append({"role": "user", "content": message.text})

        # Ограничиваем историю максимальным количеством сообщений
        if len(conversation_history[user_id]) > MAX_HISTORY:
            conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY:]

        # Добавляем системное сообщение для более дружелюбных ответов
        messages = [{"role": "system", "content": "Ты дружелюбный ассистент, который помогает пользователям с их вопросами. Ты отвечаешь на русском или английском в зависимости от языка пользователя."}]
        messages.extend(conversation_history[user_id])

        # Отправляем запрос к Groq API с историей сообщений
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Модель Llama 3 от Groq
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )

        # Получаем текст ответа от Groq
        reply_text = response.choices[0].message.content

        # Добавляем ответ ассистента в историю
        conversation_history[user_id].append({"role": "assistant", "content": reply_text})

        # Отправляем текстовый ответ
        bot.reply_to(message, reply_text)

    except Exception as e:
        error_message = f"Произошла ошибка: {str(e)}"
        bot.reply_to(message, error_message)

# Запускаем бота
if __name__ == '__main__':
    print('Бот запущен...')
    keep_alive()  # Start the Flask server in a separate thread
    bot.polling(none_stop=True)
