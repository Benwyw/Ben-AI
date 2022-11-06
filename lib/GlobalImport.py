#import ctypes
#import ctypes.util

import asyncio
import functools
import itertools
import math
import random
import os
import io
import pytz
import requests
import discord
import yt_dlp
import pandas as pd
from lib.MinecraftServer import MinecraftServer as mc

from discord import slash_command, Option, OptionChoice, SlashCommandGroup
from discord.ext import commands, pages, tasks
from discord.ui import InputText, Modal

#find_opus = ctypes.util.find_library('opus')
#discord.opus.load_opus(find_opus)

from dotenv import load_dotenv
from random import randrange
from datetime import datetime
from tika import parser

import re
from lib.DBConnection import DBConnection
from lib.game.SortingOrders import order, presOrder, pokerOrder, suitOrder
from io import BytesIO
from discord.ext.tasks import loop
from PIL import Image, ImageDraw, ImageColor, ImageFont

BOT_PREFIX = '$'
bot = commands.Bot(BOT_PREFIX, description='使用Python的Ben AI，比由Java而成的Ben Kaneki更有效率。', guild_subscriptions=True, intents=discord.Intents.all())
bot.owner_id = os.getenv('OWNER_ID')
# Slash
from lib.GlobalVariables import *
load_dotenv()
if os.getenv('TOKEN')[0:3] == 'ODE':
    guild_ids = [guild_BenDiscordBot]

#from main import bot

# News API
from newsapi import NewsApiClient

# URL Validator
from urllib.parse import quote, urlparse

# Alpha Vantage
from alpha_vantage.timeseries import TimeSeries
import matplotlib
import matplotlib.pyplot as plt

# Game imports
from lib.game.Game import Game, TexasHoldEm, President

# Card ordering dictionary
ORDER = order

# Free Games
from bs4 import BeautifulSoup

# Cov Locate
from urllib.request import Request, urlopen
import json

# for URL encode base64
import base64

#Make plots bigger
matplotlib.rcParams['figure.figsize'] = (20.0, 10.0)


'''import logging
logging.basicConfig(level="DEBUG")'''


newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

# Listener
def getRegion(region):
    region = region.lower()
    if region == 'tw':
        return 'loltw'
    elif region == 'na':
        return 'lolna'
    
# API Key
load_dotenv()
ts = TimeSeries(key=os.getenv('API_KEY'), output_format='pandas')

# Google Map
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAP_API_KEY')

# Virus Total
load_dotenv()
VIRUS_TOTAL_API_KEY = os.getenv('VIRUS_TOTAL_API_KEY')

def getLatLonByAddress(address):
    urlparams = {'address': address}
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    if GOOGLE_MAPS_API_KEY is not None:
        urlparams['key'] = GOOGLE_MAPS_API_KEY
    try:
        response = requests.get(url, params=urlparams)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
    payload = response.json()
    lat = payload['results'][0]['geometry']['location']['lat']
    lon = payload['results'][0]['geometry']['location']['lng']
    return lat, lon

def getMapsImageByLatLon(lat, lon, zoom):
    scale = 1
    position = ','.join((str(lat), str(lon)))
    urlparams = {'center': position,
                'zoom': str(zoom),
                'maptype': 'roadmap',
                'scale': scale,
                'size': '640x640'}
    url = 'http://maps.google.com/maps/api/staticmap'
    if GOOGLE_MAPS_API_KEY is not None:
        urlparams['key'] = GOOGLE_MAPS_API_KEY
    try:
        response = requests.get(url, params=urlparams)
        image = Image.open(BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        print(e)
    return image

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False
    
def post_scan(payload, api):
    url = "https://www.virustotal.com/api/v3/urls"
    
    payload = f"url={payload}"
    headers = {
        "Accept": "application/json",
        "x-apikey": f"{api}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    return requests.post(url, data=payload, headers=headers)

# Minecraft
global mc_ops, temp_blocked_list
mc_ops = ['benlien', 'willywilly234', 'rykos714', 'pokz98']
temp_blocked_list = []

class OpError(Exception):
    pass

class VoiceError(Exception):
    pass

class YTDLError(Exception):
    pass

# Music
# Silence useless bug reports messages
yt_dlp.utils.bug_reports_message = lambda: ''

def get_log_channel():
    return bot.get_channel(809527650955296848)

def get_timestamp():
    return str(datetime.now(pytz.timezone('Asia/Hong_Kong')))

async def log(content):
    log_channel = get_log_channel()
    timestamp = get_timestamp()
    await log_channel.send(f'{str(content)}\n\n`{timestamp}`')

async def getUserById(userid):
    result = bot.get_user(int(userid))
    if result is None:
        result = await bot.fetch_user(int(userid))
    return result

async def getNewsEmbed(source):
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:
        # /v2/top-headlines
        if source == 'Rthk.hk':
            top_headlines = newsapi.get_top_headlines(category='general', language='zh', country='hk')
        else:
            top_headlines = newsapi.get_everything(sources=source, language='en', sort_by='publishedAt')

        selected_top_headline = ''
        for top_headline in top_headlines['articles']:
            #if top_headline['author'] == '香港經濟日報HKET':
            if top_headline['source']['name'] == source:
                selected_top_headline = top_headline
                break

        if selected_top_headline == '' or selected_top_headline is None:
            return

        publishedAt = selected_top_headline['publishedAt']
        db_published_at = DBConnection.getPublishedAt(source)[0][0]

        if str(publishedAt) == str(db_published_at):
            return
        else:
            DBConnection.updatePublishedAt(publishedAt, source)

            title = selected_top_headline['title']
            url = selected_top_headline['url']
            urlToImage = selected_top_headline['urlToImage'] if selected_top_headline['urlToImage'] is not None and 'http' in selected_top_headline['urlToImage'] and '://' in selected_top_headline['urlToImage'] else 'https://i.imgur.com/UdkSDcb.png'
            authorName = selected_top_headline['source']['name']
            author = selected_top_headline['author']
            description = selected_top_headline['description']
            footer = '{}'.format(publishedAt) if author is None else '{}\n{}'.format(author, publishedAt)
            iurl = str(DBConnection.getRemarks(source, 'Y')[0][0])

            embed = discord.Embed(title=title)
            #embed.color = 0xb50024

            #url handlings
            if url is not None and 'http' in url and '://' in url:
                if source == 'Rthk.hk':
                    url2 = url.rsplit('/',1)[1]
                    url1 = url.rsplit('/',1)[0]
                    if url2 is not None and url2 != '' and not url2.isalnum():
                        url2 = quote(url2)
                        url = url1 +'/'+ url2
                    embed.url = url
                else:
                    embed.url = url

            embed.description = description
            embed.set_author(name=authorName, icon_url=iurl) #News API logo: https://i.imgur.com/UdkSDcb.png
            embed.set_thumbnail(url=urlToImage)
            embed.set_footer(text=footer)

            return embed
    except Exception as e:
        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
        if 'DPY-4011' in str(e):
            await BDS_Log_Channel.send('<@{}>\n{}\n\nError occured in newsLoop({})\n{}'.format(bot.owner_id,e,source,timestamp))
        else:
            await BDS_Log_Channel.send('{}\n\nError occured in newsLoop({})\n{}'.format(e,source,timestamp))

async def is_owner(ctx):
    if str(ctx.author.id) == str(bot.owner_id):
        return True
    else:
        return await ctx.send_followup('This command is for owner use only.')