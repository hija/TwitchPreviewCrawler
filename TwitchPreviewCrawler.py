"""
This code was written for Data Analytics 2
It allows one to download twitch.tv preview images.

How to use it:
1. Start the TwitchPreviewCrawler.py 
 -> A config file is generated, the crawler itself stops
2. Edit the config file
3. Start the TwitchPreviewCrawler.py again
 -> The crawler starts crawling until you stop it.

How to obtain an API Key:
 -> https://dev.twitch.tv/docs/v5/guides/using-the-twitch-api
"""

# Imports
from twitch import TwitchClient
import configparser
import os

import logging
import sys
import time

from requests import get

import re

class TwitchPreviewCrawler:
	"""
	This is the Twitch preview image crawler class.
	It only has one method: crawl()
	If you want to stop the crawler from crawling just set the variable abortcrawling to True.
	Please note, that it might take some time for the crawler to stop, since it uses time.sleep
	"""

	def __init__(self, twitch_api_key, delay, image_delay, preview_size, topgames = None):
		"""
		Constructor of the twitch image preview crawler.

		@twitch_api_key Valid twich api key
		@delay Delay between two crawling sessions
		@image_delay Delay between downloading images, e.g. if set to 1 the download of three images takes two seconds.
		@preview_size The requested preview size (small, medium or large)
		@topgames A list of topgames, if set to None the topgames will be determined by the twitch api
		"""

		self.abortcrawling = False # Set to True to stop the crawler
		self._delay = delay 
		self._image_delay = image_delay
		self.__twitch_api_key = twitch_api_key
		self._preview_size = preview_size
		self._client = TwitchClient(client_id = self.__twitch_api_key) # Uses the external Twitch Api

		# Load topgames...
		if not(topgames):
			# ... either from twitch API
			logging.info('>> Loading top games, since no top games have been predefined')
			self.topgames = list(self._get_top_games().values())
		else:
			# ... or from our config file
			self.topgames = topgames
		
	def _get_top_games(self):
		"""
		This method gets the toplist from the twitch api
		@return Topgames as list
		"""
		_top_games = dict()
		for entry in self._client.games.get_top():
			_top_games[int(entry['game']['id'])] = entry['game']['name']
		logging.debug('>> Found the following games: ' + ', '.join(_top_games.values()))
		return _top_games

	def crawl(self):
		"""
		Does the actual crawling.
		"""
		while(not(self.abortcrawling)):
			logging.info('>> Downloading images!')
			for game in self.topgames: # For every game in the gameslist...
				streams = self._client.streams.get_live_streams(game = game) #... get the livechannel list
				for stream in streams: # For every stream in the games' livechannel list...
					image_url = stream['preview'][self._preview_size] #... get the preview image url
					self._download_image(image_url, game) # Download the image
					time.sleep(self._image_delay) # Sleep for the delay between image downloads
			logging.info('>> Downloaded images! Now I am going to sleep.') # After images have been downloaded
			time.sleep(self._delay) # Sleep


	def _download_image(self, image_url, game_name):
		"""
		Downloads an image. This method is specifically bind to the Twitch Game Crawler - do not use it in other projects!
		"""
		directory_name = 'images/' + TwitchPreviewCrawler.slugify(game_name) # First get the directory name, e.g. DOTA_2
		file_name = directory_name + '/' + image_url.split('ttv/')[1].split(".jpg")[0] + "_" + str(time.mktime(time.gmtime())) + ".jpg" # Create the filename
		
		os.makedirs(directory_name, exist_ok=True) # Create the directory structure where the files shall be stored
		
		with open(file_name, "wb") as file:
			response = get(image_url) # Download the image
			file.write(response.content) # Write it into the file

	def slugify(value):
		"""
		Code by Django Framework! It's used to create os-accepted direcotry names (e.g. "Player's" is not allwoed, so ít gets changes to Player_s)
		"""
		s = str(value).strip().replace(' ', '_')
		return re.sub(r'(?u)[^-\w.]', '', s)

def main():
	"""
	This is the main method and its used to start the crawler with a config file.
	"""

	# Setup logging
	logging.basicConfig(stream=sys.stderr, level=logging.INFO) # We log messages with the logginglevel Info
	logging.getLogger('urllib3').setLevel(logging.WARNING) # Stops boring error messages

	# Load data from config file
	config = _load_config()
	if config:
		logging.info('>> Start Crawling data')
		
		topgames = None # Defined later...
		if config.has_option('Twitch','topgames'):
			# If we have already defined topgames we use them
			topgames = [str.strip(x) for x in config.get('Twitch','topgames').split(';')]

		twitch_crawler = TwitchPreviewCrawler(config.get('Twitch', 'key'),
			int(config.get('Twitch', 'min_delay', fallback=300)),
			float(config.get('Twitch', 'min_delay_download', fallback=0.8)),
			config.get('Twitch', 'preview_size', fallback='medium'),
			topgames) # We create the twitchcrawler instance

		# We write the topgames to our config, so we always crawl the same games!
		if not(topgames): # Only if we did not have topgames before:
			with open('config.ini','w') as f:
				config.set('Twitch', '; Enter your topgames, seperated by ;')
				config.set('Twitch', 'topgames', ';'.join([str(x) for x in twitch_crawler.topgames]))
				config.write(f)

		# Start crawling
		twitch_crawler.crawl()
	else:
		exit_missing_credentials()

def _load_config():
	"""
	This method loads or creates a config file.config
	@return config
	"""
	if os.path.exists('config.ini'): # if the config file exists already
		config_parser = configparser.ConfigParser(allow_no_value=True)
		config_parser.read('config.ini')
		if config_parser.has_option('Twitch', 'key') and len(config_parser.get('Twitch', 'key')) > 0:
			return config_parser
		else:
			return False
	else: # create a new config gile
		with open('config.ini','w') as f:
			config_parser = configparser.ConfigParser(allow_no_value=True)
			config_parser.add_section('Twitch')
			config_parser.set('Twitch', '; General Twitch settings here')

			config_parser.set('Twitch', '; Enter your application key here')
			config_parser.set('Twitch', 'key', '')
			config_parser.set('Twitch', '; Enter the minimum seconds between checking images')
			config_parser.set('Twitch', 'min_delay', '300')
			config_parser.set('Twitch', '; Enter the minimum seconds between downloading images')
			config_parser.set('Twitch', 'min_delay_download', '0.8')
			config_parser.set('Twitch', '; Enter the preview-image size (small medium or large)')
			config_parser.set('Twitch', 'preview_size', 'medium')
			config_parser.write(f)
		return False

def exit_missing_credentials():
	logging.error('>> Please enter the credentials to the config.ini first!')
	exit()

if __name__ == '__main__':
	main()