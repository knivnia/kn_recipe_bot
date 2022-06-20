import logging
import os
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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
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
HEALTH = {
    'Alcohol-Cocktail': 'alcohol-cocktail',
    'Alcohol-Free': 'alcohol-free',
    'Celery-Free': 'celery-free',
    'Crustcean-Free': 'crustacean-free',
    'Dairy-Free': 'dairy-free',
    'DASH': 'DASH',
    'Egg-Free': 'egg-free',
    'Fish-Free': 'fish-free',
    'FODMAP-Free': 'fodmap-free',
    'Gluten-Free': 'gluten-free',
    'Immuno-Supportive': 'immuno-supportive',
    'Keto-Friendly': 'keto-friendly',
    'Kidney-Friendly': 'kidney-friendly',
    'Kosher': 'kosher',
    'Low Potassium': 'low-potassium',
    'Low Sugar': 'low-sugar',
    'Lupine-Free': 'lupine-free',
    'Mediterranean': 'Mediterranean',
    'Mollusk-Free': 'mollusk-free',
    'Mustard-Free': 'mustard-free',
    'No oil added': 'No-oil-added',
    'Paleo': 'paleo',
    'Peanut-Free': 'peanut-free',
    'Pescatarian': 'pecatarian',
    'Pork-Free': 'pork-free',
    'Red-Meat-Free': 'red-meat-free',
    'Sesame-Free': 'sesame-free',
    'Shellfish-Free': 'shellfish-free',
    'Soy-Free': 'soy-free',
    'Sugar-Conscious': 'sugar-conscious',
    'Sulfite-Free': 'sulfite-free',
    'Tree-Nut-Free': 'tree-nut-free',
    'Vegan': 'vegan',
    'Vegetarian': 'vegetarian',
    'Wheat-Free': 'wheat-free'
}
MEAL = {
    'Breakfast': 'breakfast',
    'Brunch': 'brunch',
    'Lunch/dinner': 'lunch/dinner',
    'Snack': 'snack',
    'Teatime': 'teatime'
}
DISH = {
    'Alcohol cocktail': 'alcohol cocktail',
    'Biscuits and cookies': 'biscuits and cookies',
    'Bread': 'bread',
    'Cereals': 'cereals',
    'Condiments and sauces': 'condiments and sauces',
    'Desserts': 'desserts',
    'Drinks': 'drinks',
    'Egg': 'egg',
    'Ice cream and custard': 'ice cream and custard',
    'Supper': 'supper',
    'Pancake': 'pancake',
    'Pasta': 'pasta',
    'Pastry': 'pastry',
    'Pies and tarts': 'pies and tarts',
    'Pizza': 'pizza',
    'Preps': 'preps',
    'Preserve': 'preserve',
    'Salad': 'salad',
    'Sandwiches': 'sandwiches',
    'Seafood': 'seafood',
    'Side dish': 'side dish',
    'Soup': 'soup',
    'special occasions': 'special occasions',
    'Starter': 'starter',
    'Sweets': 'sweets'
}
CUISINE = {
    'American': 'american',
    'Asian': 'asian',
    'British': 'british',
    'Caribbean': 'caribbean',
    'Central europe': 'central europe',
    'Chinese': 'chinese',
    'Eastern europe': 'eastern europe',
    'French': 'french',
    'Greek': 'greek',
    'Indian': 'indian',
    'Italian': 'italian',
    'Japanese': 'japanese',
    'Korean': 'korean',
    'Kosher': 'kosher',
    'Mediterranean': 'mediterranean',
    'Mexican': 'mexican',
    'Middle eastern': 'middle eastern',
    'Nordic': 'nordic',
    'South american': 'south american',
    'South east asian': 'south east asian',
    'World': 'world',
}


def wake_up(update, context):
    """Start bot."""
    context.user_data['diet'] = []
    context.user_data['health'] = []
    context.user_data['meal'] = []
    context.user_data['dish'] = []
    context.user_data['cuisine'] = []
    context.user_data['ingridients'] = []
    context.user_data['recipes'] = []
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
    """Buttons in main menu."""
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
    """Buttons in diet menu."""
    keyboard = [
        [InlineKeyboardButton('<<Main menu', callback_data='main')]
    ]
    for title, diet in DIETS.items():
        if diet in context.user_data['diet']:
            keyboard.insert(0, [InlineKeyboardButton(
                title + u'\u2713',
                callback_data=diet)])
        else:
            keyboard.insert(0, [InlineKeyboardButton(
                title,
                callback_data=diet)])
    return InlineKeyboardMarkup(keyboard, resize_keyboard=True)


