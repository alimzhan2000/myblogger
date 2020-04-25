import telebot
import photos
import time
from database import Database
from telebot import types
from telebot.types import InputMediaPhoto
from profiles import Blogger, Order, categories, cities

token = "1084778927:AAGiGZSUjhh-U5YT0CzHhBwqZnRs2COBxOM" #mainbot
# token = "962351766:AAE_2ax6GANwka1ldGni2xMbV7-CPZboPEk" #testbot
bot = telebot.TeleBot(token)
db = Database()
users = {}

class Settings:
	def __init__(self):
		self.mode = 0
		self.blogger = None
		self.profile = Blogger()
		self.search_st = False
		self.search_mess_id = 0
		self.search_list = []
		self.cur_blogger = -1
		self.filters = [[], [], [], []]
		self.last_keyboard = None
		self.order = Order()
		self.orders_list = []
		self.cur_order = -1
		self.order_mess_id = 0
		self.match_bloggers = []
		self.cur_match_blogger = -1
		self.feedback_st = False
		self.match_orders = []
		self.match_orders_id = 0
		self.cur_match_order = -1
		self.profile_mess_id = 0
		self.profile_edit_mode = 0
		self.order_edit_mode = 0
		self.tmp = []
def add_new_user(chat_id):
	global users
	if chat_id in users.keys():
		return 
	a = Settings()
	users[chat_id] = a
def default_vars(chat_id):
	global users
	if chat_id not in users.keys():
		users[chat_id] = Settings()
		return
	tmp = users[chat_id].blogger
	users[chat_id] = Settings()
	users[chat_id].blogger = tmp
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
def order_info(order):
	text = 'Название бренда - ' + order.name + '\n'
	text += 'Логин в Instagram - ' + order.login + '\n'
	text += 'Рекламируемый продукт - ' + order.descr + '\n'
	text += 'Вариант продвижения - '
	if order.post_or_story == 'Оба варианта':
		text += 'Публикации и Истории'
	else:
		text += order.post_or_story
	text += '\nНеобходимый охват - ' + str(order.coverage)
	text += '\nЦелевая аудитория:'
	text += '\n География - '
	for city in order.geo:
		if city == order.geo[-1]:
			text += city
		else:
			text += city + ', '
	text += '\n Ср. возраст - '
	for age in order.age:
		if age == order.age[-1]:
			text += age + ' лет'
		else:
			text += age + ' лет, '
	text += '\n Пол - ' + order.gender
	text += '\nТематика продукта - ' + order.subject
	text += '\nБюджет - ' + str(order.budget) + ' тенге'
	if order.comment is not None:
		text += '\nДополнительные комментарии:\n' + order.comment
	return text
def main_menu(chat_id):
	global users
	default_vars(chat_id)
	keyboard = types.ReplyKeyboardMarkup(True, False)
	blogger = db.check_blogger(chat_id)
	order = db.check_order(chat_id)
	if users[chat_id].blogger is not None:
		if users[chat_id].blogger is False:
			keyboard.row('Поиск блогеров', 'Создать заказ')
			keyboard.row('Мои заказы', 'Обратная связь')
		elif blogger is True:
			keyboard.row('Мой профиль', 'Найти заказ')
			keyboard.row('Создать профиль', 'Обратная связь')
		else:
			keyboard.row('Я Блогер', 'Я Рекламодатель')
			bot.send_message(chat_id, 'Кем Вы являетесь?', reply_markup=keyboard)
			return
		bot.send_message(chat_id, 'Главное меню.', reply_markup = keyboard)
		return
	if blogger is False and order is False:
		users[chat_id].blogger = None
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Я Блогер', 'Я Рекламодатель')
		bot.send_message(chat_id, 'Кем Вы являетесь?', reply_markup=keyboard)
		return
	users[chat_id].blogger = blogger
	if blogger is True:
		keyboard.row('Мой профиль', 'Найти заказ')
		keyboard.row('Создать профиль', 'Обратная связь')
	else:
		keyboard.row('Поиск блогеров', 'Создать заказ')
		keyboard.row('Мои заказы', 'Обратная связь')
	bot.send_message(chat_id, 'Главное меню.', reply_markup = keyboard)	
def refresh_search(message):
	global users
	chat_id = message.chat.id
	if len(users[chat_id].search_list) == 0:
		text = 'К сожалению, у нас нет блогеров по данному запросу'
		text += '\n\nФильтры: '
		for i in range(4):
			n = len(users[chat_id].filters[i])
			if n > 0:
				if i == 0:
					text += '\nпо интересам - '
				if i == 1:
					text += '\nпо региону - '
				if i == 2:
					text += '\nпо возрасту - '
				if i == 3:
					text += '\nпо полу - '
			for j in range(n):
				text += users[chat_id].filters[i][j]
				if j != n - 1:
					text += ', '
		bot.edit_message_text(chat_id = chat_id, message_id = users[chat_id].search_mess_id, \
			text = text, reply_markup = users[chat_id].last_keyboard)
		return
	users[chat_id].cur_blogger = 0
	cur_blogger = users[chat_id].cur_blogger
	blogger_id = users[chat_id].search_list[cur_blogger]
	profile = db.get_profile_by_id(blogger_id)
	profile = Blogger(profile)
	text = profile_info(profile)
	text += '\n\nФильтры:'
	for i in range(4):
		n = len(users[chat_id].filters[i])
		if n > 0:
			if i == 0:
				text += '\nпо интересам - '
			if i == 1:
				text += '\nпо региону - '
			if i == 2:
				text += '\nпо возрасту - '
			if i == 3:
				text += '\nпо полу - '
		for j in range(n):
			text += users[chat_id].filters[i][j]
			if j != n - 1:
				text += ', '
			
	text += '\n\n' + str(cur_blogger+1) + '/' + str(len(users[chat_id].search_list))
	photo = photos.download_photo(profile.profile_photo_id)
	media = InputMediaPhoto(photo, caption = text)
	bot.edit_message_media(chat_id = chat_id, message_id = users[chat_id].search_mess_id, media = media,\
		reply_markup = users[chat_id].last_keyboard) 
def refresh_profile(message):
	global users
	chat_id = message.chat.id
	profile = Blogger(db.get_profile_by_chat_id(chat_id))
	info = profile_info(profile)
	try:
		bot.edit_message_caption(chat_id = chat_id, message_id = users[chat_id].profile_mess_id, caption = info, \
			reply_markup = users[chat_id].last_keyboard)
	except:
		pass
