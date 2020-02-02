import telebot
import mediator
import constants
import datetime
import random

# Bot API Key
bot = telebot.TeleBot("659838353:AAG1nXNGNqkNFTyopQGbBo-FOdMY5mKlzrY")


# ================================== INIT ================================
# Telegram Options Keyboard
options = telebot.types.ReplyKeyboardMarkup(row_width=2)
itembtn1 = telebot.types.KeyboardButton(constants.DIST)
itembtn2 = telebot.types.KeyboardButton(constants.PRICE)
itembtn3 = telebot.types.KeyboardButton(constants.RATE)
itembtn4 = telebot.types.KeyboardButton(constants.NONE)
options.add(itembtn1, itembtn2, itembtn3, itembtn4)

# Telegram Clear Prior Options
clear = telebot.types.ReplyKeyboardRemove(selective=False)

# Telegram Food-Types Keyboard
food_types = telebot.types.ReplyKeyboardMarkup()
for button in map(lambda x: telebot.types.KeyboardButton(x), constants.TYPES):
    food_types.add(button)
select_all_button = telebot.types.KeyboardButton("Select All")
select_none_button = telebot.types.KeyboardButton("Select None")
quit_button = telebot.types.KeyboardButton("Quit")
food_types.add(select_all_button, select_none_button, quit_button)

# Telegram Inline Keyboard
inline_keyboard = telebot.types.InlineKeyboardMarkup()
go_next = telebot.types.InlineKeyboardButton('NEXT', callback_data="NEXT")
go_to = telebot.types.InlineKeyboardButton('JUMP TO', callback_data="GOTO")
go_prev = telebot.types.InlineKeyboardButton('PREV', callback_data="PREV")
inline_keyboard.add(go_prev, go_to, go_next)

# Telegram days of week Keyboard
days = telebot.types.ReplyKeyboardMarkup(row_width=4)
mon = telebot.types.KeyboardButton("MON")
tue = telebot.types.KeyboardButton("TUE")
wed = telebot.types.KeyboardButton("WED")
thu = telebot.types.KeyboardButton("THU")
fri = telebot.types.KeyboardButton("FRI")
sat = telebot.types.KeyboardButton("SAT")
sun = telebot.types.KeyboardButton("SUN")
clr = telebot.types.KeyboardButton("CLEAR")
days.add(mon, tue, wed, thu, fri, sat, sun, clr)

# ======================== Message Handlers ===========================


# Start message
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.next_step_handlers = {}
    user = mediator.get_user(message.chat.id)
    bot.reply_to(message,
                 "Hi " + message.from_user.first_name
                 + ", I am the NTU Food Bot! \nLet me guide you through the setting up process! \n",
                 reply_markup=clear)
    if user.is_setting_up:
        bot.next_step_handlers = {}
        reply = bot.send_message(message.chat.id,
                                 "Please choose the types of food you want!\n"
                                 + "*Pressing a button toggles the food type.*\n Current Types: "
                                 + str(user.filters[constants.FOOD_TYPES]),
                                 reply_markup=food_types,
                                 parse_mode="Markdown")
        bot.register_next_step_handler(reply, toggle_type)
    else:
        bot.send_message(message.chat.id,
                         "You can search for food using /find "
                         + "or view other commands using /help",
                         reply_markup=clear,
                         parse_mode="Markdown")


# Help menu
@bot.message_handler(commands=['help'])
def help_menu(message):
    bot.send_message(message.chat.id,
                     "*HELP MENU*\n\n"
                     + "/start : Welcome message\n\n"
                     + "/preferences : Preference setting menu\n\n"
                     + "/profile : View your profile\n\n"
                     + "/location : Set your location\n\n"
                     + "/find : Search for Food Recommendations\n\n"
                     + "/help : You are here.\n\n"
                     + "/reset : Resets your user data\n\n",
                     reply_markup=clear,
                     parse_mode="Markdown")


# Profile displaying function
@bot.message_handler(commands=['profile'])
def show_profile(message):
    user = mediator.get_user(message.chat.id)
    bot.send_message(message.chat.id,
                     "*Your profile:* \n\n"
                     + "_" + message.from_user.first_name + "_\n"
                     + user.to_string()
                     + "\nUse /preferences to set your preferences,"
                     + "\nor /find to search for food options,"
                     + "\nor /help to find out more!",
                     reply_markup=clear,
                     parse_mode="Markdown")