def health_menu_keyboard(context):
    """Buttons in health menu."""
    keyboard = [
        [InlineKeyboardButton('<<Main menu', callback_data='main')]
    ]
    for title, health in HEALTH.items():
        if health in context.user_data['health']:
            keyboard.insert(0, [InlineKeyboardButton(
                title + u'\u2713',
                callback_data=health)])
        else:
            keyboard.insert(0, [InlineKeyboardButton(
                title,
                callback_data=health)])
    return InlineKeyboardMarkup(keyboard)


def meal_menu_keyboard(context):
    """Buttons in meal type menu."""
    keyboard = [
        [InlineKeyboardButton('<<Main menu', callback_data='main')]
    ]
    for title, meal in MEAL.items():
        if meal in context.user_data['meal']:
            keyboard.insert(0, [InlineKeyboardButton(
                title + u'\u2713',
                callback_data=meal)])
        else:
            keyboard.insert(0, [InlineKeyboardButton(
                title,
                callback_data=meal)])
    return InlineKeyboardMarkup(keyboard)


def dish_menu_keyboard(context):
    """Buttons in dish type menu."""
    keyboard = [
        [InlineKeyboardButton('<<Main menu', callback_data='main')]
    ]
    for title, dish in DISH.items():
        if dish in context.user_data['dish']:
            keyboard.insert(0, [InlineKeyboardButton(
                title + u'\u2713',
                callback_data=dish)])
        else:
            keyboard.insert(0, [InlineKeyboardButton(
                title,
                callback_data=dish)])
    return InlineKeyboardMarkup(keyboard)


def cuisine_menu_keyboard(context):
    """Buttons in cuisine type menu."""
    keyboard = [
        [InlineKeyboardButton('<<Main menu', callback_data='main')]
    ]
    for title, cuisine in CUISINE.items():
        if cuisine in context.user_data['cuisine']:
            keyboard.insert(0, [InlineKeyboardButton(
                title + u'\u2713',
                callback_data=cuisine)])
        else:
            keyboard.insert(0, [InlineKeyboardButton(
                title,
                callback_data=cuisine)])
    return InlineKeyboardMarkup(keyboard)


def recipe_menu_keyboard(url):
    """Buttons in recipe menu."""
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
    """Options in main menu."""
    context.user_data['recipes'] = []
    query = update.callback_query
    query.answer()
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text=main_menu_message(),
        reply_markup=main_menu_keyboard()
    )


def ingridients_menu(update, context):
    """Ingridients menu."""
    logger.info('Getting ingridients from user.')
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='Enter ingridient you have:'
    )


def diet_menu(update, context):
    """Options in diet menu."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Choose your diet:',
        reply_markup=diet_menu_keyboard(context)
    )


def health_menu(update, context):
    """Options in health menu."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Choose your health labels:',
        reply_markup=health_menu_keyboard(context)
    )


def meal_menu(update, context):
    """Options in meal menu."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Choose your meal type:',
        reply_markup=meal_menu_keyboard(context)
    )


def dish_menu(update, context):
    """Options in dish menu."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Choose your dish type:',
        reply_markup=dish_menu_keyboard(context)
    )


def cuisine_menu(update, context):
    """Options in cuisine menu."""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text='Choose your cuisine type:',
        reply_markup=cuisine_menu_keyboard(context)
    )


def recipe_menu(update, context):
    """Options in recipe menu."""
    if len(context.user_data['recipes']) == 0:
        get_recipe(update, context)
    query = update.callback_query
    query.answer()
    chat = update.effective_chat
    chosen_recipe = context.user_data.get('recipes').pop()
    if chosen_recipe is None:
        context.bot.send_message(
            chat_id=chat.id,
            text='You have seen all dishes for your search',
            reply_markup=recipe_menu_keyboard()
        )
    else:
        label = chosen_recipe.get('label')
        context.bot.send_photo(
            chat.id,
            chosen_recipe.get('image'),
            caption=f'{label}',
            reply_markup=recipe_menu_keyboard(chosen_recipe.get('url'))
        )


# !!!!!!!!!!!!!!!!!!!!!get objects!!!!!!!!!!!!!!!!!!!!!
def get_ingridients(update, context):
    """Saving user's ingridients."""
    logger.info(f'User have this ingridients: {update.message.text}')
    context.user_data['ingridients'] = update.message.text


def get_diet(update, context):
    """Saving user's diet options."""
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


def get_health(update, context):
    """Saving user's health options."""
    query = update.callback_query
    query.answer()
    if query.data not in context.user_data['health']:
        context.user_data['health'].append(query.data)
    else:
        context.user_data['health'].remove(query.data)
    query.edit_message_text(
        text='Choose your health labels:',
        reply_markup=health_menu_keyboard(context)
    )
    logger.info(f'Health labels: {context.user_data["health"]}.')