def refresh_order(message):
	global users
	chat_id = message.chat.id
	order_id = users[chat_id].orders_list[users[chat_id].cur_order][0]
	order = db.get_order_by_id(order_id)
	info = order_info(Order(order))
	info += '\n\n*Выбери то, что ты хочешь изменить*'
	keyboard = types.InlineKeyboardMarkup()
	button1 = types.InlineKeyboardButton('Название', callback_data = 'edit_order_name')
	button2 = types.InlineKeyboardButton('Логин', callback_data = 'edit_order_login')
	button3 = types.InlineKeyboardButton('Описание', callback_data = 'edit_descr')
	button4 = types.InlineKeyboardButton('Продвижение', callback_data = 'edit_post_or_story')
	button5 = types.InlineKeyboardButton('Охват', callback_data = 'edit_order_coverage')
	button6 = types.InlineKeyboardButton('Бюджет', callback_data = 'edit_budget')
	button7 = types.InlineKeyboardButton('Доп.комментарий', callback_data = 'edit_comments')
	button8 = types.InlineKeyboardButton('Целевая аудитория', callback_data = 'edit_target')
	button9 = types.InlineKeyboardButton('Назад', callback_data = 'back_to_order')
	keyboard.row(button1, button2, button3)
	keyboard.row(button4, button5, button6)
	keyboard.row(button7, button8)
	keyboard.row(button9)
	try:
		bot.edit_message_text(chat_id = chat_id, message_id = users[chat_id].order_mess_id, text = info,\
			parse_mode = 'Markdown', reply_markup = keyboard)
	except:
		pass
@bot.message_handler(commands = ['start'])
def start(message):
	chat_id = message.chat.id
	add_new_user(chat_id)
	default_vars(chat_id)
	keyboard = types.ReplyKeyboardMarkup(True, False)
	keyboard.row('Я Блогер', 'Я Рекламодатель')
	bot.send_message(message.chat.id, 'Привет! Я бот, который соединяет блогеров с их заказчиками и делает это самым\
	эффективным способом. Для начала нашей работы, скажи, ты блогер или рекламодатель?', reply_markup=keyboard)

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
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			bot.send_message(chat_id, 'Спасибо! Теперь мне нужно узнать охват одного stories\
			\n(P.S Зайди в раздел “статистика”, выбери “истории”, и далее “охват” за последние 14 дней)')
		elif users[chat_id].mode == 7:
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			n = len(cities)
			for i in range(1, n, 2):
				keyboard.row(cities[i-1], cities[i])
			if n % 2 != 0:
				keyboard.row(cities[n-1])
			bot.send_message(chat_id, 'Теперь давай узнаем с каких регионов у тебя подписчики.', reply_markup = keyboard)
		elif users[chat_id].mode == 9:
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('13-17', '18-24', '25-34')
			keyboard.row('35-44', '45-54')
			bot.send_message(chat_id, 'Спасибо :з Теперь нужно понять, какой средний возраст твоих подписчиков.', reply_markup = keyboard)
		elif users[chat_id].mode == 11:
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			bot.send_message(chat_id, 'Теперь нужно разделение твоих подписчиков по половому признаку в процентном соотношении.\
			Сколько процентов твоей аудитории женская?')
		elif users[chat_id].mode == 14:
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			n = len(categories)
			for i in range(1, n, 2):
				keyboard.row(categories[i-1], categories[i])
			if n % 2 != 0:
				keyboard.row(categories[n-1])
			bot.send_message(chat_id, 'Осталось еще 3 шага для создания твоего профиля!\
			Выбери тематику своего аккаунта\n(P.S. Можешь выбрать несколько)', reply_markup = keyboard)
		elif users[chat_id].mode == 18:
			users[chat_id].profile.profile_photo_id = photos.document_handler(message, bot)
			users[chat_id].profile.telegram_username = '@' + str(message.from_user.username)
			users[chat_id].mode = 0
			db.new_blogger(users[chat_id].profile)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Мой профиль', 'Найти заказ')
			keyboard.row('Создать профиль', 'Обратная связь')
			bot.send_message(chat_id, 'Прекрасно! Мы с тобой это сделали! Уже предвкушаю как тебе будут писать рекламодатели\
			и размещать свою рекламу :)) Надеюсь, мы теперь с тобой друзья. Если я тебе понравился, познакомь меня пожалуйста\
			еще со своими друзьями-блогерами. Я люблю общаться с творческими людьми!', reply_markup = keyboard)
	if users[chat_id].profile_edit_mode > 0:
		mode = users[chat_id].profile_edit_mode
		if mode == 3:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 0)
			refresh_profile(message)
			bot.send_message(chat_id, 'Ты успешно изменил средний охват публикации')
			users[chat_id].profile_edit_mode = 0
		elif mode == 4:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 1)
			refresh_profile(message)
			bot.send_message(chat_id, 'Ты успешно изменил средний охват истории')
			users[chat_id].profile_edit_mode = 0
		elif mode == 8:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 2)
			refresh_profile(message)
			bot.send_message(chat_id, 'Ты успешно изменил географию подписчиков')
			users[chat_id].profile_edit_mode = 0
		elif mode == 9:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 3)
			refresh_profile(message)
			bot.send_message(chat_id, 'Ты успешно изменил средний возраст подписчиков')
			users[chat_id].profile_edit_mode = 0
		elif mode == 10:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 4)
			refresh_profile(message)
			bot.send_message(chat_id, 'Ты успешно изменил распределение по половому признаку')
			users[chat_id].profile_edit_mode = 0

@bot.message_handler(func=lambda message:message.text == 'Назад в меню')
def main_menu_handler(message):
	main_menu(message.chat.id)