# Location header function
@bot.message_handler(commands=['location'])
def location_command(message):
    mediator.get_user(message.chat.id)
    reply = bot.send_message(message.chat.id,
                         "Where are you? \n(You can reply with a location in NTU, such as \"SCSE\" or \"Hive\", " +
                         "or send me your location!)",
                         reply_markup=clear)
    bot.register_next_step_handler(reply, set_location)


# Location setting function
def set_location(message):
    user = mediator.get_user(message.chat.id)
    # Allows the use of telegram's built in location function
    if message.content_type == "location":
        user.set_location_values(message.location.latitude, message.location.longitude, "My Location")
        bot.send_message(message.chat.id, "Set your location as supplied!", reply_markup=clear)
    # Searches for a location by name
    else:
        loc = mediator.location_from_text(message.text)
        if loc is not None:
            user.set_location(loc)
            bot.send_message(message.chat.id,
                             "Setting location to: " + loc.loc_name,
                             reply_markup=clear)
        else:
            reply = bot.send_message(message.chat.id,
                             "Invalid Location! Please try again!",
                             reply_markup=clear)
            bot.register_next_step_handler(reply, set_location)
            return

    if user.is_setting_up:
        user.is_setting_up = False
        bot.send_message(message.chat.id,
                         "You are done setting up! Use /find to start finding food locations,"
                         + " or /help for more information!",
                         reply_markup=clear)
        show_profile(message)


# Preferences setting menu
@bot.message_handler(commands=["preferences", "pref"])
def set_preferences(message):
    mediator.get_user(message.chat.id)
    bot.send_message(message.chat.id,
                     "You can set the following preferences!\n\n"
                     + "/order : Order of priorities\n\n"
                     + "/filter : Search Filters\n\n"
                     + "/types : Set food types\n\n"
                     + "/time : Set time",
                     reply_markup=clear)


# Priority setting header
@bot.message_handler(commands=["order"])
def set_order(message):
    mediator.get_user(message.chat.id)
    reply = bot.send_message(message.chat.id,
                             "What is your greatest priority?",
                             reply_markup=options)
    bot.register_next_step_handler(reply, order)


# Sets the primary priority
def order(message):
    user = mediator.get_user(message.chat.id)
    # Lead to second priority
    if message.text == constants.RATE or message.text == constants.PRICE or message.text == constants.DIST:
        user.set_pref(pri_pref=message.text)
        reply = bot.send_message(message.chat.id,
                                 "What is your second priority?",
                                 reply_markup=options)
        bot.register_next_step_handler(reply, second_order)
    # Use default priority
    elif message.text == constants.NONE:
        user.set_pref(pri_pref=constants.DIST, sec_pref=constants.PRICE)
        bot.send_message(message.chat.id, "Priorities defaulted to Distance and Price!", reply_markup=clear)

        # Checks if the user is setting up to end the setting up process
        if user.is_setting_up:
            bot.send_message(message.chat.id, "Now, please set your location.", reply_markup=clear)
            location_command(message)

    # Error checking
    else:
        reply = bot.send_message(message.chat.id, "Invalid Input!", reply_markup=options)
        bot.register_next_step_handler(reply, order)


# Sets the secondary priority
def second_order(message):
    user = mediator.get_user(message.chat.id)
    if message.text == constants.RATE or message.text == constants.PRICE or message.text == constants.DIST:
        user.set_pref(sec_pref=message.text)
        bot.send_message(message.chat.id,
                         "Priorities set to " + user.pref[0] + " and " +
                         user.pref[1],
                         reply_markup=clear)

        # Checks if the user is setting up to end the setting up process
        if user.is_setting_up:
            bot.send_message(message.chat.id, "Now, please set your location.", reply_markup=clear)
            location_command(message)

    elif message.text == constants.NONE:
        bot.send_message(message.chat.id,
                         "Priority set to " + user.pref[0],
                         reply_markup=clear)

        # Checks if the user is setting up to end the setting up process
        if user.is_setting_up:
            bot.send_message(message.chat.id, "Now, please set your location.", reply_markup=clear)
            location_command(message)
    # Error checking
    else:
        reply = bot.send_message(message.chat.id, "Invalid Input!", reply_markup=options)
        bot.register_next_step_handler(reply, second_order)


# Filter header function
@bot.message_handler(commands=["filter"])
def set_filter(message):
    mediator.get_user(message.chat.id)
    reply = bot.send_message(message.chat.id,
                             "What do you want to filter by?",
                             reply_markup=options)
    bot.register_next_step_handler(reply, choose_filter)


