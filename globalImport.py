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
import MinecraftServer as mc

from discord import slash_command, Option, OptionChoice
from discord.ext import commands, pages
from discord.ui import InputText, Modal

from dotenv import load_dotenv
from random import randrange
from datetime import datetime
from tika import parser

import re
from DBConnection import DBConnection
from sortingOrders import order, presOrder, pokerOrder, suitOrder
from io import BytesIO
from discord.ext.tasks import loop
from discord.ext import tasks
from PIL import Image, ImageDraw, ImageColor, ImageFont

BOT_PREFIX = '$'
bot = commands.Bot(BOT_PREFIX, description='使用Python的Ben AI，比由Java而成的Ben Kaneki更有效率。', guild_subscriptions=True, intents=discord.Intents.all())

# Slash
from config.GlobalVariables import *
load_dotenv()
if os.getenv('TOKEN')[0:3] == 'ODE':
    guild_ids = [guild_BenDiscordBot]

#from main import bot

from io import BytesIO
from PIL import Image, ImageDraw, ImageColor, ImageFont
import requests
from datetime import datetime
import pytz

# News API
from newsapi import NewsApiClient
from urllib.parse import quote

# Alpha Vantage
from alpha_vantage.timeseries import TimeSeries
import matplotlib
import matplotlib.pyplot as plt

# Game imports
from Game import Game, TexasHoldEm, President

# Card ordering dictionary
ORDER = order

# Free Games
from bs4 import BeautifulSoup

# Cov Locate
from urllib.request import Request, urlopen
import json

# URL Validator
from urllib.parse import urlparse

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
    await log_channel.send(f'{str(content)}\n\n{timestamp}')