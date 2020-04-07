import psycopg2
import telebot
import os
from profiles import Blogger

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
			);''')
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
			tmp[0] = ['спорт', 'лайфстайл', 'красота', 'личностный рост', 'бизнес', 'все']
		else:
			tmp[0].append('все')
		if len(tmp[1]) == 0:
			tmp[1] = ['Нур-Султан', 'Алматы', 'Шымкент', 'Караганда']
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
		tmp[0].remove('все')
		tmp = self.cur.fetchall()
		profiles = []
		for a in tmp:
			profiles.append(a[0])
		return profiles