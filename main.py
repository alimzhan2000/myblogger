import telebot
import photos
import time
from database import Database
from telebot import types
from profiles import Blogger

token = "962351766:AAE_2ax6GANwka1ldGni2xMbV7-CPZboPEk"
bot = telebot.TeleBot(token)
db = Database()
users = {}

class Settings:
	def __init__(self):
		self.mode = 0
		self.blogger = False
		self.profile = Blogger()
		self.search_st = False
		self.search_mess_id = 0
		self.search_list = []
		self.cur_blogger = 0
		self.filters = [[], [], [], []]
		self.last_keyboard = None
def add_new_user(chat_id):
	global users
	if chat_id in users.keys():
		return 
	a = Settings()
	users[chat_id] = a
def default_vars(chat_id):
	global users
	users[chat_id] = Settings()

def profile_info(profile):
	text = profile.name + '\n' + profile.login + '\n' + str(profile.followers) + ' подписчиков\n'
	text += 'Средний охват одной публикации - ' + str(profile.avg_post_coverage)
	text += '\nСредний охват одной истории - ' + str(profile.avg_story_coverage)
	text += '\nГеография подписчиков - '
	for city in profile.followers_geo:
		if city == profile.followers_geo[-1]:
			text += city
		else:
			text += city + ', '
	text += '\nСредний возраст подписчиков - '
	for age in profile.avg_age:
		if age == profile.avg_age[-1]:
			text += age + ' лет'
		else:
			text += age + ' лет, '
	text += '\nПол подписчиков:\nМужчины - ' + str(profile.male_ratio) + '%\nЖенщины - ' + str(profile.female_ratio)
	text += '%\nТематика аккаунта - '
	for sub in profile.subjects:
		if sub == profile.subjects[-1]:
			text += sub
		else:
			text += sub + ', '
	text += '\nЦена одной публикации - ' + str(profile.post_price) + ' тенге'
	text += '\nЦена одной истории - ' + str(profile.story_price) + ' тенге'
	return text  
@bot.message_handler(commands = ['start'])
def start(message):
	chat_id = message.chat.id
	add_new_user(chat_id)
	default_vars(chat_id)
	keyboard = types.ReplyKeyboardMarkup(True, False)
	if db.check_blogger(chat_id) == True:
		users[chat_id].blogger = True
		keyboard.row('Мой профиль')
		bot.send_message(chat_id, 'Главное меню', reply_markup = keyboard)
		return
	keyboard.row('Я Блогер', 'Я Рекламодатель')
	bot.send_message(message.chat.id, 'Здравствуйте, кем Вы являетесь?', reply_markup=keyboard)

@bot.message_handler(func=lambda message:message.text is not None and message.text[:4] == 'mode')
def mode_set(message):
	users[message.chat.id].mode = int(message.text[4:])
	print(users[message.chat.id].mode)

@bot.message_handler(content_types = ['photo'])
def upload_photo(message):
	global users
	chat_id = message.chat.id
	if users[chat_id].blogger is True:
		if users[chat_id].mode == 5:
			photos.document_handler(message, bot)
			users[chat_id].mode += 1
			bot.send_message(chat_id, 'Какой у Вас средний охват одного story в Instagram?\n(пример: 35000)')
		elif users[chat_id].mode == 7:
			photos.document_handler(message, bot)
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Нур-Султан', 'Алматы')
			keyboard.row('Шымкент', 'Караганда')
			bot.send_message(chat_id, 'Укажите откуда Ваши подписчики.', reply_markup = keyboard)
		elif users[chat_id].mode == 9:
			photos.document_handler(message, bot)
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('13-17', '18-24', '25-34')
			keyboard.row('35-44', '45-54')
			bot.send_message(chat_id, 'Укажите средний возраст Вашей аудитории.', reply_markup = keyboard)
		elif users[chat_id].mode == 11:
			photos.document_handler(message, bot)
			users[chat_id].mode += 1
			bot.send_message(chat_id, 'Сколько процентов Вашей аудитории женская?\n(пример: 55)')
		elif users[chat_id].mode == 14:
			photos.document_handler(message, bot)
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('спорт', 'лайфстайл')
			keyboard.row('бизнес', 'красота')
			keyboard.row('личностный рост', 'всё')
			bot.send_message(chat_id, 'Какая тематика у Вашего аккаунта в Instagram?', reply_markup = keyboard)

