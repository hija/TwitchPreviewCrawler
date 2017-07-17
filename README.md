# TwitchPreviewCrawler
Crawls Twitch.tv's (temporary) preview pictures of the stream.

# Requirements
This crawler was tested with python 3.6.1. Please use pip to download requirements (see next step, Installation).

# Installation
Use the requirements.txt to install all required packages

    pip install -r requirements.txt

# How it works
The crawler makes use of the official twitch.tv-API3. The crawler works in the following manner. 
1. Check if the config.ini file exists 
1.1. If this is not the case, create the config.ini and exit the program, so the user can fill out the config.ini file 
2. Check if the config.ini file contains the twitch api key key 
2.1. If this is not the case, exit the program with an error message 
3. Check if the user has specified the games topgames which shall be crawled 
3.1. Otherwise use the current top 10 games which are streamed on twitch 
4. For every game which shall be crawled... 
4.1. Get all available streams... 
4.1.1. And download the preview image. Then sleep for min_delay_download seconds 
4.2. After every game has been crawled, sleep for min_delay seconds and return to step 4. 

Furthermore, the value delay_on_error can be specified which sets the program to sleep if an error occurs (e.g. network error). The program can be exit by sending the terminate signal to the program.

The cursive written variables can be specified in the config.ini. The Python program was run on a Debian Server to collect the images. 