# Filter setting menu
def choose_filter(message):
    user = mediator.get_user(message.chat.id)
    # Redirects user to the appropriate sub function
    if message.text == constants.DIST:
        reply = bot.send_message(message.chat.id,
                                 "What is the maximum distance you are willing to travel? (in meters)",
                                 reply_markup=clear)
        bot.register_next_step_handler(reply, set_dist)
    elif message.text == constants.PRICE:
        reply = bot.send_message(message.chat.id,
                                 "What is your budget? (Do not put units)",
                                 reply_markup=clear)
        bot.register_next_step_handler(reply, set_budget)
    elif message.text == constants.RATE:
        reply = bot.send_message(message.chat.id,
                                 "What is the minimum rating of the food you are looking for? (0 to 10)",
                                 reply_markup=clear)
        bot.register_next_step_handler(reply, set_rating)

    # Checks if user is done setting filters
    elif message.text == constants.NONE:
        bot.send_message(message.chat.id,
                         "*>Exiting set filter mode*",
                         reply_markup=clear,
                         parse_mode="Markdown")
        # Checks if user is setting up, if yes, redirects user to choosing priorities
        if user.is_setting_up:
            reply = bot.send_message(message.chat.id,
                                     "Among the below criteria, what is your first priority?",
                                     reply_markup=options)
            bot.register_next_step_handler(reply, order)
    else:
        reply = bot.send_message(message.chat.id, "Invalid Input!", reply_markup=options)
        bot.register_next_step_handler(reply, choose_filter)


# Sets the max distance
def set_dist(message):
    user = mediator.get_user(message.chat.id)
    try:
        dist = int(message.text)
        # Attempts to use the setter, and checks if successful
        if user.set_filter(constants.MAX_DIST, dist):
            reply = bot.send_message(message.chat.id,
                                     "Set maximum distance to "+str(dist)+"m!\nDo you want to set any other filters?",
                                     reply_markup=options)
            bot.register_next_step_handler(reply, choose_filter)
            return
    except ValueError:
        pass
    # General error message
    reply = bot.send_message(message.chat.id,
                             "Invalid Input! Please enter a positive integer number of meters!",
                             reply_markup=clear)
    bot.register_next_step_handler(reply, set_dist)


# Sets the max price
def set_budget(message):
    user = mediator.get_user(message.chat.id)
    try:
        price = float(message.text)
        # Attempts to set value and checks if successful
        if user.set_filter(constants.PRICE_RANGE, max=price):
            # Formats the floating point number as money for success message
            reply = bot.send_message(message.chat.id,
                                     "Set budget to " + '${:,.2f}'.format(price) +
                                     "!\nDo you want to set any other filters?",
                                     reply_markup=options)
            bot.register_next_step_handler(reply, choose_filter)
            return
    except ValueError:
        pass
    # Error Message
    reply = bot.send_message(message.chat.id,
                             "Invalid Input! Please enter a valid price with no units!",
                             reply_markup=clear)
    bot.register_next_step_handler(reply, set_budget)


# Sets the rating
def set_rating(message):
    user = mediator.get_user(message.chat.id)
    try:
        rating = int(message.text)
        # Attempts to set the value and checks if successful
        if user.set_filter(constants.MIN_RATING, rating):
            reply = bot.send_message(message.chat.id,
                                     "Set minimum food rating to " + str(rating) +
                                     "!\nDo you want to set any other filters?",
                                     reply_markup=options)
            bot.register_next_step_handler(reply, choose_filter)
            return
    except ValueError:
        pass
    # Error Message
    reply = bot.send_message(message.chat.id,
                             "Invalid Input! Please enter an integer rating between 0 and 10!",
                             reply_markup=clear)
    bot.register_next_step_handler(reply, set_rating)