@bot.message_handler(func=lambda message:message.chat.id in users.keys() and users[message.chat.id].mode > 0 and users[message.chat.id].blogger == True)
def create_profile(message):
	global users
	chat_id = message.chat.id 
	if users[chat_id].mode == 1:
		users[chat_id].profile.name = message.text
		users[chat_id].profile.chat_id = chat_id
		bot.send_message(chat_id, 'Какой у Вас логин в Instagram?\n(пример: @bloggerskz)')
		users[chat_id].mode += 1
	elif users[chat_id].mode == 2:
		users[chat_id].profile.login = message.text
		bot.send_message(chat_id, 'Сколько у Вас подписчиков?\n(пример: 23500)')
		users[chat_id].mode += 1
	elif users[chat_id].mode == 3:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введите целое число без букв и других символов')
			return
		users[chat_id].profile.followers = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Какой у вас средний охват одной публикации в Instagram?\n(пример: 35000)')		
	elif users[chat_id].mode == 4:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введите целое число без букв и других символов')
			return
		users[chat_id].profile.avg_post_coverage = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Прикрепите скрин для доказательства\n\
		(в разделе “статистика” выберите “публикации”, и выберите “охват” за последние 30 дней)')
	elif users[chat_id].mode == 6:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введите целое число без букв и других символов')
			return
		users[chat_id].profile.avg_story_coverage = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Прикрепите скрин для доказательства\n\
(в разделе “статистика” выберите “истории”, и выберите “охват” за последние 14 дней)')
	elif users[chat_id].mode == 8:
		if message.text == 'Следующий шаг':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardRemove()
			bot.send_message(chat_id, 'Прикрепите скрин для доказательства\n\
(в разделе “статистика”, выберите “аудитория”, и “топ местоположений” по городам)', reply_markup = keyboard)
			return
		users[chat_id].profile.followers_geo.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Следующий шаг')
		keyboard.row('Нур-Султан', 'Алматы')
		keyboard.row('Шымкент', 'Караганда')
		if len(users[chat_id].profile.followers_geo) <= 1: 
			bot.send_message(chat_id, 'Вы можете выбрать несколько городов или нажать "Следующий шаг",\
			чтобы перейти к следующему этапу.', reply_markup = keyboard)
	elif users[chat_id].mode == 10:
		if message.text == 'Следующий шаг':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardRemove()
			bot.send_message(chat_id, 'Прикрепите скрин для доказательства\n\
(в разделе “статистика”, выберите “аудитория”, и “возрастной диапазон” всех подписчиков)', reply_markup=keyboard)
			return
		users[chat_id].profile.avg_age.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Следующий шаг')
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		if len(users[chat_id].profile.avg_age) <= 1: 
			bot.send_message(chat_id, 'Вы можете выбрать несколько диапозонов или нажать "Следующий шаг",\
			чтобы перейти к следующему этапу.', reply_markup = keyboard)
	elif users[chat_id].mode == 12:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введите целое число без букв и других символов')
			return
		users[chat_id].profile.female_ratio = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Сколько процентов Вашей аудитории мужская?\n(пример: 45)')
	elif users[chat_id].mode == 13:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введите целое число без букв и других символов')
			return
		users[chat_id].profile.male_ratio = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Прикрепите скрин для доказательства\n\
(в разделе “статистика”, выберите “аудитория”, и “пол”)')
	elif users[chat_id].mode == 15:
		if message.text == 'Следующий шаг':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardRemove()
			bot.send_message(chat_id, 'Какая у Вас средняя стоимость рекламной публикации в тенге?\n(пример: 45000)',\
			reply_markup = keyboard)
			return
		users[chat_id].profile.subjects.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Следующий шаг')
		keyboard.row('спорт', 'лайфстайл')
		keyboard.row('бизнес', 'красота')
		keyboard.row('личностный рост', 'всё')
		if len(users[chat_id].profile.subjects) <= 1: 
			bot.send_message(chat_id, 'Вы можете выбрать несколько тематик или нажать "Следующий шаг",\
			чтобы перейти к следующему этапу.', reply_markup = keyboard)
	elif users[chat_id].mode == 16:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введите целое число без букв и других символов')
			return
		users[chat_id].profile.post_price = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Какая у Вас средняя стоимость рекламной истории в тенге?\n(пример: 25000)')
	elif users[chat_id].mode == 17:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введите целое число без букв и других символов')
			return
		users[chat_id].profile.story_price = int(message.text)
		users[chat_id].mode = 0
		db.new_blogger(users[chat_id].profile)
		bot.send_message(chat_id, 'Ваш профиль заполнен и создан. Спасибо!')


