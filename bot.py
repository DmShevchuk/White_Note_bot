from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater
from requests import get

# Your Telegram token here
TELEGRAM_TOKEN = ''
# Вставить ссылку на "White Note"
api_url = ''  # Например 0dafb9f9.ngrok.io


# При запуске бота
def start(update, context):
    # Установка незарегистрированного пользователя
    context.chat_data['user_id'] = False
    # Отправка сообщения
    update.message.reply_text('Введите логин и пароль для просмотра своих записей!')


# Обработка текстовых сообщений
def message_handler(update, context):
    message = update.message.text
    # Пользователь должен войти, чтобы работать с ботом
    if not context.chat_data['user_id']:
        # Попытка входа
        try:
            # Обращение к нашему API
            login, password = message.split()
            response = get(f'http://{api_url}/api/login_user/{login}/{password}').json()
            if 'success' in response:
                context.chat_data['user_id'] = int(response['success'])
                # Отправка сообщения
                update.message.reply_text('Вход выполнен успешно!\n\n'
                                          'Команда /all_notes покажет все Ваши записи,\n'
                                          'Команда /logout поможет выйти с аккаунта!')
            else:
                # Отправка сообщения
                update.message.reply_text(response['error'])

        except Exception:
            # Отправка сообщения
            update.message.reply_text('Нужно ввести логин и пароль через пробел, одной строчкой!')
    # Если пользователь вошёл
    else:
        # Попытка получить запись по заголовку
        try:
            # Обращение к нашему API
            response = get(
                f'http://{api_url}/api/get_note/{context.chat_data["user_id"]}/{message}').json()
            if 'note' in response:
                title = response['note']['title']
                body = response['note']['body']
                is_important = '✅ Важная ✅' if response['note']['is_important'] else ''
                # Отправка сообщения
                update.message.reply_text(f'{is_important}\n\n{title}\n\n{body}')
            else:
                # Отправка сообщения
                update.message.reply_text(response['error'])
        # Если записка не найдена
        except Exception:
            # Отправка сообщения
            update.message.reply_text('Не удалось получить записку!')


# Получение всех записок и вывод их в пользовательскую клавиатуру
def all_notes(update, context):
    if not context.chat_data['user_id']:
        # Отправка сообщения
        update.message.reply_text('Нужно ввести логин и пароль через пробел, одной строчкой!')
    else:
        try:
            # Обращение к нашему API
            response = get(f'http://{api_url}/api/all_notes/{context.chat_data["user_id"]}').json()
            if 'notes' in response:
                keyboard = [[elem['title']] for elem in response['notes']]
                markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)
                # Отправка сообщения
                update.message.reply_text('Список ваших записей!\n'
                                          'Жмите на любую, чтобы прочитать её!', reply_markup=markup)
        except Exception:
            # Отправка сообщения
            update.message.reply_text('Не удалось получить список записей!')


# Выход пользователя
def logout(update, context):
    context.chat_data['user_id'] = False
    # Отправка сообщения
    update.message.reply_text('Выход выполнен успешно!')


# оновная функция
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)  # API-ключ Telegram
    dp = updater.dispatcher
    # Инициализация всех обработчиков
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('logout', logout))
    dp.add_handler(CommandHandler('all_notes', all_notes))
    dp.add_handler(MessageHandler(Filters.text, message_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
