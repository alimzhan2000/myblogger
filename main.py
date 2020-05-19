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
	text = profile.name + '\n' + profile.login + '\n' + str(profile.followers) + ' followers\n'
	text += 'Average Post Coverage - ' + str(profile.avg_post_coverage)
	text += '\nAverage Story Coverage - ' + str(profile.avg_story_coverage)
	text += '\nFollower Geography - '
	for city in profile.followers_geo:
		if city == profile.followers_geo[-1]:
			text += city
		else:
			text += city + ', '
	text += '\nAverage Follower Age - '
	for age in profile.avg_age:
		if age == profile.avg_age[-1]:
			text += age + ' years old'
		else:
			text += age + ' years old, '
	text += '\nFollower Gender:\nMale - ' + str(profile.male_ratio) + '%\nFemale - ' + str(profile.female_ratio)
	text += '%\nAccount Subjects - '
	for sub in profile.subjects:
		if sub == profile.subjects[-1]:
			text += sub
		else:
			text += sub + ', '
	text += '\nPost price - ' + str(profile.post_price) + ' CAD'
	text += '\nStory Price - ' + str(profile.story_price) + ' CAD'
	return text  
def order_info(order):
	text = 'Brand name - ' + order.name + '\n'
	text += 'Instagram account - ' + order.login + '\n'
	text += 'Product Advertised - ' + order.descr + '\n'
	text += 'Promotion option - '
	if order.post_or_story == 'Both':
		text += 'Post and Story'
	else:
		text += order.post_or_story
	text += '\nNecessary Audience Reach - ' + str(order.coverage)
	text += '\nThe target audience:'
	text += '\n Follower Geography - '
	for city in order.geo:
		if city == order.geo[-1]:
			text += city
		else:
			text += city + ', '
	text += '\n Average age - '
	for age in order.age:
		if age == order.age[-1]:
			text += age + ' years old'
		else:
			text += age + ' years old, '
	text += '\n Gender - ' + order.gender
	text += '\nProduct subjects - ' + order.subject
	text += '\nBudget - ' + str(order.budget) + ' CAD'
	if order.comment is not None:
		text += '\nAdditional Comments:\n' + order.comment
	return text
def main_menu(chat_id):
	global users
	default_vars(chat_id)
	keyboard = types.ReplyKeyboardMarkup(True, False)
	blogger = db.check_blogger(chat_id)
	order = db.check_order(chat_id)
	if users[chat_id].blogger is not None:
		if users[chat_id].blogger is False:
			keyboard.row('Find my blogger', 'Create an order')
			keyboard.row('My orders', 'Feedback')
		elif blogger is True:
			keyboard.row('My profile', 'Find an order')
			keyboard.row('Create a profile', 'Feedback')
		else:
			keyboard.row('I am a blogger', 'I am an advertiser')
			bot.send_message(chat_id, 'Who are you?', reply_markup=keyboard)
			return
		bot.send_message(chat_id, 'Main menu', reply_markup = keyboard)
		return
	if blogger is False and order is False:
		users[chat_id].blogger = None
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('I am a blogger', 'I am an advertiser')
		bot.send_message(chat_id, 'Who are you?', reply_markup=keyboard)
		return
	users[chat_id].blogger = blogger
	if blogger is True:
		keyboard.row('My profile', 'Find an order')
		keyboard.row('Create a profile', 'Feedback')
	else:
		keyboard.row('Find my blogger', 'Create an order')
		keyboard.row('My orders', 'Feedback')
	bot.send_message(chat_id, 'Main menu', reply_markup = keyboard)	