@bot.message_handler(content_types = ['text'])
def get_message(message):
	global users
	chat_id = message.chat.id
	if message.text == 'Я Блогер':
		users[chat_id].blogger = True
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Создать профиль')
		bot.send_message(chat_id, 'Для начала Вам необходимо создать профиль', reply_markup = keyboard)
	elif message.text == 'Создать профиль':
		users[chat_id].mode = 1
		bot.send_message(chat_id, 'Как Вас зовут?')
	elif message.text == 'Мой профиль':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Удалить профиль', callback_data = 'delete_profile')
		keyboard.add(button)
		bot.send_message(chat_id, info, reply_markup = keyboard)
	elif message.text == 'Я Рекламодатель':
		users[chat_id].blogger = False
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Поиск блогеров', 'Умный подбор')
		bot.send_message(chat_id, 'Для самостоятельного поиска блогеров по фильтрам нажмите\n*"Поиск блогеров"*\n\nДля подбора блогеров\
 максимально таргетированных на вашу целевую аудиторию и попадающим под Ваш рекламный бюджет нажмите\n*"Умный подбор"*',\
 reply_markup=keyboard,parse_mode = 'Markdown')
	elif message.text == 'Поиск блогеров':
		users[chat_id].search_st = True
		users[chat_id].search_list = db.search_bloggers()
		users[chat_id].cur_blogger = 0
		keyboard = types.InlineKeyboardMarkup()
		if len(users[chat_id].search_list) == 0:
			bot.send_message(chat_id, 'К сожалению, в нашей базе нет блогеров по данному запросу')
			return
		if len(users[chat_id].search_list) > 1:
			button = types.InlineKeyboardButton('Следующий блогер >>', callback_data = 'next_blogger')
			keyboard.add(button)
		button = types.InlineKeyboardButton('Фильтровать по..', callback_data = 'filters')
		keyboard.add(button)
		# button = types.InlineKeyboardButton('Сортировать по..', callback_data = 'sort')
		# keyboard.add(button)
		cur_blogger = users[chat_id].cur_blogger
		blogger_id = users[chat_id].search_list[cur_blogger]
		profile = db.get_profile_by_id(blogger_id)
		profile = Blogger(profile)
		text = profile_info(profile)
		text += '\n\nФильтры:\n\n' + str(cur_blogger+1) + '/' + str(len(users[chat_id].search_list))
		mess = bot.send_message(chat_id, text, reply_markup = keyboard) 
		users[chat_id].search_mess_id = mess.message_id

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	chat_id = call.message.chat.id
	if call.data == 'delete_profile':
		db.delete_profile(chat_id)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Создать профиль')
		bot.send_message(chat_id, 'Ваш профиль был успешно удален!', reply_markup=keyboard)
	elif call.data == 'next_blogger' or call.data == 'prev_blogger':
		users[chat_id].cur_blogger += 1
		if call.data == 'prev_blogger':
			users[chat_id].cur_blogger -= 2
		cur_blogger = users[chat_id].cur_blogger
		search_list = users[chat_id].search_list
		search_mess_id = users[chat_id].search_mess_id
		keyboard = types.InlineKeyboardMarkup()
		if cur_blogger < 0 or cur_blogger >= len(search_list):
			if call.data == 'prev_blogger':
				users[chat_id].cur_blogger += 2
			else:
				users[chat_id].cur_blogger -= 1
			return
		if cur_blogger != len(search_list) - 1 and cur_blogger > 0:
			button1 = types.InlineKeyboardButton('След >>', callback_data = 'next_blogger')
			button2 = types.InlineKeyboardButton('<< Пред', callback_data = 'prev_blogger')
			keyboard.row(button2, button1)
		elif cur_blogger != len(search_list) - 1:
			keyboard.add(types.InlineKeyboardButton('Следующий блогер >>', callback_data = 'next_blogger'))
		elif cur_blogger > 0:
			keyboard.add(types.InlineKeyboardButton('<< Предыдущий блогер', callback_data = 'prev_blogger'))			
		button = types.InlineKeyboardButton('Фильтровать по..', callback_data = 'filters')
		keyboard.add(button)
		# button = types.InlineKeyboardButton('Сортировать по..', callback_data = 'sort')
		# keyboard.add(button)
		blogger_id = search_list[cur_blogger]
		profile = db.get_profile_by_id(blogger_id)
		profile = Blogger(profile)
		text = profile_info(profile)
		text += '\n\nФильтры: '
		for a in users[chat_id].filters:
			for b in a:
				if b == a[-1] and a == users[chat_id].filters[-1]:
					text += b
				else:
					text += b + ', '
		text += '\n\n' + str(cur_blogger+1) + '/' + str(len(search_list))
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_text(chat_id = chat_id, message_id = search_mess_id, text = text, reply_markup = keyboard)
	elif call.data == 'filters':
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('интересам', callback_data = 'filter_sub')
		button2 = types.InlineKeyboardButton('региону', callback_data = 'filter_geo')
		button3 = types.InlineKeyboardButton('возрасту', callback_data = 'filter_age')
		button4 = types.InlineKeyboardButton('полу', callback_data = 'filter_gender')
		button5 = types.InlineKeyboardButton('назад', callback_data = 'search_back_main')
		keyboard.row(button1, button2)
		keyboard.row(button3, button4)
		keyboard.add(button5)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)
	elif call.data == 'search_back_main':
		cur_blogger = users[chat_id].cur_blogger
		search_list = users[chat_id].search_list
		search_mess_id = users[chat_id].search_mess_id
		keyboard = types.InlineKeyboardMarkup()
		if cur_blogger != len(search_list) - 1 and cur_blogger > 0:
			button1 = types.InlineKeyboardButton('След >>', callback_data = 'next_blogger')
			button2 = types.InlineKeyboardButton('<< Пред', callback_data = 'prev_blogger')
			keyboard.row(button2, button1)
		elif cur_blogger != len(search_list) - 1:
			keyboard.add(types.InlineKeyboardButton('Следующий блогер >>', callback_data = 'next_blogger'))
		elif cur_blogger > 0:
			keyboard.add(types.InlineKeyboardButton('<< Предыдущий блогер', callback_data = 'prev_blogger'))			
		button = types.InlineKeyboardButton('Фильтровать по..', callback_data = 'filters')
		keyboard.add(button)
		# button = types.InlineKeyboardButton('Сортировать по..', callback_data = 'sort')
		# keyboard.add(button)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = search_mess_id, reply_markup = keyboard)
	elif call.data == 'filter_sub':
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('спорт', callback_data = 'filter_sub_sport')
		button2 = types.InlineKeyboardButton('лайфстайл', callback_data = 'filter_sub_ls')
		button3 = types.InlineKeyboardButton('бизнес', callback_data = 'filter_sub_business')
		button4 = types.InlineKeyboardButton('красота', callback_data = 'filter_sub_beauty')
		button5 = types.InlineKeyboardButton('личностный рост', callback_data = 'filter_sub_growth')
		button6 = types.InlineKeyboardButton('назад', callback_data = 'filters')
		keyboard.row(button1, button2)
		keyboard.row(button3, button4)
		keyboard.add(button5, button6)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)
	elif call.data[:10] == 'filter_sub':
		key = call.data[11:]
		if key == 'sport':
			key = 'спорт'
		elif key == 'ls':
			key = 'лайфстайл'
		elif key == 'business':
			key = 'бизнес'
		elif key == 'beauty':
			key = 'красота'
		elif key == 'growth':
			key = 'личностный рост'
		check = False
		for sub in users[chat_id].filters[0]:
			if sub == key:
				users[chat_id].filters[0].remove(key)
				check = True
				break
		if check is False:
			users[chat_id].filters[0].append(key)
		users[chat_id].search_list = db.search_bloggers(users[chat_id].filters)
		users[chat_id].cur_blogger = 0
		refresh_search(call.message)
	elif call.data == 'filter_geo':
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('Нур-Султан', callback_data = 'filter_geo_nur')
		button2 = types.InlineKeyboardButton('Алматы', callback_data = 'filter_geo_ala')
		button3 = types.InlineKeyboardButton('Шымкент', callback_data = 'filter_geo_shym')
		button4 = types.InlineKeyboardButton('Караганда', callback_data = 'filter_geo_krg')
		button5 = types.InlineKeyboardButton('назад', callback_data = 'filters')
		keyboard.row(button1, button2)
		keyboard.row(button3, button4)
		keyboard.add(button5)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)
	elif call.data[:10] == 'filter_geo':
		key = call.data[11:]
		if key == 'nur':
			key = 'Нур-Султан'
		elif key == 'ala':
			key = 'Алматы'
		elif key == 'shym':
			key = 'Шымкент'
		elif key == 'krg':
			key = 'Караганда'
		check = False
		for sub in users[chat_id].filters[1]:
			if sub == key:
				users[chat_id].filters[1].remove(key)
				check = True
				break
		if check is False:
			users[chat_id].filters[1].append(key)
		users[chat_id].search_list = db.search_bloggers(users[chat_id].filters)
		users[chat_id].cur_blogger = 0
		refresh_search(call.message)
	elif call.data == 'filter_age':
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('13-17', callback_data = 'filter_age_13-17')
		button2 = types.InlineKeyboardButton('18-24', callback_data = 'filter_age_18-24')
		button3 = types.InlineKeyboardButton('25-34', callback_data = 'filter_age_25-34')
		button4 = types.InlineKeyboardButton('35-44', callback_data = 'filter_age_35-44')
		button5 = types.InlineKeyboardButton('45-54', callback_data = 'filter_age_45-54')
		button6 = types.InlineKeyboardButton('назад', callback_data = 'filters')
		keyboard.row(button1, button2)
		keyboard.row(button3, button4)
		keyboard.row(button5, button6)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)
	elif call.data[:10] == 'filter_age':
		key = call.data[11:]
		check = False
		for sub in users[chat_id].filters[2]:
			if sub == key:
				users[chat_id].filters[2].remove(key)
				check = True
				break
		if check is False:
			users[chat_id].filters[2].append(key)
		users[chat_id].search_list = db.search_bloggers(users[chat_id].filters)
		users[chat_id].cur_blogger = 0
		refresh_search(call.message)
	elif call.data == 'filter_gender':
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('мужчины', callback_data = 'filter_gender_male')
		button2 = types.InlineKeyboardButton('женщины', callback_data = 'filter_gender_female')
		button3 = types.InlineKeyboardButton('назад', callback_data = 'filters')
		keyboard.row(button1, button2)
		keyboard.row(button3)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)
	elif call.data[:13] == 'filter_gender':
		key = call.data[14:]
		if key == 'male':
			key = 'мужчины'
		if key == 'female':
			key = 'женщины'
		check = False
		for sub in users[chat_id].filters[3]:
			if sub == key:
				users[chat_id].filters[3].remove(key)
				check = True
				break
		if check is False:
			users[chat_id].filters[3].clear()
			users[chat_id].filters[3].append(key)
		users[chat_id].search_list = db.search_bloggers(users[chat_id].filters)
		users[chat_id].cur_blogger = 0
		refresh_search(call.message)
	elif call.data == 'sort':
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('подписчикам', callback_data = 'sort_followers')
		button2 = types.InlineKeyboardButton('назад', callback_data = 'search_back_main')
		keyboard.row(button1, button2)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)