@bot.message_handler(func=lambda message:message.chat.id in users.keys() and users[message.chat.id].mode > 0 and users[message.chat.id].blogger == True)
def create_profile(message):
	global users
	chat_id = message.chat.id 
	if users[chat_id].mode == 1:
		users[chat_id].profile.name = message.text
		users[chat_id].profile.chat_id = chat_id
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Назад в меню')
		bot.send_message(chat_id, 'Введи название своего аккаунта в Instagram.\n(пример: @bloggerskz)', reply_markup=keyboard)
		users[chat_id].mode += 1
	elif users[chat_id].mode == 2:
		users[chat_id].profile.login = message.text
		bot.send_message(chat_id, 'Сколько у тебя подписчиков?\n(пример: 23500)')
		users[chat_id].mode += 1
	elif users[chat_id].mode == 3:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без букв и других символов')
			return
		users[chat_id].profile.followers = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Вау, это впечатляет. А какой у тебя охват одного поста?\
		\n(P.S. Можешь зайти у себя в инсте в раздел “статистика”, выбери “публикации”, и “охват” за последние 30 дней)')		
	elif users[chat_id].mode == 4:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без букв и других символов')
			return
		users[chat_id].profile.avg_post_coverage = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Так, теперь чтобы я тебе полностью поверил, пришли пожалуйста скриншот этой страницы с охватом.')
	elif users[chat_id].mode == 6:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без букв и других символов')
			return
		users[chat_id].profile.avg_story_coverage = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'И еще один скриншот-подтверждение пожалуйста. Пойми, нас просто начальство проверяет🙁')
	elif users[chat_id].mode == 8:
		if message.text == 'Следующий шаг':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Назад в меню')
			bot.send_message(chat_id, 'Я наверное уже надоел с этим, но нужно и для этого скриншот-подтверждение.\
			Для этого, зайди в “статистика”, выбери “аудитория” и “топ-местоположений” по городам.', reply_markup = keyboard)
			return
		users[chat_id].profile.followers_geo.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		keyboard.row('Следующий шаг')
		if len(users[chat_id].profile.followers_geo) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько городов или нажать "Следующий шаг", чтобы перейти к следующему этапу.', reply_markup = keyboard)
	elif users[chat_id].mode == 10:
		if message.text == 'Следующий шаг':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Назад в меню')
			bot.send_message(chat_id, 'Так, начальство требует и для этого подтверждение. Пришли скриншот и для этого\
			пожалуйста (Зайди в раздел “статистика”, далее выбери “аудитория” и “возрастной диапазон” всех подписчиков).\
			Не переживай, нам осталось совсем немного', reply_markup=keyboard)
			return
		users[chat_id].profile.avg_age.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		keyboard.row('Следующий шаг')
		if len(users[chat_id].profile.avg_age) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько диапозонов или нажать "Следующий шаг", чтобы перейти к следующему этапу.', reply_markup = keyboard)
	elif users[chat_id].mode == 12:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без букв и других символов')
			return
		users[chat_id].profile.female_ratio = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'А сколько процентов аудитории мужская?')
	elif users[chat_id].mode == 13:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без букв и других символов')
			return
		users[chat_id].profile.male_ratio = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'И так, это последний скриншот, который я у тебя попрошу. Зайди в “статистика”,\
		выбери “аудитория” и “пол”')
	elif users[chat_id].mode == 15:
		if message.text == 'Следующий шаг':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Назад в меню')
			bot.send_message(chat_id, 'А теперь десерт. Мне нужно знать сколько ты хочешь зарабатывать на одном посте.\
			Введи сумму в тенге.', reply_markup = keyboard)
			return
		users[chat_id].profile.subjects.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		keyboard.row('Следующий шаг')
		if len(users[chat_id].profile.subjects) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько тематик или нажать "Следующий шаг",\
			чтобы перейти к следующему этапу.', reply_markup = keyboard)
	elif users[chat_id].mode == 16:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без букв и других символов')
			return
		users[chat_id].profile.post_price = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Неплохо, но если вдруг тебе не будут писать довольно долгое время, ты всегда можешь\
		изменить цену и весь свой профиль у себя в кабинете. Для этого нужно будет зайти в “Мой профиль”')
		bot.send_message(chat_id, 'И так, последний вопрос! Сколько ты хочешь зарабатывать на одном stories?')
	elif users[chat_id].mode == 17:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без букв и других символов')
			return
		users[chat_id].profile.story_price = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Теперь тебе осталось только отправить мне фотографию своего профиля.')

@bot.message_handler(func=lambda message:message.chat.id in users.keys() and users[message.chat.id].mode > 0 and users[message.chat.id].blogger == False)
def create_order(message):
	global users
	chat_id = message.chat.id
	if users[chat_id].mode == 1:
		users[chat_id].order.name = message.text
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Теперь укажи аккаунт бренда в инстаграме.\n(пример: @mybloggerkz)')
	elif users[chat_id].mode == 2:
		users[chat_id].order.login = message.text
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Прекрасно! Что мы собираемся продвигать?(пример: косметика из натуральных компонентов)')		 
	elif users[chat_id].mode == 3:
		users[chat_id].order.descr = message.text
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Публикация', 'История')
		keyboard.row('Оба варианта')
		bot.send_message(chat_id, 'Теперь укажи какой вариант продвижения тебя интересует', reply_markup=keyboard)
	elif users[chat_id].mode == 4:
		if message.text != 'Публикация' and message.text != 'История' and message.text != 'Оба варианта':
			bot.send_message(chat_id, 'Неправильный ввод! Прошу тебя воспользоваться клавиатурой\
			или отправить сообщением один из вариантов.\n1.Публикация\n2.История\n3.Оба варианта')
			return
		users[chat_id].order.post_or_story = message.text
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.add('Назад в меню')
		bot.send_message(chat_id, 'Какой необходимый охват для продвижения?\n(пример: 25000)', reply_markup = keyboard)
	elif users[chat_id].mode == 5:
		if message.text.isdigit() is False:
			bot.send_message(chat_id, 'Прошу тебя ввести целое число без других символов.')
			return
		users[chat_id].order.coverage = int(message.text)
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		bot.send_message(chat_id, 'Какая география у твоей целевой аудитории?', reply_markup = keyboard)
	elif users[chat_id].mode == 6:
		if message.text == 'Следующий шаг':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('13-17', '18-24', '25-34')
			keyboard.row('35-44', '45-54')
			bot.send_message(chat_id, 'Какой средний возраст у твоей целевой аудитории.', reply_markup = keyboard)
			return
		users[chat_id].order.geo.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		keyboard.row('Следующий шаг')
		if len(users[chat_id].order.geo) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько городов или нажать "Следующий шаг", чтобы перейти к следующему этапу.', reply_markup = keyboard)
	elif users[chat_id].mode == 7:
		if message.text == 'Следующий шаг':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Мужчины', 'Женщины')
			keyboard.row('Все')
			bot.send_message(chat_id, 'Так, теперь нужно указать какой пол у твоей аудитории.', reply_markup=keyboard)
			return
		users[chat_id].order.age.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		keyboard.row('Следующий шаг')
		if len(users[chat_id].order.age) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько диапозонов или нажать "Следующий шаг", чтобы перейти к следующему этапу.', reply_markup = keyboard)
	elif users[chat_id].mode == 8:
		if message.text != 'Мужчины' and message.text != 'Женщины' and message.text != 'Все':
			bot.send_message(chat_id, 'Неправильный ввод! Прошу тебя воспользоваться клавиатурой\
			или отправить сообщением один из вариантов.\n1.Мужчины\n2.Женщины\n3.Все')
			return
		users[chat_id].order.gender = message.text
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		bot.send_message(chat_id, 'Осталось всего два шага до поиска самых эффективных тебе блогеров!')
		bot.send_message(chat_id, 'Укажи интересы своих клиентов рекламируемого бренда или продукта.', reply_markup = keyboard)
	elif users[chat_id].mode == 9:
		users[chat_id].order.subject = message.text
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.add('Назад в меню')
		bot.send_message(chat_id, 'И последний шаг. Какой бюджет у твоей рекламной кампании?\n(пример: 65000)', reply_markup = keyboard)
	elif users[chat_id].mode == 10:
		if message.text.isdigit() is False:
			bot.send_message(chat_id, 'Неправильный ввод! Прошу тебя ввести целое число без других символов.')
			return
		users[chat_id].order.budget = int(message.text)
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Пропустить')
		bot.send_message(chat_id, 'Оставьте дополнительные комментарии (Здесь может быть ваше видение того, как блогеру\
		нужно преподнести ваш продукт - минимальное техническое задание)', reply_markup = keyboard)
	elif users[chat_id].mode == 11:
		if message.text == 'Пропустить':
			users[chat_id].order.comment = None
		else:
			users[chat_id].order.comment = message.text
		users[chat_id].order.chat_id = str(chat_id)
		users[chat_id].order.telegram_username = '@' + str(message.from_user.username)
		print(users[chat_id].order.telegram_username)
		db.new_order(users[chat_id].order)
		bot.send_message(chat_id, order_info(users[chat_id].order))
		time.sleep(2)
		users[chat_id].mode = 0
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск блогеров', 'Создать заказ')
		keyboard.row('Мои заказы', 'Обратная связь')
		bot.send_message(chat_id, 'Ура! Мы сформировали тебе заказ, для того чтобы просмотреть подходящих блогеров или\
			что-то изменить, зайди в “Мои заказы” в своем кабинете. Если тебе понравилось наше знакомство, я буду очень рад,\
			если ты расскажешь про меня своим коллегам или друзьям. Чем больше друзей, тем лучше. Люблю общаться с деловыми\
			людьми!', reply_markup = keyboard)

