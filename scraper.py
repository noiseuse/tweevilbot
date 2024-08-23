from dotenv import load_dotenv
from selenium import webdriver as web
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

import os
import time
import json
import asyncio
import random

us = ''
load_dotenv()
profiles = []
executable_path = os.environ.get('EXECUTE_PATH')
json_file = 'followers.json'

with open('users.json', 'r') as file:
	user_data = json.load(file)

for profile in user_data.values():
	profiles.append(profile['instagram'])

class Instagram():
	def __init__(self, username, password):
		self.username = username
		self.password = password
		options = Options()
		options.add_experimental_option("excludeSwitches", ["enable-logging"])
		self.browser = web.Chrome(executable_path=executable_path, options=options)
		self.browser.set_window_size(1200, 900)

	def close_browser(self):
		self.browser.close()
		self.browser.quit()

	async def login(self):
		browser = self.browser
		try:
			browser.get('https://www.instagram.com')
			await asyncio.sleep(random.randrange(3, 5))
			# Enter username:
			username_input = browser.find_element_by_name('username')
			username_input.clear()
			username_input.send_keys(self.username)
			await asyncio.sleep(random.randrange(2, 4))
			# Enter password:
			password_input = browser.find_element_by_name('password')
			password_input.clear()
			password_input.send_keys(self.password)
			await asyncio.sleep(random.randrange(1, 2))
			password_input.send_keys(Keys.ENTER)
			await asyncio.sleep(random.randrange(3, 5))
			print(f'[{self.username}] Successfully logged on!\n')
		except Exception as ex:
			print(f'Error: {ex}')
			print(f'[{self.username}] Authorization fail')
			self.close_browser()

	def xpath_exists(self, url):
		browser = self.browser
		try:
			browser.find_element_by_xpath(url)
			exist = True
		except NoSuchElementException:
			exist = False
		return exist

	async def get_followers(self, users):
		followers_data = {}
		
		browser = self.browser
		
		for user in users:
			followers_data[user] = {}
	
		for user in users:
			print(f"\n Begin scraping {user}'s followers \n")
			browser.get('https://instagram.com/' + user)
			await asyncio.sleep(random.randrange(3, 5))
			followers_set = set()
			new_followers = set()
			
            # Get followers count
			count = browser.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a/span/span').text
			followers_button = browser.find_element_by_xpath('/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a')
			followers_button.click()
			await asyncio.sleep(random.randrange(3, 5))
			follower_box = browser.find_element_by_xpath("/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div/div/div[4]")
			
			if ',' in count:
				count = int(''.join(count.split(',')))
			else:
				count = int(count)
				
			attempts = 0
			added_users = 0
			max_attempts = 3
			
			if count > 500:
				max_attempts = 6
			
			while added_users < count and  attempts < max_attempts:
				browser.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 800", follower_box)
				await asyncio.sleep(random.randrange(3, 5))
				
				users_in_view = browser.find_elements(By.CSS_SELECTOR, '.x1dm5mii.x16mil14.xiojian.x1yutycm.x1lliihq.x193iq5w.xh8yej3')
				await asyncio.sleep(random.randrange(4, 7))
				
				for usr in users_in_view:
					try:
						username = usr.find_element_by_xpath(f"/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div/div/div[4]/div[{added_users + 1}]/div/div/div/div/div/div/div[2]/div/div/div/div/div/a/div/div/span").text
						new_followers.add(username)
						added_users += 1
					except Exception as ex:
						continue
				
				if new_followers.issubset(followers_set):
					attempts += 1
				else:
					attempts = 0

				followers_set.update(new_followers)
					
				followers_data[user] = list(followers_set)
				
				if added_users >= count:
					break
				
				with open(json_file, 'w') as file:
					json.dump(followers_data, file, indent=4)
					
			print(f"Finished scraping {user}'s {len(followers_set)} followers.")
		self.close_browser()
			
# insta = Instagram(os.environ.get('USERNAME'), os.environ.get('PASSWORD'))
# insta.login()
# insta.get_followers(['noiseus.e'])