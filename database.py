import psycopg2
import telebot
import os
from profiles import Blogger, categories, cities

class Database:
	def __init__(self):
		#local host------------------
		# self.con = psycopg2.connect(
		#   database = "bloggerskz",
		#   user ="postgres", 
		#   password="sbazgugu", 
		#   host="localhost", 
		#   port="5432"
		# )
		# #----------------------------

		#heroku----------------------
		DATABASE_URL = os.environ['DATABASE_URL']
		self.con = psycopg2.connect(DATABASE_URL, sslmode='require')
		#----------------------------

		self.cur = self.con.cursor()
	def create_tables(self):
		self.cur.execute('''
			CREATE TABLE bloggers (
				id SERIAL PRIMARY KEY,
				name TEXT,
				login TEXT,
				followers INT,
				avg_post_coverage INT,
				avg_story_coverage INT,
				followers_geo TEXT[],
				avg_age TEXT[],
				male_ratio INT,
				female_ratio INT,
				subjects TEXT[],
				post_price INT,
				story_price INT,
				chat_id TEXT
			);
			CREATE TABLE orders(
				id SERIAL PRIMARY KEY,
				name TEXT,
				login TEXT,
				descr TEXT,
				post_or_story TEXT,
				coverage INT,
				geo TEXT[],
				age TEXT[],
				gender TEXT,
				subject TEXT,
				budget INT,
				comment TEXT,
				chat_id TEXT
			);''')
		self.con.commit()
	def drop_tables(self):
		self.cur.execute('DROP TABLE bloggers')
		self.con.commit()
	def new_blogger(self, profile):
		self.cur.execute('''
		INSERT INTO bloggers(name, login, followers, avg_post_coverage, avg_story_coverage, followers_geo, avg_age, \
		male_ratio, female_ratio, subjects, post_price, story_price, chat_id)
		VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',\
		(profile.name, profile.login, profile.followers, profile.avg_post_coverage, profile.avg_story_coverage,\
		profile.followers_geo, profile.avg_age, profile.male_ratio, profile.female_ratio, profile.subjects,\
		profile.post_price, profile.story_price, profile.chat_id) )
		self.con.commit()
	def new_order(self, order):
		self.cur.execute('''
		INSERT INTO orders(name, login, descr, post_or_story, coverage, geo, age, gender, subject, 
		budget, comment, chat_id)
		VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',\
		(order.name, order.login, order.descr, order.post_or_story, order.coverage, order.geo, order.age, \
		order.gender, order.subject, order.budget, order.comment, order.chat_id) )
		self.con.commit()
	def get_profile_by_chat_id(self, chat_id):
		self.cur.execute('SELECT * FROM bloggers WHERE chat_id = %s', (str(chat_id), ))
		profile = self.cur.fetchone()
		return profile
	def get_profile_by_id(self, blogger_id):
		self.cur.execute('SELECT * FROM bloggers WHERE id = %s', (str(blogger_id), ))
		profile = self.cur.fetchone()
		return profile

	def check_blogger(self, chat_id):
		self.cur.execute('SELECT * FROM bloggers WHERE chat_id = %s', (str(chat_id), ))
		if self.cur.rowcount > 0:
			return True
		else:
			return False
	def check_order(self, chat_id):
		self.cur.execute('SELECT * FROM orders WHERE chat_id = %s', (str(chat_id), ))
		if self.cur.rowcount > 0:
			return True
		else:
			return False
	def delete_profile(self, chat_id):
		self.cur.execute('DELETE FROM bloggers WHERE chat_id = %s', (str(chat_id), ))
		self.con.commit()
	def search_bloggers(self, filters = None):
		if filters is None:
			self.cur.execute('SELECT id FROM bloggers')
			tmp = self.cur.fetchall()
			profiles = []
			for a in tmp:
				profiles.append(a[0])
			return profiles
		tmp = filters.copy()
		if len(tmp[0]) == 0:
			tmp[0] = categories
		if len(tmp[1]) == 0:
			tmp[1] = cities
		if len(tmp[2]) == 0:
			tmp[2] = ['13-17', '18-24', '25-34', '35-44', '45-54']
		if len(tmp[3]) == 0:
			self.cur.execute('''
				SELECT * FROM bloggers
				WHERE 
					subjects && %s AND
					followers_geo && %s AND
					avg_age && %s
				''', (tmp[0], tmp[1], tmp[2]))
		elif tmp[3][0] == 'мужчины':
			self.cur.execute('''
				SELECT * FROM bloggers
				WHERE 
					subjects && %s AND
					followers_geo && %s AND
					avg_age && %s AND
					male_ratio >= female_ratio
				''', (tmp[0], tmp[1], tmp[2]))
		elif tmp[3][0] == 'женщины':
			self.cur.execute('''
				SELECT * FROM bloggers
				WHERE 
					subjects && %s AND
					followers_geo && %s AND
					avg_age && %s AND
					female_ratio >= male_ratio
				''', (tmp[0], tmp[1], tmp[2]))
		tmp = self.cur.fetchall()
		profiles = []
		for a in tmp:
			profiles.append(a[0])
		return profiles

	def get_orders_by_chat_id(self, chat_id):
		self.cur.execute('SELECT * FROM orders WHERE chat_id = %s', (str(chat_id), ))
		if self.cur.rowcount < 1:
			return None
		return self.cur.fetchall()
	def delete_order(self, order_id):
		self.cur.execute('DELETE FROM orders WHERE id = %s', (order_id,) )
		self.con.commit()
	def get_match_bloggers(self, order):
		self.cur.execute('SELECT * FROM bloggers')
		bloggers = self.cur.fetchall()
		n = self.cur.rowcount
		if n == 0:
			return None
		# avg_post_coverage = profile[4]
		# avg_story_coverage = profile[5]
		# followers_geo = profile[6]
		# avg_age = profile[7]
		# male_ratio = profile[8]
		# female_ratio = profile[9]
		# subjects = profile[10]
		# post_price = profile[11]
		# story_price = profile[12]
		cf = {}
		for i in range(n):
			num = 0
			# все тематики, весь Казахстан добавить -
			for j in order.geo:
				for k in bloggers[i][6]:
					if j == k:
						num += 1
			for j in bloggers[i][10]:
				if j == order.subject:
					num += 1
			for j in order.age:
				for k in bloggers[i][7]:
					if j == k:
						num += 1
			if order.gender == 'Мужчины' and bloggers[i][8] >= bloggers[i][9]:
				num += 1
			elif order.gender == 'Женщины' and bloggers[i][8] <= bloggers[i][9]:
				num += 1
			cf[i] = num
		for i in range(n):
			for j in range(0, n-i-1):
				if cf[j] < cf[j+1]:
					cf[j], cf[j+1] = cf[j+1], cf[j]
					bloggers[j], bloggers[j+1] = bloggers[j+1], bloggers[j]
		return bloggers
	def get_match_orders(self, blogger):
		self.cur.execute('SELECT * FROM orders')
		orders = self.cur.fetchall()
		n = self.cur.rowcount
		if n == 0:
			return None
		# post_or_story = order[4]  
		# coverage = order[5]
		# geo = order[6]
		# age = order[7]
		# gender = order[8]
		# subject = order[9]
		# budget = order[10]
		cf = {}
		for i in range(n):
			num = 0
			for j in blogger.followers_geo:
				for k in orders[i][6]:
					if j == k:
						num += 1
			for j in blogger.subjects:
				if j == orders[i][9]:
					num += 1
			for j in blogger.avg_age:
				for k in orders[i][7]:
					if j == k:
						num += 1
			if orders[i][8] == 'Мужчины' and blogger.male_ratio >= blogger.female_ratio:
				num += 1
			elif orders[i][8] == 'Женщины' and blogger.male_ratio <= blogger.female_ratio:
				num += 1
			cf[i] = num
		for i in range(n):
			for j in range(0, n-i-1):
				if cf[j] < cf[j+1]:
					cf[j], cf[j+1] = cf[j+1], cf[j]
					orders[j], orders[j+1] = orders[j+1], orders[j]
		return orders