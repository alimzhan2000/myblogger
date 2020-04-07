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