def get_meal(update, context):
    """Saving user's meal options."""
    query = update.callback_query
    query.answer()
    if query.data not in context.user_data['meal']:
        context.user_data['meal'].append(query.data)
    else:
        context.user_data['meal'].remove(query.data)
    query.edit_message_text(
        text='Choose your meal type:',
        reply_markup=meal_menu_keyboard(context)
    )
    logger.info(f'Meal types: {context.user_data["meal"]}.')


def get_dish(update, context):
    """Saving user's dish options."""
    query = update.callback_query
    query.answer()
    if query.data not in context.user_data['dish']:
        context.user_data['dish'].append(query.data)
    else:
        context.user_data['dish'].remove(query.data)
    query.edit_message_text(
        text='Choose your dish type:',
        reply_markup=dish_menu_keyboard(context)
    )
    logger.info(f'Dish types: {context.user_data["dish"]}.')


def get_cuisine(update, context):
    """Saving user's cuisine options."""
    query = update.callback_query
    query.answer()
    if query.data not in context.user_data['cuisine']:
        context.user_data['cuisine'].append(query.data)
    else:
        context.user_data['cuisine'].remove(query.data)
    query.edit_message_text(
        text='Choose your cuisine type:',
        reply_markup=cuisine_menu_keyboard(context)
    )
    logger.info(f'Cuisine types: {context.user_data["cuisine"]}.')


def get_recipe(update, context):
    """Sending request to API with user's search params."""
    logger.info('Searching recipes.')
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
        'diet': context.user_data.get('diet'),
        'health': context.user_data.get('health'),
        'mealType': context.user_data.get('meal'),
        'dishType': context.user_data.get('dish'),
        'cuisineType': context.user_data.get('cuisine')
    }
    try:
        response = requests.get(URL, params=params).json()
        check_response(response, context)
    except Exception:
        raise ConnectionError('API is not responding!')


def check_response(response, context):
    """Check API response."""
    logger.info('Beginning to check API response.')
    if not isinstance(response, dict):
        raise TypeError('Wrong data type (not dict)!')
    recipes = response.get('hits')
    if not isinstance(recipes, list):
        raise TypeError('Wrong data type (not list)!')
    if recipes is None:
        raise KeyError('Recipes not in response!')
    context.user_data['recipes'] = recipes
    for recipe in recipes:
        chosen_recipe = recipe.get('recipe')
        if chosen_recipe is not None:
            recipe_data = {
                'label': chosen_recipe.get('label'),
                'url': chosen_recipe.get('shareAs'),
                'image': chosen_recipe.get('images').get('REGULAR').get('url')
            }
            context.user_data['recipes'].append(recipe_data)
    logger.info('Ended checking API response.')


def check_tokens():
    """Checking tokens (all required)."""
    return all([APP_ID, TELEGRAM_TOKEN, APP_KEY])


def main():
    """Main bot logic."""
    if not check_tokens():
        logger.critical('Tokens are missing!')
        sys.exit('Tokens are missing!')
    try:
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
        for diet in DIETS.values():
            updater.dispatcher.add_handler(CallbackQueryHandler(
                get_diet,
                pattern=diet)
                )

        updater.dispatcher.add_handler(CallbackQueryHandler(
            health_menu, pattern='health'))
        for health in HEALTH.values():
            updater.dispatcher.add_handler(CallbackQueryHandler(
                get_health,
                pattern=health)
                )

        updater.dispatcher.add_handler(CallbackQueryHandler(
            meal_menu, pattern='meal'))
        for meal in MEAL.values():
            updater.dispatcher.add_handler(CallbackQueryHandler(
                get_meal,
                pattern=meal)
                )

        updater.dispatcher.add_handler(CallbackQueryHandler(
            dish_menu, pattern='dish'))
        for dish in DISH.values():
            updater.dispatcher.add_handler(CallbackQueryHandler(
                get_dish,
                pattern=dish)
                )

        updater.dispatcher.add_handler(CallbackQueryHandler(
            cuisine_menu, pattern='cuisine'))
        for cuisine in CUISINE.values():
            updater.dispatcher.add_handler(CallbackQueryHandler(
                get_cuisine,
                pattern=cuisine)
                )

        updater.dispatcher.add_handler(CallbackQueryHandler(
            recipe_menu, pattern='recipe'))

        updater.start_polling()
        updater.idle()
    except Exception as error:
        logger.error(f'Error: {error}', exc_info=True)


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
