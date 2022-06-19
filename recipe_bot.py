import logging
import os
import random
import sys

import requests
from dotenv import load_dotenv

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    Filters,
    MessageHandler,
    Updater
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')
URL = 'https://api.edamam.com/api/recipes/v2'
DIETS = {
    'Balanced diet': 'balanced',
    'High-fiber diet': 'high-fiber',
    'High-protein diet': 'high-protein',
    'Low-carb diet': 'low-carb',
    'Low-fat diet': 'low-fat',
    'Low-sodium diet': 'low-sodium'
}


def wake_up(update, context):
    context.user_data['diet'] = []
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text='Hi, {}!'.format(name)
        )
    update.message.reply_text(
        text=main_menu_message(),
        reply_markup=main_menu_keyboard()
    )


# !!!!!!!!!!!!!!!!!!!!!keyboards!!!!!!!!!!!!!!!!!!!!!
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton('Ingridients (required)', callback_data='ingr'),
            InlineKeyboardButton('Diet', callback_data='diet')],
        [InlineKeyboardButton('Health', callback_data='health'),
            InlineKeyboardButton('Cuisine type', callback_data='cuisineType')],
        [InlineKeyboardButton('Meal type', callback_data='mealType'),
            InlineKeyboardButton('Dish type', callback_data='dishType')],
        [InlineKeyboardButton('Find recipe', callback_data='recipe')]
    ]
    return InlineKeyboardMarkup(keyboard)


def diet_menu_keyboard(context):
    keyboard = [
        [InlineKeyboardButton('<<Main menu', callback_data='main')]
    ]
    for title, diet in DIETS.items():
        if diet in context.user_data['diet']:
            keyboard.insert(0, [InlineKeyboardButton(
                title + '✔',
                callback_data=diet)])
        else:
            keyboard.insert(0, [InlineKeyboardButton(
                title,
                callback_data=diet)])
    return InlineKeyboardMarkup(keyboard)


def recipe_menu_keyboard(url):
    keyboard = [
        [InlineKeyboardButton('Go to the recipe', url=url)],
        [InlineKeyboardButton('<< New search', callback_data='main'),
            InlineKeyboardButton(
                'Another recipe',
                callback_data='recipe-card')]
    ]
    return InlineKeyboardMarkup(keyboard)


# !!!!!!!!!!!!!!!!!!!!!menus!!!!!!!!!!!!!!!!!!!!!
def main_menu_message():
    return 'Choose options:'


def main_menu(update, context):
    query = update.callback_query
    query.answer()
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=main_menu_message(),
        reply_markup=main_menu_keyboard()
    )


def ingridients_menu(update, context):
    logger.info('Getting ingridients from user.')
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Enter ingridient you have:'
    )


def diet_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Choose your diet:',
        reply_markup=diet_menu_keyboard(context)
    )


def recipe_menu(update, context):
    get_recipe(update, context)
    query = update.callback_query
    query.answer()
    chat = update.effective_chat
    chosen_recipe = context.user_data.get('recipes').popitem()[-1]
    if chosen_recipe is None:
        context.bot.send_message(
            chat_id=chat.id,
            text='You have seen all dishes for your search',
            reply_markup=recipe_menu_keyboard()
        )
    label = chosen_recipe.get('label')
    url = chosen_recipe.get('shareAs')
    image = chosen_recipe.get('images').get('REGULAR').get('url')
    context.bot.send_photo(
        chat.id,
        image,
        caption=f'{label}',
        reply_markup=recipe_menu_keyboard(url)
    )


# !!!!!!!!!!!!!!!!!!!!!get objects!!!!!!!!!!!!!!!!!!!!!
def get_ingridients(update, context):
    logger.info(f'User have this ingridients: {update.message.text}')
    context.user_data['ingridients'] = update.message.text


def get_diet(update, context):
    query = update.callback_query
    query.answer()
    if query.data not in context.user_data['diet']:
        context.user_data['diet'].append(query.data)
    else:
        context.user_data['diet'].remove(query.data)
    query.edit_message_text(
        text='Choose your diet:',
        reply_markup=diet_menu_keyboard(context)
    )
    logger.info(f'Diet: {context.user_data["diet"]}.')


def get_recipe(update, context):
    logger.info('Searching recipe.')
    chat = update.effective_chat
    ingridients = context.user_data.get('ingridients')
    if ingridients is None:
        context.bot.send_message(
            chat_id=chat.id,
            text='Enter at least one ingridient!'
        )
    params = {
        'type': 'public',
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'q': ingridients,
        'diet': context.user_data.get('diet')
    }
    response = requests.get(URL, params=params).json()
    hits_len = len(response.get('hits'))
    if hits_len == 0:
        context.bot.send_message(
            chat_id=chat.id,
            text='Nothing found for your request',
            reply_markup=recipe_menu_keyboard()
        )
    else: 
        context.user_data['recipes'] = random.choice(response.get('hits'))
        context.user_data['recipes'].popitem()


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', wake_up))
    updater.dispatcher.add_handler(CallbackQueryHandler(
        main_menu,
        pattern='main'))
    updater.dispatcher.add_handler(CallbackQueryHandler(
        ingridients_menu, pattern='ingr'))
    updater.dispatcher.add_handler(MessageHandler(
        ~Filters.command, get_ingridients))
    updater.dispatcher.add_handler(CallbackQueryHandler(
        diet_menu, pattern='diet'))
    updater.dispatcher.add_handler(CallbackQueryHandler(
        get_diet,
        pattern='balanced|high-fiber|high-protein|low-carb|low-fat|low-sodium')
        )

    updater.dispatcher.add_handler(CallbackQueryHandler(
        recipe_menu, pattern='recipe'))
    # updater.dispatcher.add_handler(CallbackQueryHandler(
    #     get_recipe, pattern='recipe'))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler(os.path.basename('/root/recipe_bot.log'), 'w'),
            logging.StreamHandler(sys.stdout)],
        format=(
            '%(asctime)s -'
            ' %(name)s -'
            ' %(levelname)s -'
            ' %(funcName)s -'
            ' %(levelno)s -'
            ' %(message)s'
        )
    )
    main()