def refresh_search(message):
	global users
	chat_id = message.chat.id
	if len(users[chat_id].search_list) == 0:
		text = 'Unfortunately, we did not find a blogger with your specified parameters'
		text += '\n\nFilters: '
		for i in range(4):
			n = len(users[chat_id].filters[i])
			if n > 0:
				if i == 0:
					text += '\nby interests - '
				if i == 1:
					text += '\nby region - '
				if i == 2:
					text += '\nby age - '
				if i == 3:
					text += '\nby gender - '
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
	text += '\n\nFilters:'
	for i in range(4):
		n = len(users[chat_id].filters[i])
		if n > 0:
			if i == 0:
				text += '\nby interests - '
			if i == 1:
				text += '\nby region - '
			if i == 2:
				text += '\nby age - '
			if i == 3:
				text += '\nby gender - '
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
	info += '\n\n*Choose what you would like to change*'
	keyboard = types.InlineKeyboardMarkup()
	button1 = types.InlineKeyboardButton('Order name', callback_data = 'edit_order_name')
	button2 = types.InlineKeyboardButton('Login', callback_data = 'edit_order_login')
	button3 = types.InlineKeyboardButton('Description', callback_data = 'edit_descr')
	button4 = types.InlineKeyboardButton('Promotion', callback_data = 'edit_post_or_story')
	button5 = types.InlineKeyboardButton('Coverage', callback_data = 'edit_order_coverage')
	button6 = types.InlineKeyboardButton('Budget', callback_data = 'edit_budget')
	button7 = types.InlineKeyboardButton('Additional comment', callback_data = 'edit_comments')
	button8 = types.InlineKeyboardButton('Target audience', callback_data = 'edit_target')
	button9 = types.InlineKeyboardButton('Go back', callback_data = 'back_to_order')
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
	keyboard.row('I am a blogger', 'I am an advertiser')
	bot.send_message(message.chat.id, 'Hi! I am the bot, which connects advertisers with their perfect match bloggers. To begin our work, tell me who you are: a blogger or an advertiser?', reply_markup=keyboard)
	bot.send_sticker(chat_id, 'CAACAgIAAxkBAALZIF7D6Ujs9ALtrGIL53htddX9pN1IAAKSCAACCLcZAt2558s4lgJ9GQQ')

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
			bot.send_message(chat_id, 'Thank you! Now I need to know the coverage of your stories\
			\n(P.S Go to "statistics", choose "stories", then "coverage" for the last 14 days)')
		elif users[chat_id].mode == 7:
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			n = len(cities)
			for i in range(1, n, 2):
				keyboard.row(cities[i-1], cities[i])
			if n % 2 != 0:
				keyboard.row(cities[n-1])
			bot.send_message(chat_id, "Okay! Now let's find out what regions your followers from", reply_markup = keyboard)
		elif users[chat_id].mode == 9:
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('13-17', '18-24', '25-34')
			keyboard.row('35-44', '45-54')
			bot.send_message(chat_id, 'Got it! What is your average follower age', reply_markup = keyboard)
		elif users[chat_id].mode == 11:
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			bot.send_message(chat_id, 'Cool! Now I need to divide your followers by gender as a percentage\
			How many percent of your followers is female')
		elif users[chat_id].mode == 14:
			users[chat_id].profile.proof_photo_id.append(photos.document_handler(message, bot))
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			n = len(categories)
			for i in range(1, n, 2):
				keyboard.row(categories[i-1], categories[i])
			if n % 2 != 0:
				keyboard.row(categories[n-1])
			bot.send_message(chat_id, 'Great! Only 3 steps are left to create your profile!\
			Choose the subject (interests) of your account\n(P.S. You may choose several)', reply_markup = keyboard)
		elif users[chat_id].mode == 18:
			users[chat_id].profile.profile_photo_id = photos.document_handler(message, bot)
			users[chat_id].profile.telegram_username = '@' + str(message.from_user.username)
			users[chat_id].mode = 0
			db.new_blogger(users[chat_id].profile)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('My profile', 'Find an order')
			keyboard.row('Create a profile', 'Feedback')
			bot.send_message(chat_id, 'Hooray! We did it! I’m already looking forward to how advertisers will write to you and place their ads :)) I hope you and I are friends now. If you liked me, please introduce me to your friends-bloggers. I love communicating with creative people!', reply_markup = keyboard)
			bot.send_sticker(chat_id, 'CAACAgIAAxkBAALZHl7D6QtW1Pb9p4mky7Sc9Nxda-NwAAKyCAACCLcZAhMvzLXnfVShGQQ')
	if users[chat_id].profile_edit_mode > 0:
		mode = users[chat_id].profile_edit_mode
		if mode == 3:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 0)
			refresh_profile(message)
			bot.send_message(chat_id, 'You successfully changed average post coverage')
			users[chat_id].profile_edit_mode = 0
		elif mode == 4:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 1)
			refresh_profile(message)
			bot.send_message(chat_id, 'You successfully changed average stories coverage')
			users[chat_id].profile_edit_mode = 0
		elif mode == 8:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 2)
			refresh_profile(message)
			bot.send_message(chat_id, 'You successfully changed follower geography')
			users[chat_id].profile_edit_mode = 0
		elif mode == 9:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 3)
			refresh_profile(message)
			bot.send_message(chat_id, 'You successfully changed follower average age')
			users[chat_id].profile_edit_mode = 0
		elif mode == 10:
			photo_id = photos.document_handler(message, bot)
			db.profile_edit_proof(chat_id, photo_id, 4)
			refresh_profile(message)
			bot.send_message(chat_id, 'You successfully changed gender distribution')
			users[chat_id].profile_edit_mode = 0

@bot.message_handler(func=lambda message:message.text == 'Back to menu')
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
		bot.send_message(chat_id, 'Can you please type the name of your Instagram account?\n(example: @bloggerscanada)', reply_markup=keyboard)
		users[chat_id].mode += 1
	elif users[chat_id].mode == 2:
		users[chat_id].profile.login = message.text
		bot.send_message(chat_id, 'Got it! How many followers do you have?\n(example: 23500)')
		users[chat_id].mode += 1
	elif users[chat_id].mode == 3:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Please, type only numbers without symbols or letters')
			return
		users[chat_id].profile.followers = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Wow, that is impressive! What is your post coverage?\
		\n(P.S. Go to "statistics", choose "publications", then "coverage" for the last 30 days')		
	elif users[chat_id].mode == 4:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Please, type only numbers without symbols or letters')
			return
		users[chat_id].profile.avg_post_coverage = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Okay, now in order me to believe this number, I need to double-check. Can you please upload a screenshot of the page with post coverage?')
	elif users[chat_id].mode == 6:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Please, type only numbers without symbols or letters')
			return
		users[chat_id].profile.avg_story_coverage = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'One more screenshot to prove please. I am very sorry, but our boss is very strict🙁')
	elif users[chat_id].mode == 8:
		if message.text == 'Next step':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Back to menu')
			bot.send_message(chat_id, 'I am probably annoying with this, but I need one more screenshot of the page to prove\
			Go to "statistics", choose "audience", then "region and cities"', reply_markup = keyboard)
			return
		users[chat_id].profile.followers_geo.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		keyboard.row('Next step')
		if len(users[chat_id].profile.followers_geo) <= 1: 
			bot.send_message(chat_id, 'You can choose several options. After choosing all of them, press "Next step" button to go further', reply_markup = keyboard)
	elif users[chat_id].mode == 10:
		if message.text == 'Next step':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Back to menu')
			bot.send_message(chat_id, 'Okay, our boss requires even this to be proven. Can you please send me a screenshot-provement. There are few steps left!\
			(P.S. Go to "statistics", choose "audience", then "age distribution" of all followers)', reply_markup=keyboard)
			return
		users[chat_id].profile.avg_age.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		keyboard.row('Next step')
		if len(users[chat_id].profile.avg_age) <= 1: 
			bot.send_message(chat_id, 'You can choose several options. After choosing all of them, press "Next step" button to go further', reply_markup = keyboard)
	elif users[chat_id].mode == 12:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Please, type only numbers without symbols or letters')
			return
		users[chat_id].profile.female_ratio = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'How many percent of your followers is male?')
	elif users[chat_id].mode == 13:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Please, type only numbers without symbols or letters')
			return
		users[chat_id].profile.male_ratio = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Okay, the last screenshot I am going to ask! Go to "statistics", choose "audience" and "gender"')
	elif users[chat_id].mode == 15:
		if message.text == 'Next step':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Back to menu')
			bot.send_message(chat_id, 'The main thing! How much do you want to earn on a post ad?\
			Type only numbers (in CAD)', reply_markup = keyboard)
			return
		users[chat_id].profile.subjects.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		keyboard.row('Next step')
		if len(users[chat_id].profile.subjects) <= 1: 
			bot.send_message(chat_id, 'You can choose several options. After choosing all of them, press "Next step" button"', reply_markup = keyboard)
	elif users[chat_id].mode == 16:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Please, type only numbers without symbols or letters')
			return
		users[chat_id].profile.post_price = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Not bad. But If there will be very few orders for a long time, you can change that price at any time. Go to /menu and choose "My profile"')
		bot.send_message(chat_id, 'How much do you want to earn on a stories ad?')
	elif users[chat_id].mode == 17:
		if message.text.isdigit() == False:
			bot.send_message(chat_id, 'Please, type only numbers without symbols or letters')
			return
		users[chat_id].profile.story_price = int(message.text)
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'The last step! Can you please upload your Instagram profile photo?')

