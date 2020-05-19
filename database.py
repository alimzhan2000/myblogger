import psycopg2
import telebot
import os
from profiles import Blogger, categories, cities

class Database:
	def __init__(self):
		#local host------------------
		self.con = psycopg2.connect(
		  database = "bloggersca",
		  user ="postgres", 
		  password="qW!1234567", 
		  host="localhost", 
		  port="5432"
		)
		# #----------------------------

		#heroku----------------------
		# DATABASE_URL = os.environ['DATABASE_URL']
		# self.con = psycopg2.connect(DATABASE_URL, sslmode='require')
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
				chat_id TEXT,
				proof_photo_id TEXT[],
				profile_photo_id TEXT,
				telegram_username TEXT
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
				chat_id TEXT,
				telegram_username TEXT
			);''')
		self.con.commit()
	def drop_tables(self):
		self.cur.execute('DROP TABLE bloggers; DROP TABLE orders;')
		self.con.commit()
	def new_blogger(self, profile):
		self.cur.execute('''
		INSERT INTO bloggers(name, login, followers, avg_post_coverage, avg_story_coverage, followers_geo, avg_age, \
		male_ratio, female_ratio, subjects, post_price, story_price, chat_id, proof_photo_id, profile_photo_id, telegram_username)
		VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',\
		(profile.name, profile.login, profile.followers, profile.avg_post_coverage, profile.avg_story_coverage,\
		profile.followers_geo, profile.avg_age, profile.male_ratio, profile.female_ratio, profile.subjects,\
		profile.post_price, profile.story_price, profile.chat_id, profile.proof_photo_id, profile.profile_photo_id,\
		profile.telegram_username) )
		self.con.commit()
	def new_order(self, order):
		self.cur.execute('''
		INSERT INTO orders(name, login, descr, post_or_story, coverage, geo, age, gender, subject, 
		budget, comment, chat_id, telegram_username)
		VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',\
		(order.name, order.login, order.descr, order.post_or_story, order.coverage, order.geo, order.age, \
		order.gender, order.subject, order.budget, order.comment, order.chat_id, order.telegram_username) )
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
	def get_order_by_id(self, order_id):
		self.cur.execute('SELECT * FROM orders WHERE id = %s', (order_id, ))
		return self.cur.fetchone()
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

	def profile_edit_name(self, chat_id, name):
		self.cur.execute('UPDATE bloggers SET name = %s WHERE chat_id = %s', (str(name), str(chat_id)))
		self.con.commit()
	def profile_edit_login(self, chat_id, login):
		self.cur.execute('UPDATE bloggers SET login = %s WHERE chat_id = %s', (str(login), str(chat_id)))
		self.con.commit()
	def profile_edit_followers(self, chat_id, flw):
		self.cur.execute('UPDATE bloggers SET followers = %s WHERE chat_id = %s', (flw, str(chat_id)))
		self.con.commit()
	def profile_edit_post_cvg(self, chat_id, cvg):
		self.cur.execute('UPDATE bloggers SET avg_post_coverage = %s WHERE chat_id = %s', (cvg, str(chat_id)))
		self.con.commit()
	def profile_edit_story_cvg(self, chat_id, cvg):
		self.cur.execute('UPDATE bloggers SET avg_story_coverage = %s WHERE chat_id = %s', (cvg, str(chat_id)))
		self.con.commit()	
	def profile_edit_geo(self, chat_id, geo):
		self.cur.execute('UPDATE bloggers SET followers_geo = %s WHERE chat_id = %s', (geo, str(chat_id)))
		self.con.commit()
	def profile_edit_age(self, chat_id, age):
		self.cur.execute('UPDATE bloggers SET avg_age = %s WHERE chat_id = %s', (age, str(chat_id)))
		self.con.commit()
	def profile_edit_gender(self, chat_id, female):
		male = 100 - female
		self.cur.execute('UPDATE bloggers SET male_ratio = %s WHERE chat_id = %s', (male, str(chat_id)))
		self.cur.execute('UPDATE bloggers SET female_ratio = %s WHERE chat_id = %s', (female, str(chat_id)))
		self.con.commit()
	def profile_edit_subjects(self, chat_id, sub):
		self.cur.execute('UPDATE bloggers SET subjects = %s WHERE chat_id = %s', (sub, str(chat_id)))
		self.con.commit()
	def profile_edit_post_price(self, chat_id, price):
		self.cur.execute('UPDATE bloggers SET post_price = %s WHERE chat_id = %s', (price, str(chat_id)))
		self.con.commit()
	def profile_edit_story_price(self, chat_id, price):
		self.cur.execute('UPDATE bloggers SET story_price = %s WHERE chat_id = %s', (price, str(chat_id)))
		self.con.commit()
	def profile_edit_age(self, chat_id, age):
		self.cur.execute('UPDATE bloggers SET avg_age = %s WHERE chat_id = %s', (age, str(chat_id)))
		self.con.commit()
	def profile_edit_proof(self, chat_id, photo_id, ind):
		self.cur.execute('SELECT proof_photo_id FROM bloggers WHERE chat_id = %s', (str(chat_id), ))
		proofs = self.cur.fetchone()
		proofs[0][ind] = photo_id
		self.cur.execute('UPDATE bloggers SET proof_photo_id = %s WHERE chat_id = %s', (proofs[0], str(chat_id), ))
		self.con.commit()


	def order_edit_name(self, order_id, name):
		self.cur.execute('UPDATE orders SET name = %s WHERE id = %s', (name, str(order_id)))
		self.con.commit()
	def order_edit_login(self, order_id, login):
		self.cur.execute('UPDATE orders SET login = %s WHERE id = %s', (login, str(order_id)))
		self.con.commit()
	def order_edit_descr(self, order_id, descr):
		self.cur.execute('UPDATE orders SET descr = %s WHERE id = %s', (descr, str(order_id)))
		self.con.commit()
	def order_edit_coverage(self, order_id, cvg):
		self.cur.execute('UPDATE orders SET coverage = %s WHERE id = %s', (cvg, str(order_id)))
		self.con.commit()
	def order_edit_post_or_story(self, order_id, pos):
		self.cur.execute('UPDATE orders SET post_or_story = %s WHERE id = %s', (pos, str(order_id)))
		self.con.commit()
	def order_edit_name(self, order_id, name):
		self.cur.execute('UPDATE orders SET name = %s WHERE id = %s', (str(name), str(order_id)))
		self.con.commit()
	def order_edit_geo(self, order_id, geo):
		self.cur.execute('UPDATE orders SET geo = %s WHERE id = %s', (geo, str(order_id)))
		self.con.commit()
	def order_edit_age(self, order_id, age):
		self.cur.execute('UPDATE orders SET age = %s WHERE id = %s', (age, str(order_id)))
		self.con.commit()
	def order_edit_subject(self, order_id, subject):
		self.cur.execute('UPDATE orders SET subject = %s WHERE id = %s', (subject, str(order_id)))
		self.con.commit()
	def order_edit_gender(self, order_id, gender):
		self.cur.execute('UPDATE orders SET gender = %s WHERE id = %s', (gender, str(order_id)))
		self.con.commit()
	def order_edit_budget(self, order_id, budget):
		self.cur.execute('UPDATE orders SET budget = %s WHERE id = %s', (budget, str(order_id)))
		self.con.commit()
	def order_edit_comment(self, order_id, com):
		self.cur.execute('UPDATE orders SET comment = %s WHERE id = %s', (com, str(order_id)))
		self.con.commit()