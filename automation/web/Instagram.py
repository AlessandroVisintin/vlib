from vlib.automation.web.Browser import Browser


class Instagram:


	def __init__(self, drv_path):
		self.brs = Browser(drv_path)


	def __del__(self):
		del self.brs


	def login(self, username, password, sleep=0):
		self.brs.open('https://instagram.com')
		#cookie
		self.brs.click('body > div.RnEpo.Yx5HN._4Yzd2 > div > div > button.aOOlW.bIiDR', sleep=2)
		#username
		self.brs.send('input[name="username"]', username, sleep=2)
		#password
		self.brs.send('input[type="password"]', password, sleep=2)
		#login
		log_btn = '#loginForm > div > div:nth-child(3) > button > div'
		if sleep > 0:
			self.brs.click(log_btn, sleep=sleep)
		else:
			self.brs.click(log_btn)