@bot.message_handler(func=lambda message:message.chat.id in users.keys() and users[message.chat.id].mode > 0 and users[message.chat.id].blogger == False)
def create_order(message):
	global users
	chat_id = message.chat.id
	if users[chat_id].mode == 1:
		users[chat_id].order.name = message.text
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Great! Now I need to know your brand name in Instagram\n(example: @mybloggercanada)')
	elif users[chat_id].mode == 2:
		users[chat_id].order.login = message.text
		users[chat_id].mode += 1
		bot.send_message(chat_id, 'Got it! What we are going to promote?\n(example: natural cosmetics)')		 
	elif users[chat_id].mode == 3:
		users[chat_id].order.descr = message.text
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Post', 'Stories')
		keyboard.row('Both')
		bot.send_message(chat_id, 'What a product! If I were alive, I would definetely buy it! Now, choose your promotion you are interested in', reply_markup=keyboard)
	elif users[chat_id].mode == 4:
		if message.text != 'Post' and message.text != 'Stories' and message.text != 'Both':
			bot.send_message(chat_id, 'Sorry, I understand only text that you choose from the buttons below:\n1.Post\n2.Stories\n3.Both')
			return
		users[chat_id].order.post_or_story = message.text
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.add('Back to menu')
		bot.send_message(chat_id, 'What is your promotion coverage?\n(example: 25000)', reply_markup = keyboard)
	elif users[chat_id].mode == 5:
		if message.text.isdigit() is False:
			bot.send_message(chat_id, 'Please, type only numbers without symbols and letters')
			return
		users[chat_id].order.coverage = int(message.text)
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		bot.send_message(chat_id, 'Big plans! What is your audience geography?', reply_markup = keyboard)
	elif users[chat_id].mode == 6:
		if message.text == 'Next step':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('13-17', '18-24', '25-34')
			keyboard.row('35-44', '45-54')
			bot.send_message(chat_id, 'Okay, what is your audience average age?', reply_markup = keyboard)
			return
		users[chat_id].order.geo.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		keyboard.row('Next step')
		if len(users[chat_id].order.geo) <= 1: 
			bot.send_message(chat_id, 'You can choose several options. When you finish, press "Next step" in order to go further', reply_markup = keyboard)
	elif users[chat_id].mode == 7:
		if message.text == 'Next step':
			users[chat_id].mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Male', 'Female')
			keyboard.row('Both')
			bot.send_message(chat_id, 'Now I need to know your audience gender', reply_markup=keyboard)
			return
		users[chat_id].order.age.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		keyboard.row('Next')
		if len(users[chat_id].order.age) <= 1: 
			bot.send_message(chat_id, 'You may choose several options. When you finish, press "Next step" in order to go further', reply_markup = keyboard)
	elif users[chat_id].mode == 8:
		if message.text != 'Male' and message.text != 'Female' and message.text != 'Both':
			bot.send_message(chat_id, 'Please, use the buttons below:\n1.Male\n2.Female\n3.Both')
			return
		users[chat_id].order.gender = message.text
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		bot.send_message(chat_id, 'There are only 2 steps to find you the perfect match blogger!')
		bot.send_message(chat_id, 'Please, choose the interests of your target audience', reply_markup = keyboard)
	elif users[chat_id].mode == 9:
		users[chat_id].order.subject = message.text
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.add('Back to menu')
		bot.send_message(chat_id, 'The last step! What is your promotion budget?\n(example: 65000)', reply_markup = keyboard)
	elif users[chat_id].mode == 10:
		if message.text.isdigit() is False:
			bot.send_message(chat_id, 'Please, provide only numbers without symbols and letters')
			return
		users[chat_id].order.budget = int(message.text)
		users[chat_id].mode += 1
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Skip')
		bot.send_message(chat_id, 'Okay, we are finished! Any additional comments? (Here you can describe the methods or work plan for the blogger to have better understanding)', reply_markup = keyboard)
	elif users[chat_id].mode == 11:
		if message.text == 'Skip':
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
		keyboard.row('Find my blogger', 'Create an order')
		keyboard.row('My orders', 'Feedback')
		bot.send_message(chat_id, 'Hooray! We successfuly created your profile. If you want to edit some info further, you can easily go to the /menu and choose "My orders". I hope you and I are friends now. If so, can you please introduce me to your friends. I adore communicating with people from business!', reply_markup = keyboard)
		bot.send_sticker(chat_id, 'CAACAgIAAxkBAALZHl7D6QtW1Pb9p4mky7Sc9Nxda-NwAAKyCAACCLcZAhMvzLXnfVShGQQ')

