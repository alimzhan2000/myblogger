class Blogger:
	def __init__(self, profile=None):
		if profile is None:
			self.name = ""
			self.login = ""
			self.followers = 0
			self.avg_post_coverage = 0
			self.avg_story_coverage = 0
			self.followers_geo = []
			self.avg_age = []
			self.male_ratio = 0
			self.female_ratio = 0
			self.subjects = []
			self.post_price = 0
			self.story_price = 0
			self.chat_id = ""
			self.proof_photo_id = []
			self.profile_photo_id = ""
			self.telegram_username = ""
		else:
			self.name = profile[1]
			self.login = profile[2]
			self.followers = profile[3]
			self.avg_post_coverage = profile[4]
			self.avg_story_coverage = profile[5]
			self.followers_geo = profile[6]
			self.avg_age = profile[7]
			self.male_ratio = profile[8]
			self.female_ratio = profile[9]
			self.subjects = profile[10]
			self.post_price = profile[11]
			self.story_price = profile[12]
			self.chat_id = profile[13]
			self.proof_photo_id = profile[14]
			self.profile_photo_id = profile[15]
			self.telegram_username = profile[16]
class Order:
	def __init__(self, order=None):
		if order is None:
			self.name = ""
			self.login = ""
			self.descr = ""
			self.post_or_story = ""
			self.coverage = 0
			self.geo = []
			self.age = []
			self.gender = ""
			self.subject = ""
			self.budget = 0
			self.comment = ""
			self.chat_id = ""
			self.telegram_username = ""
		else:
			self.name = order[1]
			self.login = order[2]
			self.descr = order[3]
			self.post_or_story = order[4]  
			self.coverage = order[5]
			self.geo = order[6]
			self.age = order[7]
			self.gender = order[8]
			self.subject = order[9]
			self.budget = order[10]
			self.comment = order[11]
			self.chat_id = order[12]
			self.telegram_username = order[13]
cities = [
	'Toronto',
	'Mississauga',
	'Waterloo',
	'Guelph',
	'Montreal',
	'Vancouver',
	'Calgary',
	'Ottawa-Gatineau',
	'Edmonton',
	'Winnipeg',
	'Quebec city',
	'Hamilton',
	'Victoria',
	'Halifax',
	'Oshawa',
	'Windsor'
]
categories = [
	'Lifestyle',
	'Humor',
	'Fashion',
	'Cosmetics',
	'Insta mum',
	'Insta dad',
	'Food',
	'Travel',
	'Dance/Music',
	'Insta couple',
	'Entreprenership/Business',
	'Video/Photo making'
]