# Lets the user configure the food types they want
@bot.message_handler(commands=["types"])
def toggle_type(message):
    user = mediator.get_user(message.chat.id)
    # Checks if the user is quitting
    if message.text == "Quit":
        bot.send_message(message.chat.id,
                         "*Your food preferences have been set!*\n Types: "
                         + str(user.filters[constants.FOOD_TYPES]),
                         reply_markup=clear,
                         parse_mode="Markdown")
        # Checks if the user is setting up, if yes, redirect the user to search filters
        if user.is_setting_up:
            reply = bot.send_message(message.chat.id,
                                     "Now to set your search filters!\nWhat filters would you like to set?",
                                     reply_markup=options,
                                     parse_mode="Markdown")
            bot.register_next_step_handler(reply, choose_filter)
    else:
        # Toggles the type of food on/off
        if message.text in constants.TYPES:
            if user.toggle_type(message.text):
                bot.send_message(message.chat.id, "*>Adding " + message.text + "*", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "*>Removing " + message.text + "*", parse_mode="Markdown")
        elif message.text == "Select All":
            bot.send_message(message.chat.id, "*>Adding all types*", parse_mode="Markdown")
            user.add_all_types()
        elif message.text == "Select None":
            bot.send_message(message.chat.id, "*>Removing all types*", parse_mode="Markdown")
            user.remove_all_types()
        # Check command usage
        elif message.text == "/types":
            pass
        # Error message
        else:
            bot.send_message(message.chat.id, "Invalid Food Type!")
        # Continues Looping
        reply = bot.send_message(message.chat.id,
                                 "*Pressing a button toggles the food type.*\n Current Types: "
                                 + str(user.filters[constants.FOOD_TYPES]),
                                 reply_markup=food_types,
                                 parse_mode="Markdown")
        bot.register_next_step_handler(reply, toggle_type)


# Time setting header
@bot.message_handler(commands=["time"])
def set_time(message):
    mediator.get_user(message.chat.id)
    reply = bot.send_message(message.chat.id,
                             "What day is it? (Press CLEAR to clear existing time data",
                             reply_markup=days)
    bot.register_next_step_handler(reply, query_day)


# Queries day of the week
def query_day(message):
    user = mediator.get_user(message.chat.id)
    if message.text == "CLEAR":
        user.clear_time()
        bot.send_message(message.chat.id,
                         "Cleared existing time data!",
                         reply_markup=clear)
    else:
        if message.text == "MON":
            user.set_day(0)
        elif message.text == "TUE":
            user.set_day(1)
        elif message.text == "WED":
            user.set_day(2)
        elif message.text == "THU":
            user.set_day(3)
        elif message.text == "FRI":
            user.set_day(4)
        elif message.text == "SAT":
            user.set_day(5)
        elif message.text == "SUN":
            user.set_day(6)
        else:
            reply = bot.send_message(message.chat.id,
                                     "Invalid Input!\nWhat day is it? (Press CLEAR to clear existing time data",
                                     reply_markup=days)
            bot.register_next_step_handler(reply, query_day)
            return
        reply = bot.send_message(message.chat.id,
                                 "Set day to " + message.text
                                 +"\nWhat time do you want to eat? (Reply in 24H format, e.g. 1430)",
                                 reply_markup=clear)
        bot.register_next_step_handler(reply, query_time)


# Sets the query time
def query_time(message):
    user = mediator.get_user(message.chat.id)
    try:
        hour = int(message.text) // 100
        minute = int(message.text) % 100
        if hour < 24 and minute < 60:
            user.set_time(int(message.text))
            bot.send_message(message.chat.id,
                             "Set time to " + message.text + "H!",
                             reply_markup=clear)
        else:
            reply = bot.send_message(message.chat.id,
                                     "Invalid Input! Please input a time in 24H format (e.g. 1430)",
                                     reply_markup=clear)
            bot.register_next_step_handler(reply, query_time)
    except ValueError:
        reply = bot.send_message(message.chat.id,
                                 "Invalid Input! Please input a time in 24H format (e.g. 1430)",
                                 reply_markup=clear)
        bot.register_next_step_handler(reply, query_time)


# Resets user details
@bot.message_handler(commands=['reset'])
def reset(message):
    mediator.reset_user(message.chat.id)
    bot.next_step_handlers = {}
    bot.send_message(message.chat.id, "Resetting your details!", reply_markup=clear)
    start_message(message)


# Actual query method
@bot.message_handler(commands=["find"])
def find_food(message):
    user = mediator.get_user(message.chat.id)
    bot.send_message(message.chat.id,
                     "*Finding food with the following parameters...*\n"
                     + user.to_string(),
                     reply_markup=clear,
                     parse_mode="Markdown")

    # Display of additional query parameters
    str_result, result = user.query()
    if str_result != "":
        bot.send_message(message.chat.id, str_result, reply_markup=clear)

    # Summary display of canteen info
    mes = "*Result*\n"
    index = 0
    for cant in result:
        index += 1
        mes += "\n*" + str(index) + " : " + cant[constants.NAME] + "* - " + cant[constants.LOCATION].loc_name
    bot.send_message(message.chat.id, mes, reply_markup=clear, parse_mode="Markdown")

    # Detailed display of canteen info
    reply = user.entry_as_str()
    bot.send_message(message.chat.id, reply, reply_markup=inline_keyboard, parse_mode="Markdown")