@bot.message_handler(func=lambda message:message.chat.id in users.keys() and users[message.chat.id].profile_edit_mode > 0)
def edit_profile(message):
	global users
	chat_id = message.chat.id
	mode = users[chat_id].profile_edit_mode
	if mode == 1:
		db.profile_edit_name(chat_id, message.text)
		refresh_profile(message)
		bot.send_message(chat_id, 'You successfully changed your name')
		users[chat_id].profile_edit_mode = 0
	elif mode == 2:
		db.profile_edit_login(chat_id, message.text)
		refresh_profile(message)
		bot.send_message(chat_id, 'You successfully changed your login')
		users[chat_id].profile_edit_mode = 0
	elif mode == 3:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Please, provide only numbers without symbols and letters')
			return
		db.profile_edit_post_cvg(chat_id, int(message.text))
		bot.send_message(chat_id, 'Can you please provide screenshot to prove this. I will be very thankful😘\n(P.S. Go to "statistics", choose "posts", then "coverage" for the last 30 days')
	elif mode == 4:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Please, provide only numbers without symbols and letters')
			return
		db.profile_edit_story_cvg(chat_id, int(message.text))
		bot.send_message(chat_id, 'We also need provement for this one. Can you please send me a screenshot of your coverage?\n(P.S. Go to "statistics", choose "stories", then "coverage" for 14 days)')
	elif mode == 5:
		if message.text == 'Edit':
			db.profile_edit_subjects(chat_id, users[chat_id].tmp)
			users[chat_id].tmp = []
			refresh_profile(message)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('My profile', 'Find an order')
			keyboard.row('Create a profile', 'Feedback')
			bot.send_message(chat_id, 'Success', reply_markup = keyboard)
			users[chat_id].profile_edit_mode = 0
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		keyboard.row('Edit')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'You may choose several options and when you are done, press "Edit"', reply_markup = keyboard)
	elif mode == 6:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Please, provide only numbers without letters and symbols')
			return
		db.profile_edit_post_price(chat_id, int(message.text))
		users[chat_id].profile_edit_mode = 7
		bot.send_message(chat_id, 'Okay, now I need to know your new price for one story')
	elif mode == 7:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Please, provide only numbers without letters and symbols')
			return
		db.profile_edit_story_price(chat_id, int(message.text))
		refresh_profile(message)
		users[chat_id].profile_edit_mode = 0
		bot.send_message(chat_id, 'Success ;)')
	elif mode == 8:
		if message.text == 'Edit':
			db.profile_edit_geo(chat_id, users[chat_id].tmp)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('My profile', 'Find an order')
			keyboard.row('Create a profile', 'Feedback')
			bot.send_message(chat_id, 'Wonderful! Now I need one more provement for this one (P.S. all charges not to me, but to my boss😅)\n(P.S.S. Go to "statistics", choose "audience", then "locations" by regions and cities)', reply_markup = keyboard)
			users[chat_id].tmp = []
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(cities)
		for i in range(1, n, 2):
			keyboard.row(cities[i-1], cities[i])
		if n % 2 != 0:
			keyboard.row(cities[n-1])
		keyboard.row('Edit')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'You may choose several options, when you are done, press "Edit" to finish', reply_markup = keyboard)
	elif mode == 9:
		if message.text == 'Edit':
			db.profile_edit_age(chat_id, users[chat_id].tmp)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('My profile', 'Find an order')
			keyboard.row('Create a profile', 'Feedback')
			bot.send_message(chat_id, 'Heey! Can you please send my screenshot for this? (P.S. Go to "statistics", choose "audience", then "average follower age"', reply_markup = keyboard)
			users[chat_id].tmp = []
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		keyboard.row('Edit')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'You may choose several options, when you are done, press "Edit" to finish', reply_markup = keyboard)		
	elif mode == 10:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Please provide only numbers without symbols and letters')
			return
		if int(message.text) < 0 or int(message.text) > 100:
			bot.send_message(chat_id, 'Type any number from 0 to 100')
			return
		db.profile_edit_gender(chat_id, int(message.text))
		bot.send_message(chat_id, 'Now I need to double check it (P.S. Go to "statistics", choose "audience", then "gender"')
	elif mode == 11:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Please provide only numbers without symbols and letters')
			return
		db.profile_edit_followers(chat_id, int(message.text))
		users[chat_id].profile_edit_mode = 0
		refresh_profile(message)
		bot.send_message(chat_id, 'The number of your followers has successfully changed!')

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
		bot.send_message(chat_id, 'The name of your brand has successfully changed!')
	elif mode == 2:
		db.order_edit_login(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'The login of your brand has successfully changed!')
	elif mode == 3:
		db.order_edit_descr(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'The description of your product has successfully changed!')
	elif mode == 4:
		db.order_edit_post_or_story(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'The promotion type has successfully changed')
	elif mode == 5:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Please, provide only numbers without symbols and letters')
			return
		db.order_edit_coverage(order_id, int(message.text))
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Your promotions coverage has successfully changed')
	elif mode == 6:
		if message.text.isdigit() is not True:
			bot.send_message(chat_id, 'Please, provide only numbers without symbols and letters')
			return
		db.order_edit_budget(order_id, int(message.text))
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Your budget has successfuly changed')
	elif mode == 7:
		db.order_edit_comment(order_id, message.text)
		users[chat_id].order_edit_mode = 0
		refresh_order(message)
		bot.send_message(chat_id, 'Your comments has successfuly changed')
	elif mode == 8:
		if message.text == 'Edit':
			db.order_edit_geo(order_id, users[chat_id].tmp)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Find my blogger', 'Create an order')
			keyboard.row('My orders', 'Feedback')
			bot.send_message(chat_id, 'Your audience geography has successfully changed', reply_markup = keyboard)
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
		keyboard.row('Edit')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'You may choose several oprtions, when you are done press "Edit" to finish', reply_markup = keyboard)
	elif mode == 9:
		if message.text == 'Edit':
			db.order_edit_age(order_id, users[chat_id].tmp)
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Find my blogger', 'Create an order')
			keyboard.row('My orders', 'Feedback')
			bot.send_message(chat_id, 'Your average audience age has successfully changed', reply_markup = keyboard)
			users[chat_id].tmp = []
			refresh_order(message)
			users[chat_id].order_edit_mode = 0
			return
		users[chat_id].tmp.append(message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		keyboard.row('Edit')
		if len(users[chat_id].tmp) <= 1: 
			bot.send_message(chat_id, 'You may choose several options, when you are done press "Edit" to finish', reply_markup = keyboard)
	elif mode == 10:
		db.order_edit_subject(order_id, message.text)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Find my blogger', 'Create an order')
		keyboard.row('My orders', 'Feedback')
		bot.send_message(chat_id, 'Your audience interests have successfully changed!', reply_markup = keyboard)
		refresh_order(message)
		users[chat_id].order_edit_mode = 0
	elif mode == 11:
		db.order_edit_gender(order_id, message.text)
		refresh_order(message)
		users[chat_id].order_edit_mode = 0
		bot.send_message(chat_id, 'Your audience gender has successfully changed!')

		
@bot.message_handler(content_types = ['text'])
def get_message(message):
	global users
	chat_id = message.chat.id
	if message.text == 'I am a blogger':
		users[chat_id].blogger = True
		if db.check_blogger(chat_id) is True:
			main_menu(chat_id)
			return
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Create a profile')
		bot.send_message(chat_id, 'Heey! My future star, in this section you can create your profile or see your current one. Also, you can find the order yourself. But first, you need to create your profile.', reply_markup = keyboard)
	elif message.text == 'Create a profile':
		if db.check_blogger(chat_id) is True:
			bot.send_message(chat_id, 'You have already created profile! If you want to create a new one or make some editions, go to /menu and "My profile"')
			return
		users[chat_id].mode = 1
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Back to menu')
		bot.send_message(chat_id, 'Great! Oh, I nearly forgot to introduce myself. My name is Hodor. What is yours?', reply_markup = keyboard)
	elif message.text == 'Find an order':
		blogger = Blogger(db.get_profile_by_chat_id(chat_id))
		match_orders = users[chat_id].match_orders = db.get_match_orders(blogger)
		cur_match_order = users[chat_id].cur_match_order = 0
		keyboard = types.InlineKeyboardMarkup()
		if len(match_orders) > 1:
			keyboard.add(types.InlineKeyboardButton('Next >>', callback_data = 'next_match_order'))
		keyboard.add(types.InlineKeyboardButton('Invite to cooperation', callback_data = 'invite_order'))
		order = Order(match_orders[cur_match_order])
		info = order_info(order)
		mess = bot.send_message(chat_id = chat_id, text = info, reply_markup = keyboard)
		users[chat_id].match_orders_id = mess.message_id
	elif message.text == 'My profile':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		photo = photos.download_photo(profile.profile_photo_id)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Edit profile', callback_data = 'edit_profile')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Delete', callback_data = 'delete_profile')
		keyboard.add(button)
		users[chat_id].last_keyboard = keyboard
		mess = bot.send_photo(chat_id, photo, info, reply_markup = keyboard)
		users[chat_id].profile_mess_id = mess.message_id
	elif message.text == 'I am an advertiser':
		users[chat_id].blogger = False
		if db.check_order(chat_id) is True:
			main_menu(chat_id)
			return
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Find my blogger', 'Create an order')
		keyboard.row('My orders', 'Feedback')
		bot.send_message(chat_id, 'Heey! Welcome to our program. You may find your blogger by creating a profile, you may create an order and find all your current orders',reply_markup=keyboard,parse_mode = 'Markdown')
	elif message.text == 'Find my blogger':
		users[chat_id].search_st = True
		users[chat_id].search_list = db.search_bloggers()
		users[chat_id].cur_blogger = 0
		keyboard = types.InlineKeyboardMarkup()
		if len(users[chat_id].search_list) == 0:
			bot.send_message(chat_id, 'Unfortunately, we do not have bloggers that may match your parameters :(')
			return
		if len(users[chat_id].search_list) > 1:
			button = types.InlineKeyboardButton('Next blogger >>', callback_data = 'next_blogger')
			keyboard.add(button)
		button = types.InlineKeyboardButton('Filter by..', callback_data = 'filters')
		keyboard.add(button)
		# button = types.InlineKeyboardButton('Сортировать по..', callback_data = 'sort')
		# keyboard.add(button)
		cur_blogger = users[chat_id].cur_blogger
		blogger_id = users[chat_id].search_list[cur_blogger]
		profile = db.get_profile_by_id(blogger_id)
		profile = Blogger(profile)
		text = profile_info(profile)
		text += '\n\nFilters:\n\n' + str(cur_blogger+1) + '/' + str(len(users[chat_id].search_list))
		photo = photos.download_photo(profile.profile_photo_id)
		mess = bot.send_photo(chat_id, photo, text, reply_markup = keyboard) 
		users[chat_id].search_mess_id = mess.message_id
	elif message.text == 'Create an order':
		orders_list = db.get_orders_by_chat_id(chat_id)
		if orders_list is not None:
			keyboard = types.InlineKeyboardMarkup()
			keyboard.row(types.InlineKeyboardButton('Yes', callback_data = 'create_order_true'),\
				types.InlineKeyboardButton('No', callback_data = 'create_order_false'))
			bot.send_message(chat_id, 'You have current orders: '\
				+ '*' + str(len(orders_list)) + '*\nDo you wish to create a new one?', reply_markup = keyboard,\
				parse_mode = 'Markdown')
			return
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.add('Back to menu')
		users[chat_id].mode = 1
		bot.send_message(chat_id, 'Great! Now I need to know the name of your brand', reply_markup = keyboard)
	elif message.text == 'My orders':
		users[chat_id].orders_list = db.get_orders_by_chat_id(chat_id)
		orders_list = users[chat_id].orders_list
		cur_order = users[chat_id].cur_order = 0
		if users[chat_id].orders_list is None:
			bot.send_message(chat_id, 'You do not have any active orders. To create one, press *"Create an order"*', parse_mode = 'Markdown')
			return
		keyboard = types.InlineKeyboardMarkup()
		if len(users[chat_id].orders_list) > 1:
			button1 = types.InlineKeyboardButton('Next >>', callback_data = 'next_order')
			keyboard.add(button1)
		button2 = types.InlineKeyboardButton('Match me with the perfect bloggers', callback_data = 'match_bloggers')
		button4 = types.InlineKeyboardButton('Edit order', callback_data = 'edit_order')
		button3 = types.InlineKeyboardButton('Delete order', callback_data = 'delete_order')
		keyboard.add(button2)
		keyboard.add(button4)
		keyboard.add(button3)
		info = order_info(Order(orders_list[cur_order]))
		mess = bot.send_message(chat_id, info, reply_markup = keyboard)
		users[chat_id].order_mess_id = mess.message_id
	elif message.text == 'Feedback' or users[chat_id].feedback_st == True:
		if users[chat_id].feedback_st == False:
			users[chat_id].feedback_st = True
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Back to menu')
			bot.send_message(chat_id, 'Please, leave us your feedback on our work. We will be very grateful to you!', reply_markup=keyboard)
		else:
			bot.send_message(365391038, str(message.text) + '\nот ' + str(message.from_user.last_name) + ' ' + str(message.from_user.first_name) + ' @' + str(message.from_user.username) )
			default_vars(chat_id)
			bot.send_message(chat_id, 'Thank you for your feedback!')
			main_menu(chat_id)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	global users
	chat_id = call.message.chat.id
	if call.data == 'delete_profile':
		db.delete_profile(chat_id)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Create a profile')
		bot.send_message(chat_id, 'Your profile has benn successfully deleted!', reply_markup=keyboard)
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
			button1 = types.InlineKeyboardButton('Next >>', callback_data = 'next_blogger')
			button2 = types.InlineKeyboardButton('<< Prev', callback_data = 'prev_blogger')
			keyboard.row(button2, button1)
		elif cur_blogger != len(search_list) - 1:
			keyboard.add(types.InlineKeyboardButton('Next blogger >>', callback_data = 'next_blogger'))
		elif cur_blogger > 0:
			keyboard.add(types.InlineKeyboardButton('<< Previous blogger', callback_data = 'prev_blogger'))			
		button = types.InlineKeyboardButton('Filter by..', callback_data = 'filters')
		keyboard.add(button)
		# button = types.InlineKeyboardButton('Сортировать по..', callback_data = 'sort')
		# keyboard.add(button)
		blogger_id = search_list[cur_blogger]
		profile = db.get_profile_by_id(blogger_id)
		profile = Blogger(profile)
		text = profile_info(profile)
		text += '\n\nFilters: '
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
		button1 = types.InlineKeyboardButton('interests', callback_data = 'filter_sub')
		button2 = types.InlineKeyboardButton('location', callback_data = 'filter_geo')
		button3 = types.InlineKeyboardButton('age', callback_data = 'filter_age')
		button4 = types.InlineKeyboardButton('gender', callback_data = 'filter_gender')
		button5 = types.InlineKeyboardButton('go back', callback_data = 'search_back_main')
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
			button1 = types.InlineKeyboardButton('Next >>', callback_data = 'next_blogger')
			button2 = types.InlineKeyboardButton('<< Prev', callback_data = 'prev_blogger')
			keyboard.row(button2, button1)
		elif cur_blogger != len(search_list) - 1:
			keyboard.add(types.InlineKeyboardButton('Next blogger >>', callback_data = 'next_blogger'))
		elif cur_blogger > 0:
			keyboard.add(types.InlineKeyboardButton('<< Previous blogger', callback_data = 'prev_blogger'))			
		button = types.InlineKeyboardButton('Filter by..', callback_data = 'filters')
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
			button6 = types.InlineKeyboardButton('Go back', callback_data = 'filters')
			keyboard.row(types.InlineKeyboardButton(categories[n-1], callback_data = 'filter_sub' + str(n-1)), button6)
		else:	
			button6 = types.InlineKeyboardButton('Go back', callback_data = 'filters')
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
			button6 = types.InlineKeyboardButton('Go back', callback_data = 'filters')
			keyboard.row(types.InlineKeyboardButton(cities[n-1], callback_data = 'filter_geo' + str(n-1)), button6)
		else:	
			button6 = types.InlineKeyboardButton('Go back', callback_data = 'filters')
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
		button6 = types.InlineKeyboardButton('go back', callback_data = 'filters')
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
		button1 = types.InlineKeyboardButton('male', callback_data = 'filter_gender_male')
		button2 = types.InlineKeyboardButton('female', callback_data = 'filter_gender_female')
		button3 = types.InlineKeyboardButton('go back', callback_data = 'filters')
		keyboard.row(button1, button2)
		keyboard.row(button3)
		users[chat_id].last_keyboard = keyboard
		bot.edit_message_reply_markup(chat_id = chat_id, message_id = users[chat_id].search_mess_id, reply_markup = keyboard)
	elif call.data[:13] == 'filter_gender':
		key = call.data[14:]
		if key == 'male':
			key = 'male'
		if key == 'female':
			key = 'female'
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
		button1 = types.InlineKeyboardButton('followers', callback_data = 'sort_followers')
		button2 = types.InlineKeyboardButton('go back', callback_data = 'search_back_main')
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
			button1 = types.InlineKeyboardButton('Next >>', callback_data = 'next_order')
			button2 = types.InlineKeyboardButton('<< Prev', callback_data = 'prev_order')
			keyboard.row(button2, button1)
		elif cur_order != len(orders_list) - 1:
			keyboard.add(types.InlineKeyboardButton('Next >>', callback_data = 'next_order'))
		elif cur_order > 0:
			keyboard.add(types.InlineKeyboardButton('<< Previous', callback_data = 'prev_order'))			
		button = types.InlineKeyboardButton('Match me with the perfect bloggers', callback_data = 'match_bloggers')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Edit order', callback_data = 'edit_order')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Change order', callback_data = 'delete_order')
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
			'Your order has been successfully deleted!')
		main_menu(chat_id)
	elif call.data == 'create_order_true':
		bot.delete_message(chat_id = chat_id, message_id = call.message.message_id)
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.add('Back to menu')
		users[chat_id].mode = 1
		bot.send_message(chat_id, 'What is the name of your brand?', reply_markup = keyboard)
	elif call.data == 'create_order_false':
		bot.delete_message(chat_id = chat_id, message_id = call.message.message_id)
		main_menu(chat_id)
	elif call.data == 'match_bloggers':
		order = Order(users[chat_id].orders_list[users[chat_id].cur_order])
		match_bloggers = users[chat_id].match_bloggers = db.get_match_bloggers(order)
		cur_match_blogger = users[chat_id].cur_match_blogger = 0
		keyboard = types.InlineKeyboardMarkup()
		if len(match_bloggers) > 1:
			keyboard.add(types.InlineKeyboardButton('Next blogger >>', callback_data = 'next_match_blogger'))
		keyboard.add(types.InlineKeyboardButton('Invite to cooperation', callback_data = 'invite_blogger'))
		keyboard.add(types.InlineKeyboardButton('Back to the order', callback_data = 'back_to_order'))
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
			button1 = types.InlineKeyboardButton('Next >>', callback_data = 'next_match_blogger')
			button2 = types.InlineKeyboardButton('<< Prev', callback_data = 'prev_match_blogger')
			keyboard.row(button2, button1)
		elif cur_match_blogger != len(match_bloggers) - 1:
			keyboard.add(types.InlineKeyboardButton('Next >>', callback_data = 'next_match_blogger'))
		elif cur_match_blogger > 0:
			keyboard.add(types.InlineKeyboardButton('<< Previous', callback_data = 'prev_match_blogger'))			
		keyboard.add(types.InlineKeyboardButton('Invite to cooperation', callback_data = 'invite_blogger'))
		keyboard.add(types.InlineKeyboardButton('Back to the order', callback_data = 'back_to_order'))
		blogger = Blogger(match_bloggers[cur_match_blogger])
		info = profile_info(blogger)
		photo = photos.download_photo(blogger.profile_photo_id)
		media = InputMediaPhoto(photo, caption = info)
		bot.edit_message_media(chat_id = chat_id, message_id = users[chat_id].order_mess_id\
			, media = media, reply_markup = keyboard)
	elif call.data == 'invite_blogger':
		blogger_chat_id = users[chat_id].match_bloggers[users[chat_id].cur_match_blogger][13]
		bot.send_message(blogger_chat_id, 'You have recieved an invitation to the cooperation. Full information about the advertiser and their order will be sent in the next message')
		info = order_info(Order(users[chat_id].orders_list[users[chat_id].cur_order]))
		bot.send_message(blogger_chat_id, info)
		bot.send_message(blogger_chat_id, 'If you are ready to cooperate, please contact the advertiser through the Telegram\nTelegram account of the advertiser: ' + \
			users[chat_id].orders_list[users[chat_id].cur_order][13])
		bot.send_message(chat_id, 'An invitation to cooperation was sent to the blogger. \
			Please, wait for the response!')
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
			button1 = types.InlineKeyboardButton('Next >>', callback_data = 'next_match_order')
			button2 = types.InlineKeyboardButton('<< Prev', callback_data = 'prev_match_order')
			keyboard.row(button2, button1)
		elif cur_match_order != len(match_orders) - 1:
			keyboard.add(types.InlineKeyboardButton('Next >>', callback_data = 'next_match_order'))
		elif cur_match_order > 0:
			keyboard.add(types.InlineKeyboardButton('<< Previous', callback_data = 'prev_match_order'))			
		button = types.InlineKeyboardButton('Invite to cooperation', callback_data = 'invite_order')
		keyboard.add(button)
		info = order_info(Order(match_orders[cur_match_order]))
		bot.edit_message_text(chat_id = chat_id, message_id = match_orders_id, text = info, reply_markup = keyboard)
	elif call.data == 'invite_order':
		order_chat_id = users[chat_id].match_orders[users[chat_id].cur_match_order][12]
		bot.send_message(order_chat_id, 'You have recieved an invitation to cooperation. Full info about the blogger will be sent in the next message')
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		bot.send_message(order_chat_id, info)
		bot.send_message(order_chat_id, 'If you are ready to work, please contact the blogger through the Telegram\nTelegram account of the blogger: ' + profile.telegram_username)
		bot.send_message(chat_id, 'An invitation to cooperation was sent to this advertiser.\
			Please, wait for the response!')
	elif call.data == 'edit_profile':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		info += '\n\n*Choose what you would like to change*'
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('Name', callback_data = 'edit_name')
		button2 = types.InlineKeyboardButton('Login', callback_data = 'edit_login')
		button3 = types.InlineKeyboardButton('Coverage', callback_data = 'edit_coverage')
		button4 = types.InlineKeyboardButton('Subject', callback_data = 'edit_subjects')
		button5 = types.InlineKeyboardButton('Price', callback_data = 'edit_price')
		button6 = types.InlineKeyboardButton('Info about orders', callback_data = 'edit_followers')
		button7 = types.InlineKeyboardButton('Go back', callback_data = 'back_to_profile')
		keyboard.row(button1, button2)
		keyboard.row(button3, button4)
		keyboard.row(button5)
		keyboard.row(button6)
		keyboard.row(button7)
		bot.edit_message_caption(chat_id = chat_id, message_id = users[chat_id].profile_mess_id, caption = info,\
			parse_mode = 'Markdown', reply_markup = keyboard)
	elif call.data == 'edit_name':
		users[chat_id].profile_edit_mode = 1
		bot.send_message(chat_id, 'Type your new name')
	elif call.data == 'edit_login':
		users[chat_id].profile_edit_mode = 2
		bot.send_message(chat_id, 'Type your new Instagram login')
	elif call.data == 'edit_coverage':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		info += '\n\n*What exactly you would like to edit?*'
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('Posts', callback_data = 'edit_post_coverage')
		button2 = types.InlineKeyboardButton('Stories', callback_data = 'edit_story_coverage')
		button3 = types.InlineKeyboardButton('Go back', callback_data = 'edit_profile')
		keyboard.row(button1, button2)
		keyboard.row(button3)
		bot.edit_message_caption(chat_id = chat_id, message_id = users[chat_id].profile_mess_id, caption = info, \
			parse_mode = 'Markdown', reply_markup = keyboard)
	elif call.data == 'edit_post_coverage':
		users[chat_id].profile_edit_mode = 3
		bot.send_message(chat_id, 'Type your new posts coverage')
	elif call.data == 'edit_story_coverage':
		users[chat_id].profile_edit_mode = 4
		bot.send_message(chat_id, 'Type your new stories coverage')
	elif call.data == 'edit_subjects':
		users[chat_id].profile_edit_mode = 5
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		bot.send_message(chat_id, 'Type a new subject/s(interests) of your audience', reply_markup = keyboard)
	elif call.data == 'edit_price':
		users[chat_id].profile_edit_mode = 6
		bot.send_message(chat_id, 'Type your new price for a post (in CAD)')
	elif call.data == 'edit_followers':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		info += '\n\n*What info about followers you would like to change?*'
		keyboard = types.InlineKeyboardMarkup()
		button5 = types.InlineKeyboardButton('Numbers', callback_data = 'edit_followers_num')
		button1 = types.InlineKeyboardButton('Location', callback_data = 'edit_geo')
		button2 = types.InlineKeyboardButton('Average age', callback_data = 'edit_age')
		button3 = types.InlineKeyboardButton('Gender', callback_data = 'edit_gender')
		button4 = types.InlineKeyboardButton('Go back', callback_data = 'edit_profile')
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
		bot.send_message(chat_id, 'Type your new follower geography', reply_markup = keyboard)
	elif call.data == 'edit_age':
		users[chat_id].profile_edit_mode = 9
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		bot.send_message(chat_id, 'Choose your new average follower age', reply_markup = keyboard)
	elif call.data == 'edit_gender':
		users[chat_id].profile_edit_mode = 10
		bot.send_message(chat_id, 'What is the percantage of your audience is female?')
	elif call.data == 'edit_followers_num':
		users[chat_id].profile_edit_mode = 11
		bot.send_message(chat_id, 'What is your current number of followers?')
	elif call.data == 'back_to_profile':
		profile = Blogger(db.get_profile_by_chat_id(chat_id))
		info = profile_info(profile)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Edit profile', callback_data = 'edit_profile')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Delete profile', callback_data = 'delete_profile')
		keyboard.add(button)
		bot.edit_message_caption(chat_id = chat_id, message_id = users[chat_id].profile_mess_id, \
		caption = info, reply_markup = keyboard) 
	elif call.data == 'edit_order':
		order = users[chat_id].orders_list[users[chat_id].cur_order]
		info = order_info(Order(order))
		info += '\n\n*Choose what you would like to change*'
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('Name', callback_data = 'edit_order_name')
		button2 = types.InlineKeyboardButton('Login', callback_data = 'edit_order_login')
		button3 = types.InlineKeyboardButton('Description', callback_data = 'edit_descr')
		button4 = types.InlineKeyboardButton('Promotion', callback_data = 'edit_post_or_story')
		button5 = types.InlineKeyboardButton('Coverage', callback_data = 'edit_order_coverage')
		button6 = types.InlineKeyboardButton('Budget', callback_data = 'edit_budget')
		button7 = types.InlineKeyboardButton('Comments', callback_data = 'edit_comments')
		button8 = types.InlineKeyboardButton('Target audience', callback_data = 'edit_target')
		button9 = types.InlineKeyboardButton('Go back', callback_data = 'back_to_order')
		keyboard.row(button1, button2, button3)
		keyboard.row(button4, button5, button6)
		keyboard.row(button7, button8)
		keyboard.row(button9)
		bot.edit_message_text(chat_id = chat_id, message_id = users[chat_id].order_mess_id, text = info,\
			parse_mode = 'Markdown', reply_markup = keyboard)
	elif call.data == 'edit_order_name':
		users[chat_id].order_edit_mode = 1
		bot.send_message(chat_id, 'Type your new name of the brand')
	elif call.data == 'edit_order_login':
		users[chat_id].order_edit_mode = 2
		bot.send_message(chat_id, 'Type your new Instagram login')
	elif call.data == 'edit_descr':
		users[chat_id].order_edit_mode = 3
		bot.send_message(chat_id, 'Type your new description of your product')
	elif call.data == 'edit_post_or_story':
		users[chat_id].order_edit_mode = 4
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Post', 'Stories')
		keyboard.row('Both')
		bot.send_message(chat_id, 'Choose the type of your promotion', reply_markup = keyboard)
	elif call.data == 'edit_order_coverage':
		users[chat_id].order_edit_mode = 5
		bot.send_message(chat_id, 'What is your desired promotion coverage?')
	elif call.data == 'edit_budget':
		users[chat_id].order_edit_mode = 6
		bot.send_message(chat_id, 'Type your new budget?')
	elif call.data == 'edit_comments':
		users[chat_id].order_edit_mode = 7
		bot.send_message(chat_id, 'Type your new comments to the order')
	elif call.data == 'edit_target':
		order = users[chat_id].orders_list[users[chat_id].cur_order]
		info = order_info(Order(order))
		info += '\n\n*What exactly you would like to change about your target audience?*'
		keyboard = types.InlineKeyboardMarkup()
		button1 = types.InlineKeyboardButton('Location', callback_data = 'edit_order_geo')
		button2 = types.InlineKeyboardButton('Avg age', callback_data = 'edit_order_age')
		button3 = types.InlineKeyboardButton('Interests', callback_data = 'edit_order_sub')
		button4 = types.InlineKeyboardButton('Gender', callback_data = 'edit_order_gender')
		button5 = types.InlineKeyboardButton('Go back', callback_data = 'edit_order')
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
		bot.send_message(chat_id, 'Choose your new location of the target audience', reply_markup = keyboard)
	elif call.data == 'edit_order_age':
		users[chat_id].order_edit_mode = 9
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('13-17', '18-24', '25-34')
		keyboard.row('35-44', '45-54')
		bot.send_message(chat_id, 'Choose the average follower age of your target audience', reply_markup = keyboard)
	elif call.data == 'edit_order_sub':
		users[chat_id].order_edit_mode = 10
		keyboard = types.ReplyKeyboardMarkup(True, False)
		n = len(categories)
		for i in range(1, n, 2):
			keyboard.row(categories[i-1], categories[i])
		if n % 2 != 0:
			keyboard.row(categories[n-1])
		bot.send_message(chat_id, 'Type your target audience new interests', reply_markup = keyboard)
	elif call.data == 'edit_order_gender':
		users[chat_id].order_edit_mode = 11
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Male', 'Female')
		keyboard.row('Both')
		bot.send_message(chat_id, 'Type your new gender of the target audience', reply_markup=keyboard)		

bot.polling(none_stop=True)