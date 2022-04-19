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


# Game imports
import re
from Game import Game, TexasHoldEm, President
from DBConnection import DBConnection
from sortingOrders import order, presOrder, pokerOrder, suitOrder
from io import BytesIO
from discord.ext.tasks import loop
from discord.ext import tasks
from PIL import Image, ImageDraw, ImageColor, ImageFont

BOT_PREFIX = '$'
bot = commands.Bot(BOT_PREFIX, description='使用Python的Ben AI，比由Java而成的Ben Kaneki更有效率。', guild_subscriptions=True, intents=discord.Intents.all())

# Slash
global guild_ids
guild_ids = [763404947500564500, 351742829254410250, 671654280985313282, 490302069425700864]

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









# Card ordering dictionary
ORDER = order

# Free Games
from bs4 import BeautifulSoup

# Cov Locate
from urllib.request import Request, urlopen
import json

#Make plots bigger
matplotlib.rcParams['figure.figsize'] = (20.0, 10.0)

'''
import logging
logging.basicConfig(level="DEBUG")
'''

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