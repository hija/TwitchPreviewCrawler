# This is the main class for the crawler

# Imports
from twitch import TwitchClient
import configparser
import os

class TwitchPreviewCrawler:

	def __init__(self, twitch_api_key):
		self.twitch_api_key = twitch_api_key
		self.client = TwitchClient(client_id = self.twitch_api_key)


def main():
	# Load data from config file
	config = _load_config()
	if config:
		print('Test successful')
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
	print('>> Please enter the credentials to the config.ini first!')
	exit()

if __name__ == '__main__':
	# main!
	main()