# Allows user to flip between options
@bot.callback_query_handler(func=lambda call: True)
def canteen_callback(query):
    user = mediator.get_user(query.from_user.id)
    data = query.data
    bot.answer_callback_query(query.id)
    if data == "NEXT":
        reply = user.next_entry()
    elif data == "PREV":
        reply = user.prev_entry()
    elif data == "GOTO":
        msg = bot.send_message(query.from_user.id, "What index would you like to jump to?", reply_markup=clear)
        bot.register_next_step_handler(msg, go_to_index)
        return
    else:
        reply = ""
    if reply != "":
        bot.edit_message_text(reply,
                              query.from_user.id,
                              query.message.message_id,
                              parse_mode="Markdown",
                              reply_markup=inline_keyboard)


# Attempts to go to an index
def go_to_index(message):
    user = mediator.get_user(message.chat.id)
    try:
        index = int(message.text)
        if user.set_index(index - 1):
            reply = user.entry_as_str()
            bot.send_message(message.chat.id, reply, reply_markup=inline_keyboard, parse_mode="Markdown")
        else:
            msg = bot.send_message(message.chat.id,
                                   "Invalid Index!\nWhat index would you like to jump to?", reply_markup=clear)
            bot.register_next_step_handler(msg, go_to_index)
    except ValueError:
        msg = bot.send_message(message.chat.id,
                               "Invalid Index!\nWhat index would you like to jump to?", reply_markup=clear)
        bot.register_next_step_handler(msg, go_to_index)


# ================================= FUN FUNCTIONS =====================================================


# Random function: I'm feeling Lucky
@bot.message_handler(commands=['anything'])
def anything_command(message):
    user_name = message.from_user.first_name
    unix_time = datetime.datetime.utcfromtimestamp(message.date+3600*8)

    info_list = ['McDonald in North Spine', 'Waffle in Canteen 2', 'Fried Chicken in Canteen 9',
                 'Beef Noodles in Canteen 14', 'Toast in Canteen 13', 'Pasta opposite to Prime in North Spine',
                 'Indian food in Canteen 16', 'SteamBoat in North Spine', 'Steak in Canteen 1']
    emo_list = ['How about', 'Why not', 'Maybe', 'My personal recommendation is']
    emo_list2 = ['is awesome', 'is a great choice', 'is delicious']

    if random.randint(0, 1) == 0:
        msg = emo_list[random.randint(0, len(emo_list)-1)] + ' ' + info_list[random.randint(0, len(info_list)-1)]
    else:
        msg = info_list[random.randint(0, len(info_list)-1)] + ' ' + emo_list2[random.randint(0, len(emo_list2)-1)]

    if unix_time.hour in range(11, 14):
        bot.reply_to(message, "Hi " + user_name + "! " + "Time for Lunch! Current time is ")
        bot.reply_to(message, unix_time.time())

    if unix_time.hour in range(17, 20):
        bot.reply_to(message, "Hi " + user_name + "! " + "Time for Dinner! Current time is ")
        bot.reply_to(message, unix_time.time())

    if unix_time.hour in range(14, 17):
        bot.reply_to(message, "Hi " + user_name + "! " + "Time for a nice afternoon tea! Current time is ")
        bot.reply_to(message, unix_time.time())

    bot.reply_to(message, msg)
    bot.send_photo(chat_id=message.from_user.id,
                   photo=open('bot_png/bot' + str(random.randint(1, 5)) + '.png', "rb"))


@bot.message_handler(commands=['map'])
def send_map(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, "Hi " + user_name + "! " + "Here it is!")
    bot.send_photo(chat_id=message.from_user.id, photo=open('NTUMap.png', "rb"))
    bot.send_photo(chat_id=message.from_user.id, photo=open('bot_png/bot' + str(random.randint(1, 5)) + '.png', "rb"))


# ======================================== MISC ============================================================


# Default case
@bot.message_handler(func=lambda message: True)
def default(message):
    mediator.get_user(message.chat.id)
    bot.send_message(message.chat.id, "That was an invalid command! Maybe try /help to get more info?")

# ========================= Starting the bot ======================================


print("Starting poll...")
bot.polling()
