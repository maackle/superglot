from flask import current_app as app


RATINGS = [1, 2, 3, 4]
RATING_MIN = 1
RATING_MAX = 4
PASS_RATING_MIN = 2

def process_answer(rating, ease_factor, num_repetitions):
	if not _passing_rating(rating):
		num_repetitions = 0
		interval = 0
	else:
		ease_factor = _calculate_ease_factor(ease_factor, rating)
		if rating == PASS_RATING_MIN:
			interval = 0
		else:
			num_repetitions += 1
			if num_repetitions == 1:
				interval = 1
			elif num_repetitions == 2:
				interval = 6
			else:
				interval *= ease_factor
	return (interval, ease_factor, num_repetitions)

def _passing_rating(rating):
	return rating >= PASS_RATING_MIN
		
def _calculate_ease_factor(ease_factor, rating):
	ease_factor += (0.1-(RATING_MAX-rating)*(0.08+(RATING_MAX-rating)*0.02))
	return max(ease_factor, 1.3)


# class SRS(object):
# 	'''
# 	https://github.com/matholroyd/tworgy-spaced-repetition/blob/master/lib/spaced-repetition/sm2.rb
# 	'''

# 	ease_factor = 2.5
# 	num_repetitions = 0
# 	next_repetition = None
# 	interval = 0

# 	def process_answer(self, rating):
# 		if not SRS.passing_rating(rating):
# 			self.num_repetitions = 0
# 			self.interval = 0
# 		else:
# 			self.ease_factor = SRS.calculate_ease_factor(self.ease_factor, rating)
# 			if rating == SRS.PASS_RATING_MIN:
# 				self.interval = 0
# 			else:
# 				self.num_repetitions += 1
# 				if self.num_repetitions == 1:
# 					self.interval = 1
# 				elif self.num_repetitions == 2:
# 					self.interval = 6
# 				else:
# 					self.interval *= self.ease_factor
# 		self.next_repetition = 

# 	@staticmethod
# 	def passing_rating(rating):
# 		return rating >= SRS.PASS_RATING_MIN
		
# 	@staticmethod
# 	def calculate_ease_factor(ease_factor, rating):
# 		ease_factor += (0.1-(SRS.RATING_MAX-rating)*(0.08+(SRS.RATING_MAX-rating)*0.02))
#		return max(ease_factor, 1.3)