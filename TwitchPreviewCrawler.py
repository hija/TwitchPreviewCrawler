# This is the main class for the crawler

# Imports
from twitch import TwitchClient
import configparser
import os

import logging
import sys

class TwitchPreviewCrawler:

	def __init__(self, twitch_api_key,topgames = None):
		self.__twitch_api_key = twitch_api_key
		self._client = TwitchClient(client_id = self.__twitch_api_key)

		# Load topgames...
		if not(topgames):
			# ... either from twitch
			self.topgames = list(self._get_top_games().keys())
		else:
			# ... or from our config file
			self.topgames = topgames
		
	def _get_top_games(self):
		# Get top games
		logging.info('>> Loading top games, since no top games have been predefined')
		_top_games = dict()
		for entry in self._client.games.get_top():
			_top_games[int(entry['game']['id'])] = entry['game']['name']
		logging.debug('>> Found the following games: ' + ', '.join(_top_games.values()))
		return _top_games

def main():
	# Setup logging
	logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
	# Load data from config file
	config = _load_config()
	if config:
		logging.info('>> Start Crawling data')
		twitch_crawler = TwitchPreviewCrawler(config.get('Twitch', 'key'))
		print(twitch_crawler.topgames)
	else:
		exit_missing_credentials()

def _load_config():
	if os.path.exists('config.ini'):
		config_parser = configparser.ConfigParser()
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
			config_parser.set('Twitch', 'key')
			config_parser.set('Twitch', 'min_delay', '60')
			config_parser.write(f)
		return False

def exit_missing_credentials():
	logging.error('>> Please enter the credentials to the config.ini first!')
	exit()

if __name__ == '__main__':
	# main!
	main()