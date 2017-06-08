# This is the main class for the crawler

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

	def __init__(self, twitch_api_key, delay, image_delay, preview_size, topgames = None):
		self.abortcrawling = False
		self._delay = delay
		self._image_delay = image_delay
		self.__twitch_api_key = twitch_api_key
		self._preview_size = preview_size
		self._client = TwitchClient(client_id = self.__twitch_api_key)

		# Load topgames...
		if not(topgames):
			# ... either from twitch
			logging.info('>> Loading top games, since no top games have been predefined')
			self.topgames = list(self._get_top_games().values())
		else:
			# ... or from our config file
			self.topgames = topgames
		
	def _get_top_games(self):
		_top_games = dict()
		for entry in self._client.games.get_top():
			_top_games[int(entry['game']['id'])] = entry['game']['name']
		logging.debug('>> Found the following games: ' + ', '.join(_top_games.values()))
		return _top_games

	def crawl(self):
		while(not(self.abortcrawling)):
			logging.info('>> Downloading images!')
			# First get all channels
			for game in self.topgames:
				streams = self._client.streams.get_live_streams(game = game)
				for stream in streams:
					image_url = stream['preview'][self._preview_size]
					self._download_image(image_url, game)
					time.sleep(self._image_delay)
			logging.info('>> Downloaded images! Now I am going to sleep.')
			time.sleep(self._delay)


	def _download_image(self, image_url, game_name):
		# Maybe we should change this line later, it's a mess!
		directory_name = 'images/' + TwitchPreviewCrawler.slugify(game_name)
		file_name = directory_name + '/' + image_url.split('ttv/')[1].split(".jpg")[0] + "_" + str(time.mktime(time.gmtime())) + ".jpg"
		
		os.makedirs(directory_name, exist_ok=True)
		
		with open(file_name, "wb") as file:
			response = get(image_url)
			file.write(response.content)

	def slugify(value):
		"""
		Code by Django Framework!
		"""
		s = str(value).strip().replace(' ', '_')
		return re.sub(r'(?u)[^-\w.]', '', s)

def main():
	# Setup logging
	logging.basicConfig(stream=sys.stderr, level=logging.INFO)
	# Load data from config file
	config = _load_config()
	if config:
		logging.info('>> Start Crawling data')
		
		topgames = None # Defined later...
		if config.has_option('Twitch','topgames'):
			# If we have already defined topgames we use them
			topgames = [str.strip(x) for x in config.get('Twitch','topgames').split(';')]

		twitch_crawler = TwitchPreviewCrawler(config.get('Twitch', 'key'),
			int(config.get('Twitch', 'min_delay', fallback=60)),
			float(config.get('Twitch', 'min_delay_download', fallback=0.8)),
			config.get('Twitch', 'preview_size', fallback='medium'),
			topgames)

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
	if os.path.exists('config.ini'):
		config_parser = configparser.ConfigParser(allow_no_value=True)
		config_parser.read('config.ini')
		if config_parser.has_option('Twitch', 'key') and len(config_parser.get('Twitch', 'key')) > 0:
			return config_parser
		else:
			return False
	else:
		with open('config.ini','w') as f:
			config_parser = configparser.ConfigParser(allow_no_value=True)
			config_parser.add_section('Twitch')
			config_parser.set('Twitch', '; General Twitch settings here')

			config_parser.set('Twitch', '; Enter your application key here')
			config_parser.set('Twitch', 'key', '')
			config_parser.set('Twitch', '; Enter the minimum seconds between checking images')
			config_parser.set('Twitch', 'min_delay', '60')
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