@bot.message_handler(func=lambda message:message.chat.id in users.keys() and users[message.chat.id].profile_edit_mode > 0)
def edit_profile(message):
	global users
	chat_id = message.chat.id
	mode = users[chat_id].profile_edit_mode
	if mode == 1:
		db.profile_edit_name(chat_id, message.text)
		refresh_profile(message)
		bot.send_message(chat_id, 'Ты успешно изменил свое имя')
		users[chat_id].profile_edit_mode = 0
	elif mode == 2:
		db.profile_edit_login(chat_id, message.text)
		refresh_profile(message)
		bot.send_message(chat_id, 'Ты успешно изменил свой логин')
		users[chat_id].profile_edit_mode = 0
	elif mode == 3:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без других символов')
			return
		db.profile_edit_post_cvg(chat_id, int(message.text))
		bot.send_message(chat_id, 'Теперь пришли нам скриншот-подтверждение\n(P.S. Зайди у себя в инсте в раздел\
		“статистика”, выбери “публикации”, и “охват” за последние 30 дней)')
	elif mode == 4:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без других символов')
			return
		db.profile_edit_story_cvg(chat_id, int(message.text))
		bot.send_message(chat_id, 'Теперь пришли нам скриншот-подтверждение\n(P.S. Зайди у себя в инсте в раздел\
		“статистика”, выбери “истории”, и далее “охват” за последние 14 дней)')
	elif mode == 5:
		if message.text == 'Изменить':
			db.profile_edit_subjects(chat_id, users[chat_id].tmp)
			users[chat_id].tmp = []
			refresh_profile(message)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Мой профиль', 'Найти заказ')
			keyboard.row('Создать профиль', 'Обратная связь')
			bot.send_message(chat_id, 'Изменения успешно применены', reply_markup = keyboard)
			users[chat_id].profile_edit_mode = 0
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		keyboard.row('Изменить')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько тематик или нажать "Изменить",\
			чтобы применить изменения.', reply_markup = keyboard)
	elif mode == 6:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без других символов')
			return
		db.profile_edit_post_price(chat_id, int(message.text))
		users[chat_id].profile_edit_mode = 7
		bot.send_message(chat_id, 'Хорошо, теперь напиши стоимость одной истории')
	elif mode == 7:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без других символов')
			return
		db.profile_edit_story_price(chat_id, int(message.text))
		refresh_profile(message)
		users[chat_id].profile_edit_mode = 0
		bot.send_message(chat_id, 'Цены за рекламную интеграцию успешно изменены ;)')
	elif mode == 8:
		if message.text == 'Изменить':
			db.profile_edit_geo(chat_id, users[chat_id].tmp)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Мой профиль', 'Найти заказ')
			keyboard.row('Создать профиль', 'Обратная связь')
			bot.send_message(chat_id, 'Теперь пришли нам скриншот-подтверждение\n(P.S. Зайди в раздел\
			“статистика”, выбери “аудитория” и “топ-местоположений” по городам)', reply_markup = keyboard)
			users[chat_id].tmp = []
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		keyboard.row('Изменить')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько городов или нажать "Изменить",\
			чтобы применить изменения.', reply_markup = keyboard)
	elif mode == 9:
		if message.text == 'Изменить':
			db.profile_edit_age(chat_id, users[chat_id].tmp)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Мой профиль', 'Найти заказ')
			keyboard.row('Создать профиль', 'Обратная связь')
			bot.send_message(chat_id, 'Теперь пришли нам скриншот-подтверждение\n(P.S. Зайди в раздел\
			“статистика”, далее выбери “аудитория” и “возрастной диапазон” всех подписчиков)', reply_markup = keyboard)
			users[chat_id].tmp = []
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		keyboard.row('Изменить')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько диапозонов или нажать "Изменить",\
			чтобы применить изменения.', reply_markup = keyboard)		
	elif mode == 10:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без других символов')
			return
		if int(message.text) < 0 or int(message.text) > 100:
			bot.send_message(chat_id, 'Введи целое число от 0 до 100')
			return
		db.profile_edit_gender(chat_id, int(message.text))
		bot.send_message(chat_id, 'Теперь пришли нам скриншот-подтверждение\n(P.S. Зайди в раздел\
			“статистика”, далее выбери “аудитория” и “пол”)')
	elif mode == 11:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без других символов')
			return
		db.profile_edit_followers(chat_id, int(message.text))
		users[chat_id].profile_edit_mode = 0
		refresh_profile(message)
		bot.send_message(chat_id, 'Количество твоих подписчиков успешно изменено')