def refresh_search(message):
	global users
	chat_id = message.chat.id
	if len(users[chat_id].search_list) == 0:
		text = 'К сожалению, у нас нет блогеров по данному запросу'
		text += '\n\nФильтры: '
		for a in users[chat_id].filters:
			for b in a:
				if b == a[-1] and a == users[chat_id].filters[-1]:
					text += b
				else:
					text += b + ', '
		bot.edit_message_text(chat_id = chat_id, message_id = users[chat_id].search_mess_id, \
			text = text, reply_markup = users[chat_id].last_keyboard)
		return
	users[chat_id].cur_blogger = 0
	cur_blogger = users[chat_id].cur_blogger
	blogger_id = users[chat_id].search_list[cur_blogger]
	profile = db.get_profile_by_id(blogger_id)
	profile = Blogger(profile)
	text = profile_info(profile)
	text += '\n\nФильтры: '
	for a in users[chat_id].filters:
		for b in a:
			if b == a[-1] and a == users[chat_id].filters[-1]:
				text += b
			else:
				text += b + ', '
	text += '\n\n' + str(cur_blogger+1) + '/' + str(len(users[chat_id].search_list))
	bot.edit_message_text(chat_id = chat_id, message_id = users[chat_id].search_mess_id, text = text,\
		reply_markup = users[chat_id].last_keyboard) 

bot.polling(none_stop=True)