@bot.message_handler(func=lambda message:message.chat.id in users.keys() and users[message.chat.id].order_edit_mode > 0)
def edit_order(message):
	global users
	chat_id = message.chat.id
	mode = users[chat_id].order_edit_mode
	orders_list = users[chat_id].orders_list
	cur_order = users[chat_id].cur_order
	order_id = orders_list[cur_order][0]
	if mode == 1:
		db.order_edit_name(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Название бренда успешно изменено')
	elif mode == 2:
		db.order_edit_login(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Логин бренда успешно изменен')
	elif mode == 3:
		db.order_edit_descr(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Описание вашего продукта успешно изменено')
	elif mode == 4:
		db.order_edit_post_or_story(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Вариант продвижения успешно изменен')
	elif mode == 5:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без других символов')
			return
		db.order_edit_coverage(order_id, int(message.text))
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Необходимый охват для продвижения успешно изменен')
	elif mode == 6:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Пожалуйста, введи целое число без других символов')
			return
		db.order_edit_budget(order_id, int(message.text))
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Бюджет успешно изменен')
	elif mode == 7:
		db.order_edit_comment(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Дополнительные комментарии к заказу успешно изменены')
	elif mode == 8:
		if message.text == 'Изменить':
			db.order_edit_geo(order_id, users[chat_id].tmp)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Поиск блогеров', 'Создать заказ')
			keyboard.row('Мои заказы', 'Обратная связь')
			bot.send_message(chat_id, 'География твоей целевой аудитории успешно изменена', reply_markup = keyboard)
			users[chat_id].tmp = []
			refresh_order(message)
			users[chat_id].order_edit_mode = 0
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		keyboard.row('Изменить')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько городов или нажать "Изменить",\
			чтобы применить изменения.', reply_markup = keyboard)
	elif mode == 9:
		if message.text == 'Изменить':
			db.order_edit_age(order_id, users[chat_id].tmp)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Поиск блогеров', 'Создать заказ')
			keyboard.row('Мои заказы', 'Обратная связь')
			bot.send_message(chat_id, 'Средний возраст твоей целевой аудитории успешно изменен', reply_markup = keyboard)
			users[chat_id].tmp = []
			refresh_order(message)
			users[chat_id].order_edit_mode = 0
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		keyboard.row('Изменить')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'Ты можешь выбрать несколько диапозонов или нажать "Изменить",\
			чтобы применить изменения.', reply_markup = keyboard)
	elif mode == 10:
		db.order_edit_subject(order_id, message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск блогеров', 'Создать заказ')
		keyboard.row('Мои заказы', 'Обратная связь')
		bot.send_message(chat_id, 'Интересы твоей целевой аудитории успешно изменены', reply_markup = keyboard)
		refresh_order(message)
		users[chat_id].order_edit_mode = 0
	elif mode == 11:
		db.order_edit_gender(order_id, message.text)
		refresh_order(message)
		users[chat_id].order_edit_mode = 0
		bot.send_message(chat_id, 'Пол целевой аудитории успешно изменен')

		
@bot.message_handler(content_types = ['text'])
def get_message(message):
	global users
	chat_id = message.chat.id
	if message.text == 'Я Блогер':
		users[chat_id].blogger = True
		if db.check_blogger(chat_id) is True:
			main_menu(chat_id)
			return
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Создать профиль')
		bot.send_message(chat_id, 'Итак, будущая звезда, в этом разделе ты можешь создать свой профиль или посмотреть свой\
		действующий. Также, ты можешь сам найти заказ. Для начала тебе необходимо создать свой профиль.', reply_markup = keyboard)
	elif message.text == 'Создать профиль':
		if db.check_blogger(chat_id) is True:
			bot.send_message(chat_id, 'Вы не можете создать больше одного профиля. Для того, чтобы создать\
			новый профиль необходимо удалить старый.')
			return
		users[chat_id].mode = 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Назад в меню')
		bot.send_message(chat_id, 'Отлично! Я совсем забыл представиться, меня зовут Ходор, а как тебя?', reply_markup = keyboard)
	elif message.text == 'Найти заказ':
		blogger = Blogger(db.get_profile_by_chat_id(chat_id))
		match_orders = users[chat_id].match_orders = db.get_match_orders(blogger)
		cur_match_order = users[chat_id].cur_match_order = 0
		keyboard = types.InlineKeyboardMarkup()
		if len(match_orders) > 1:
			keyboard.add(types.InlineKeyboardButton('Следующий заказ >>', callback_data = 'next_match_order'))
		keyboard.add(types.InlineKeyboardButton('Пригласить к сотрудничеству', callback_data = 'invite_order'))
		order = Order(match_orders[cur_match_order])
		info = order_info(order)
		mess = bot.send_message(chat_id = chat_id, text = info, reply_markup = keyboard)
		users[chat_id].match_orders_id = mess.message_id
	elif message.text == 'Мой профиль':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		photo = photos.download_photo(profile.profile_photo_id)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Редактировать профиль', callback_data = 'edit_profile')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Удалить профиль', callback_data = 'delete_profile')
		keyboard.add(button)
		users[chat_id].last_keyboard = keyboard
		mess = bot.send_photo(chat_id, photo, info, reply_markup = keyboard)
		users[chat_id].profile_mess_id = mess.message_id
	elif message.text == 'Я Рекламодатель':
		users[chat_id].blogger = False
		if db.check_order(chat_id) is True:
			main_menu(chat_id)
			return
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск блогеров', 'Создать заказ')
		keyboard.row('Мои заказы', 'Обратная связь')
		bot.send_message(chat_id, 'Итак, для начала выбери что ты хочешь сделать. Ты можешь создать заказ, найти блогера и увидеть свои заказы.',\
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
		photo = photos.download_photo(profile.profile_photo_id)
		mess = bot.send_photo(chat_id, photo, text, reply_markup = keyboard) 
		users[chat_id].search_mess_id = mess.message_id
	elif message.text == 'Создать заказ':
		orders_list = db.get_orders_by_chat_id(chat_id)
		if orders_list is not None:
			keyboard = types.InlineKeyboardMarkup()
			keyboard.row(types.InlineKeyboardButton('Да', callback_data = 'create_order_true'),\
				types.InlineKeyboardButton('Нет', callback_data = 'create_order_false'))
			bot.send_message(chat_id, 'У тебя уже есть следующее количество активных заказов: '\
				+ '*' + str(len(orders_list)) + '*\nХочешь ли ты создать новый заказ?', reply_markup = keyboard,\
				parse_mode = 'Markdown')
			return
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.add('Назад в меню')
		users[chat_id].mode = 1
		bot.send_message(chat_id, 'Отлично! Теперь мне нужно знать название твоего бренда.', reply_markup = keyboard)
	elif message.text == 'Мои заказы':
		users[chat_id].orders_list = db.get_orders_by_chat_id(chat_id)
		orders_list = users[chat_id].orders_list
		cur_order = users[chat_id].cur_order = 0
		if users[chat_id].orders_list is None:
			bot.send_message(chat_id, 'У тебя пока еще нет активных заказов. Чтобы создать заказ\
			нажмите на кнопку *"Создать заказ"*', parse_mode = 'Markdown')
			return
		keyboard = types.InlineKeyboardMarkup()
		if len(users[chat_id].orders_list) > 1:
			button1 = types.InlineKeyboardButton('Следующий заказ >>', callback_data = 'next_order')
			keyboard.add(button1)
		button2 = types.InlineKeyboardButton('Подобрать подходящих блогеров', callback_data = 'match_bloggers')
		button4 = types.InlineKeyboardButton('Редактировать заказ', callback_data = 'edit_order')
		button3 = types.InlineKeyboardButton('Удалить заказ', callback_data = 'delete_order')
		keyboard.add(button2)
		keyboard.add(button4)
		keyboard.add(button3)
		info = order_info(Order(orders_list[cur_order]))
		mess = bot.send_message(chat_id, info, reply_markup = keyboard)
		users[chat_id].order_mess_id = mess.message_id
	elif message.text == 'Обратная связь' or users[chat_id].feedback_st == True:
		if users[chat_id].feedback_st == False:
			users[chat_id].feedback_st = True
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Назад в меню')
			bot.send_message(chat_id, 'Оставьте свой отзыв или предложение, отправив нам сообщение!', reply_markup=keyboard)
		else:
			bot.send_message(365391038, str(message.text) + '\nот ' + str(message.from_user.last_name) + ' ' + str(message.from_user.first_name) + ' @' + str(message.from_user.username) )
			default_vars(chat_id)
			bot.send_message(chat_id, 'Спасибо за оставленный отзыв!')
			main_menu(chat_id)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	global users
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
		photo = photos.download_photo(profile.profile_photo_id)
		media = InputMediaPhoto(photo, caption = text)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_media(chat_id = chat_id, message_id = search_mess_id, media = media, reply_markup = keyboard)
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
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(types.InlineKeyboardButton(categories[i-1], callback_data = 'filter_sub' + str(i-1))\
				, types.InlineKeyboardButton(categories[i], callback_data = 'filter_sub' + str(i)))
		if n % 2 != 0:
			button6 = types.InlineKeyboardButton('Назад', callback_data = 'filters')
			keyboard.row(types.InlineKeyboardButton(categories[n-1], callback_data = 'filter_sub' + str(n-1)), button6)
		else:	
			button6 = types.InlineKeyboardButton('Назад', callback_data = 'filters')
			keyboard.row(button6)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)
	elif call.data[:10] == 'filter_sub':
		key = categories[int(call.data[10:])]
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
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(types.InlineKeyboardButton(cities[i-1], callback_data = 'filter_geo' + str(i-1))\
				, types.InlineKeyboardButton(cities[i], callback_data = 'filter_geo' + str(i)))
		if n % 2 != 0:
			button6 = types.InlineKeyboardButton('Назад', callback_data = 'filters')
			keyboard.row(types.InlineKeyboardButton(cities[n-1], callback_data = 'filter_geo' + str(n-1)), button6)
		else:	
			button6 = types.InlineKeyboardButton('Назад', callback_data = 'filters')
			keyboard.row(button6)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)
	elif call.data[:10] == 'filter_geo':
		key = cities[int(call.data[10:])]
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
	elif call.data == 'next_order' or call.data == 'prev_order' or call.data == 'back_to_order':
		users[chat_id].cur_order += 1
		if call.data == 'prev_order':
			users[chat_id].cur_order -= 2
		elif call.data == 'back_to_order':
			users[chat_id].cur_order -= 1
		cur_order = users[chat_id].cur_order
		orders_list = users[chat_id].orders_list
		order_mess_id = users[chat_id].order_mess_id
		keyboard = types.InlineKeyboardMarkup()
		if cur_order < 0 or cur_order >= len(orders_list):
			if call.data == 'prev_order':
				users[chat_id].cur_order += 2
			else:
				users[chat_id].cur_order -= 1
			return
		if cur_order != len(orders_list) - 1 and cur_order > 0:
			button1 = types.InlineKeyboardButton('След >>', callback_data = 'next_order')
			button2 = types.InlineKeyboardButton('<< Пред', callback_data = 'prev_order')
			keyboard.row(button2, button1)
		elif cur_order != len(orders_list) - 1:
			keyboard.add(types.InlineKeyboardButton('Следующий заказ >>', callback_data = 'next_order'))
		elif cur_order > 0:
			keyboard.add(types.InlineKeyboardButton('<< Предыдущий заказ', callback_data = 'prev_order'))			
		button = types.InlineKeyboardButton('Подобрать подходящих блогеров', callback_data = 'match_bloggers')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Редактировать заказ', callback_data = 'edit_order')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Удалить заказ', callback_data = 'delete_order')
		keyboard.add(button)
		info = order_info(Order(orders_list[cur_order]))
		if call.data == 'back_to_order':
			bot.delete_message(chat_id = chat_id, message_id = order_mess_id)
			mess = bot.send_message(chat_id, info, reply_markup = keyboard)
			users[chat_id].order_mess_id = mess.message_id
		else:
			bot.edit_message_text(chat_id = chat_id, message_id = order_mess_id, text = info, reply_markup = keyboard)
	elif call.data == 'delete_order':
		db.delete_order(users[chat_id].orders_list[users[chat_id].cur_order][0])
		bot.edit_message_text(chat_id = chat_id, message_id = users[chat_id].order_mess_id, text = 
			'Ваш заказ был успешно удален!')
		main_menu(chat_id)
	elif call.data == 'create_order_true':
		bot.delete_message(chat_id = chat_id, message_id = call.message.message_id)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.add('Назад в меню')
		users[chat_id].mode = 1
		bot.send_message(chat_id, 'Какое название у твеого бренда?', reply_markup = keyboard)
	elif call.data == 'create_order_false':
		bot.delete_message(chat_id = chat_id, message_id = call.message.message_id)
		main_menu(chat_id)
	elif call.data == 'match_bloggers':
		order = Order(users[chat_id].orders_list[users[chat_id].cur_order])
		match_bloggers = users[chat_id].match_bloggers = db.get_match_bloggers(order)
		cur_match_blogger = users[chat_id].cur_match_blogger = 0
		keyboard = types.InlineKeyboardMarkup()
		if len(match_bloggers) > 1:
			keyboard.add(types.InlineKeyboardButton('Следующий блогер >>', callback_data = 'next_match_blogger'))
		keyboard.add(types.InlineKeyboardButton('Пригласить к сотрудничеству', callback_data = 'invite_blogger'))
		keyboard.add(types.InlineKeyboardButton('Назад к заказу', callback_data = 'back_to_order'))
		blogger = Blogger(match_bloggers[cur_match_blogger])
		info = profile_info(blogger)
		photo = photos.download_photo(blogger.profile_photo_id)
		bot.delete_message(chat_id = chat_id, message_id = users[chat_id].order_mess_id)
		mess = bot.send_photo(chat_id, photo, info, reply_markup = keyboard)
		users[chat_id].order_mess_id = mess.message_id
	elif call.data == 'next_match_blogger' or call.data == 'prev_match_blogger':
		users[chat_id].cur_match_blogger += 1
		if call.data == 'prev_match_blogger':
			users[chat_id].cur_match_blogger -= 2
		cur_match_blogger = users[chat_id].cur_match_blogger
		match_bloggers = users[chat_id].match_bloggers
		order_mess_id = users[chat_id].order_mess_id
		keyboard = types.InlineKeyboardMarkup()
		if cur_match_blogger < 0 or cur_match_blogger >= len(match_bloggers):
			if call.data == 'prev_match_blogger':
				users[chat_id].cur_match_blogger += 2
			else:
				users[chat_id].cur_match_blogger -= 1
			return
		if cur_match_blogger != len(match_bloggers) - 1 and cur_match_blogger > 0:
			button1 = types.InlineKeyboardButton('След >>', callback_data = 'next_match_blogger')
			button2 = types.InlineKeyboardButton('<< Пред', callback_data = 'prev_match_blogger')
			keyboard.row(button2, button1)
		elif cur_match_blogger != len(match_bloggers) - 1:
			keyboard.add(types.InlineKeyboardButton('Следующий заказ >>', callback_data = 'next_match_blogger'))
		elif cur_match_blogger > 0:
			keyboard.add(types.InlineKeyboardButton('<< Предыдущий заказ', callback_data = 'prev_match_blogger'))			
		keyboard.add(types.InlineKeyboardButton('Пригласить к сотрудничеству', callback_data = 'invite_blogger'))
		keyboard.add(types.InlineKeyboardButton('Назад к заказу', callback_data = 'back_to_order'))
		blogger = Blogger(match_bloggers[cur_match_blogger])
		info = profile_info(blogger)
		photo = photos.download_photo(blogger.profile_photo_id)
		media = InputMediaPhoto(photo, caption = info)
		bot.edit_message_media(chat_id = chat_id, message_id = users[chat_id].order_mess_id\
			, media = media, reply_markup = keyboard)
	elif call.data == 'invite_blogger':
		blogger_chat_id = users[chat_id].match_bloggers[users[chat_id].cur_match_blogger][13]
		bot.send_message(blogger_chat_id, 'Вам пришло приглашение к сотрудничеству. Подбробная информация о\
		рекламодателе будет отправлена в следующем сообщении.')
		info = order_info(Order(users[chat_id].orders_list[users[chat_id].cur_order]))
		bot.send_message(blogger_chat_id, info)
		bot.send_message(blogger_chat_id, 'Если Вы согласны сотрудничать просим Вас свзяаться напрямую\
			с рекламодетелем через мессенджер Telegram.\nTelegram аккаунт рекламодателя: ' + \
			users[chat_id].orders_list[users[chat_id].cur_order][13])
		bot.send_message(chat_id, 'Приглашение к сотрудничеству данному блогеру было отправлено.\
			Ожидайте обратной связи.')
	elif call.data == 'next_match_order' or call.data == 'prev_match_order':
		users[chat_id].cur_match_order += 1
		if call.data == 'prev_match_order':
			users[chat_id].cur_match_order -= 2
		cur_match_order = users[chat_id].cur_match_order
		match_orders = users[chat_id].match_orders
		match_orders_id = users[chat_id].match_orders_id
		keyboard = types.InlineKeyboardMarkup()
		if cur_match_order < 0 or cur_match_order >= len(match_orders):
			if call.data == 'prev_match_order':
				users[chat_id].cur_match_order += 2
			else:
				users[chat_id].cur_match_order -= 1
			return
		if cur_match_order != len(match_orders) - 1 and cur_match_order > 0:
			button1 = types.InlineKeyboardButton('След >>', callback_data = 'next_match_order')
			button2 = types.InlineKeyboardButton('<< Пред', callback_data = 'prev_match_order')
			keyboard.row(button2, button1)
		elif cur_match_order != len(match_orders) - 1:
			keyboard.add(types.InlineKeyboardButton('Следующий заказ >>', callback_data = 'next_match_order'))
		elif cur_match_order > 0:
			keyboard.add(types.InlineKeyboardButton('<< Предыдущий заказ', callback_data = 'prev_match_order'))			
		button = types.InlineKeyboardButton('Пригласить к сотрудничеству', callback_data = 'invite_order')
		keyboard.add(button)
		info = order_info(Order(match_orders[cur_match_order]))
		bot.edit_message_text(chat_id = chat_id, message_id = match_orders_id, text = info, reply_markup = keyboard)
	elif call.data == 'invite_order':
		order_chat_id = users[chat_id].match_orders[users[chat_id].cur_match_order][12]
		bot.send_message(order_chat_id, 'Вам пришло приглашение к сотрудничеству. Подробная информация о\
		блогере будет отправлена в следующем сообщении.')
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		bot.send_message(order_chat_id, info)
		bot.send_message(order_chat_id, 'Если Вы согласны сотрудничать просим Вас свзяаться напрямую\
			с блогером через мессенджер Telegram.\nTelegram аккаунт блогера: ' + profile.telegram_username)
		bot.send_message(chat_id, 'Приглашение к сотрудничеству данному рекламодателю было отправлено.\
			Ожидайте обратной связи.')
	elif call.data == 'edit_profile':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		info += '\n\n*Выбери то, что ты хочешь изменить*'
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('Имя', callback_data = 'edit_name')
		button2 = types.InlineKeyboardButton('Логин', callback_data = 'edit_login')
		button3 = types.InlineKeyboardButton('Охват', callback_data = 'edit_coverage')
		button4 = types.InlineKeyboardButton('Тематика', callback_data = 'edit_subjects')
		button5 = types.InlineKeyboardButton('Цена рекламы', callback_data = 'edit_price')
		button6 = types.InlineKeyboardButton('Данные о подписчиках', callback_data = 'edit_followers')
		button7 = types.InlineKeyboardButton('Назад', callback_data = 'back_to_profile')
		keyboard.row(button1, button2)
		keyboard.row(button3, button4)
		keyboard.row(button5)
		keyboard.row(button6)
		keyboard.row(button7)
		bot.edit_message_caption(chat_id = chat_id, message_id = users[chat_id].profile_mess_id, caption = info,\
			parse_mode = 'Markdown', reply_markup = keyboard)
	elif call.data == 'edit_name':
		users[chat_id].profile_edit_mode = 1
		bot.send_message(chat_id, 'Напиши мне свое новое имя')
	elif call.data == 'edit_login':
		users[chat_id].profile_edit_mode = 2
		bot.send_message(chat_id, 'Напиши мне свой логин в Instagram')
	elif call.data == 'edit_coverage':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		info += '\n\n*Охват чего ты хочешь изменить?*'
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('Публикации', callback_data = 'edit_post_coverage')
		button2 = types.InlineKeyboardButton('Истории', callback_data = 'edit_story_coverage')
		button3 = types.InlineKeyboardButton('Назад', callback_data = 'edit_profile')
		keyboard.row(button1, button2)
		keyboard.row(button3)
		bot.edit_message_caption(chat_id = chat_id, message_id = users[chat_id].profile_mess_id, caption = info, \
			parse_mode = 'Markdown', reply_markup = keyboard)
	elif call.data == 'edit_post_coverage':
		users[chat_id].profile_edit_mode = 3
		bot.send_message(chat_id, 'Укажи новый охват одной публикации')
	elif call.data == 'edit_story_coverage':
		users[chat_id].profile_edit_mode = 4
		bot.send_message(chat_id, 'Укажи новый охват одной истории')
	elif call.data == 'edit_subjects':
		users[chat_id].profile_edit_mode = 5
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		bot.send_message(chat_id, 'Укажи тематики своего аккаунта', reply_markup = keyboard)
	elif call.data == 'edit_price':
		users[chat_id].profile_edit_mode = 6
		bot.send_message(chat_id, 'Напиши новую стоимость рекламной интеграции за одну публикацию(в тенге)')
	elif call.data == 'edit_followers':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		info += '\n\n*Какую инфорацию о подписчиках ты хочешь изменить?*'
		keyboard = types.InlineKeyboardMarkup()
		button5 = types.InlineKeyboardButton('Количество', callback_data = 'edit_followers_num')
		button1 = types.InlineKeyboardButton('География', callback_data = 'edit_geo')
		button2 = types.InlineKeyboardButton('Средний возраст', callback_data = 'edit_age')
		button3 = types.InlineKeyboardButton('Пол', callback_data = 'edit_gender')
		button4 = types.InlineKeyboardButton('Назад', callback_data = 'edit_profile')
		keyboard.row(button1)
		keyboard.row(button2)
		keyboard.row(button3)
		keyboard.row(button4)
		bot.edit_message_caption(chat_id = chat_id, message_id = users[chat_id].profile_mess_id, caption = info, \
			parse_mode = 'Markdown', reply_markup = keyboard)
	elif call.data == 'edit_geo':
		users[chat_id].profile_edit_mode = 8
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		bot.send_message(chat_id, 'Укажи географию своих подписчиков', reply_markup = keyboard)
	elif call.data == 'edit_age':
		users[chat_id].profile_edit_mode = 9
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		bot.send_message(chat_id, 'Укажи средний возраст своих подписчиков', reply_markup = keyboard)
	elif call.data == 'edit_gender':
		users[chat_id].profile_edit_mode = 10
		bot.send_message(chat_id, 'Сколько процентов твоей аудитории женская?')
	elif call.data == 'edit_followers_num':
		users[chat_id].profile_edit_mode = 11
		bot.send_message(chat_id, 'Какое у тебя количество подписчиков на данный момент?')
	elif call.data == 'back_to_profile':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Редактировать профиль', callback_data = 'edit_profile')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Удалить профиль', callback_data = 'delete_profile')
		keyboard.add(button)
		bot.edit_message_caption(chat_id = chat_id, message_id = users[chat_id].profile_mess_id, \
		caption = info, reply_markup = keyboard) 
	elif call.data == 'edit_order':
		order = users[chat_id].orders_list[users[chat_id].cur_order]
		info = order_info(Order(order))
		info += '\n\n*Выбери то, что ты хочешь изменить*'
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('Название', callback_data = 'edit_order_name')
		button2 = types.InlineKeyboardButton('Логин', callback_data = 'edit_order_login')
		button3 = types.InlineKeyboardButton('Описание', callback_data = 'edit_descr')
		button4 = types.InlineKeyboardButton('Продвижение', callback_data = 'edit_post_or_story')
		button5 = types.InlineKeyboardButton('Охват', callback_data = 'edit_order_coverage')
		button6 = types.InlineKeyboardButton('Бюджет', callback_data = 'edit_budget')
		button7 = types.InlineKeyboardButton('Доп.комментарий', callback_data = 'edit_comments')
		button8 = types.InlineKeyboardButton('Целевая аудитория', callback_data = 'edit_target')
		button9 = types.InlineKeyboardButton('Назад', callback_data = 'back_to_order')
		keyboard.row(button1, button2, button3)
		keyboard.row(button4, button5, button6)
		keyboard.row(button7, button8)
		keyboard.row(button9)
		bot.edit_message_text(chat_id = chat_id, message_id = users[chat_id].order_mess_id, text = info,\
			parse_mode = 'Markdown', reply_markup = keyboard)
	elif call.data == 'edit_order_name':
		users[chat_id].order_edit_mode = 1
		bot.send_message(chat_id, 'Напиши мне новое название бренда')
	elif call.data == 'edit_order_login':
		users[chat_id].order_edit_mode = 2
		bot.send_message(chat_id, 'Напиши мне новый логин в Instagram')
	elif call.data == 'edit_descr':
		users[chat_id].order_edit_mode = 3
		bot.send_message(chat_id, 'Отправь новое описание к продукту')
	elif call.data == 'edit_post_or_story':
		users[chat_id].order_edit_mode = 4
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Публикация', 'История')
		keyboard.row('Оба варианта')
		bot.send_message(chat_id, 'Укажи какой метод продвижения тебя интересует', reply_markup = keyboard)
	elif call.data == 'edit_order_coverage':
		users[chat_id].order_edit_mode = 5
		bot.send_message(chat_id, 'Какой у тебя необходимый охват для продвижения?')
	elif call.data == 'edit_budget':
		users[chat_id].order_edit_mode = 6
		bot.send_message(chat_id, 'Какой у тебя новый бюджет?')
	elif call.data == 'edit_comments':
		users[chat_id].order_edit_mode = 7
		bot.send_message(chat_id, 'Отправь мне свои дополнительные комментарии к заказу')
	elif call.data == 'edit_target':
		order = users[chat_id].orders_list[users[chat_id].cur_order]
		info = order_info(Order(order))
		info += '\n\n*Какие данные о целевой аудитории ты хочешь изменить?*'
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('География', callback_data = 'edit_order_geo')
		button2 = types.InlineKeyboardButton('Ср.возраст', callback_data = 'edit_order_age')
		button3 = types.InlineKeyboardButton('Интересы', callback_data = 'edit_order_sub')
		button4 = types.InlineKeyboardButton('Пол', callback_data = 'edit_order_gender')
		button5 = types.InlineKeyboardButton('Назад', callback_data = 'edit_order')
		keyboard.row(button1, button2)
		keyboard.row(button3, button4)
		keyboard.row(button5)
		bot.edit_message_text(chat_id = chat_id, message_id = users[chat_id].order_mess_id, text = info,\
			parse_mode = 'Markdown', reply_markup = keyboard)
	elif call.data == 'edit_order_geo':
		users[chat_id].order_edit_mode = 8
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		bot.send_message(chat_id, 'Укажи географию своей целевой аудитории', reply_markup = keyboard)
	elif call.data == 'edit_order_age':
		users[chat_id].order_edit_mode = 9
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		bot.send_message(chat_id, 'Укажи средний возраст своей целевой аудитории', reply_markup = keyboard)
	elif call.data == 'edit_order_sub':
		users[chat_id].order_edit_mode = 10
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		bot.send_message(chat_id, 'Укажи интересы своей целевой аудитории', reply_markup = keyboard)
	elif call.data == 'edit_order_gender':
		users[chat_id].order_edit_mode = 11
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Мужчины', 'Женщины')
		keyboard.row('Все')
		bot.send_message(chat_id, 'Укажи пол своей целевой аудитории', reply_markup=keyboard)		

bot.polling(none_stop=True)