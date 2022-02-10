# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Valentin B.
A simple music bot written in discord.py using youtube-dl.
Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.
Requirements:
Python 3.5+
pip install -U discord.py pynacl youtube-dl
You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.
"""

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

from discord import slash_command
from discord.ext import commands, pages
from discord.ui import InputText, Modal

from dotenv import load_dotenv
from random import randrange
from datetime import datetime
from tika import parser

#Game imports
import re
from Game import Game, TexasHoldEm, President
from DBConnection import DBConnection
from sortingOrders import order, presOrder, pokerOrder, suitOrder
from io import BytesIO
from discord.ext.tasks import loop
from discord.ext import tasks
from PIL import Image, ImageDraw, ImageColor, ImageFont

BOT_PREFIX = '$'

#========================Slash========================
global guild_ids
guild_ids = [763404947500564500, 351742829254410250, 671654280985313282]

#========================Minecraft========================
global mc_ops, temp_blocked_list
mc_ops = ['benlien', 'willywilly234', 'rykos714', 'pokz98']
temp_blocked_list = []

#========================Alpha Vantage========================
from alpha_vantage.timeseries import TimeSeries
import matplotlib
import matplotlib.pyplot as plt

#========================Free Games========================
from bs4 import BeautifulSoup

#========================News API========================
from newsapi import NewsApiClient
from urllib.parse import quote

#========================Google Map========================
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

#========================Cov Locate========================
from urllib.request import Request, urlopen
import json

#Make plots bigger
matplotlib.rcParams['figure.figsize'] = (20.0, 10.0)

#API Key
load_dotenv()
ts = TimeSeries(key=os.getenv('API_KEY'), output_format='pandas')
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

#========================News========================
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
            iurl = str(DBConnection.getRemarks(source)[0][0])

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
        await BDS_Log_Channel.send('{}\n\nError occured in newsLoop({})\n{}'.format(e,source,timestamp))

#========================Listener========================
def getRegion(region):
    region = region.lower()
    if region == 'tw':
        return 'loltw'
    elif region == 'na':
        return 'lolna'

#========================Checks========================
def is_in_guild(guild_id):
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == guild_id
    return commands.check(predicate)

#========================Game========================
# Card constants
offset = 10
cardWidth = 138
cardHeight = 210

gameList = []

uncategorized = ['game', 'hand',  'in', 'rc', 'setcolor', 'setsort', 'start']

# Card generator
cardChoices = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suits = ['C', 'D', 'H', 'S']

# Card ordering dictionary
ORDER = order

# Deck constant
deck = ["https://i.imgur.com/VBdPy26.png", "https://i.imgur.com/yGcued2.png", "https://i.imgur.com/5SR155z.png", "https://i.imgur.com/8M9EbWg.png", "https://i.imgur.com/aR5T1do.png", "https://i.imgur.com/A9Nyxwn.png", "https://i.imgur.com/pKv3o52.png",
        "https://i.imgur.com/sEqDkMq.png", "https://i.imgur.com/rxaKhG4.png", "https://i.imgur.com/11yLhfD.png", "https://i.imgur.com/bq6lb5Z.png", "https://i.imgur.com/0Znul30.png", "https://i.imgur.com/md7LNs3.png", "https://i.imgur.com/GoyjsN6.png",
        "https://i.imgur.com/J3sKcoF.png", "https://i.imgur.com/0F2KC0D.png", "https://i.imgur.com/KYWeqAC.png", "https://i.imgur.com/smLknK1.png", "https://i.imgur.com/F98Y3CA.png", "https://i.imgur.com/SS7SFsT.png", "https://i.imgur.com/NRQiCiJ.png",
        "https://i.imgur.com/pTlYzW7.png", "https://i.imgur.com/v9iTjcX.png", "https://i.imgur.com/DiuE5ye.png", "https://i.imgur.com/ntwFoQr.png", "https://i.imgur.com/qSZoZT3.png", "https://i.imgur.com/mFdtL9O.png", "https://i.imgur.com/SsNG5L8.png",
        "https://i.imgur.com/3qqBau2.png", "https://i.imgur.com/DrehITV.png", "https://i.imgur.com/LblY086.png", "https://i.imgur.com/hj27dUO.png", "https://i.imgur.com/43gwYkW.png", "https://i.imgur.com/2bMLCBW.png", "https://i.imgur.com/0lqLY4E.png",
        "https://i.imgur.com/kQARj7b.png", "https://i.imgur.com/S3BUfV7.png", "https://i.imgur.com/PNGooTc.png", "https://i.imgur.com/8WhdL65.png", "https://i.imgur.com/PjxnGhg.png", "https://i.imgur.com/9cDlc0C.png", "https://i.imgur.com/4XM9H2y.png",
        "https://i.imgur.com/y3NLpIF.png", "https://i.imgur.com/7o4C1LX.png", "https://i.imgur.com/zAr7vhg.png", "https://i.imgur.com/R4bYTZo.png", "https://i.imgur.com/N8qoXrl.png", "https://i.imgur.com/MJIoVsk.png", "https://i.imgur.com/WpL2pJI.png",
        "https://i.imgur.com/bXFkuPH.png", "https://i.imgur.com/UQSjCzN.png", "https://i.imgur.com/vakonuH.png"]

def findFileName(suit, card):
    if suit == 'D':
        if card == 'A':
            return "https://i.imgur.com/pKv3o52.png"
        elif card == '2':
            return "https://i.imgur.com/0Znul30.png"
        elif card == '3':
            return "https://i.imgur.com/aR5T1do.png"
        elif card == '4':
            return "https://i.imgur.com/GoyjsN6.png"
        elif card == '5':
            return "https://i.imgur.com/SS7SFsT.png"
        elif card == '6':
            return "https://i.imgur.com/5SR155z.png"
        elif card == '7':
            return "https://i.imgur.com/md7LNs3.png"
        elif card == '8':
            return "https://i.imgur.com/2bMLCBW.png"
        elif card == '9':
            return "https://i.imgur.com/PjxnGhg.png"
        elif card == '10':
            return "https://i.imgur.com/kQARj7b.png"
        elif card == 'J':
            return "https://i.imgur.com/MJIoVsk.png"
        elif card == 'Q':
            return "https://i.imgur.com/7o4C1LX.png"
        elif card == 'K':
            return "https://i.imgur.com/WpL2pJI.png"
    elif suit == 'C':
        if card == 'A':
            return "https://i.imgur.com/bq6lb5Z.png"
        elif card == '2':
            return "https://i.imgur.com/8M9EbWg.png"
        elif card == '3':
            return "https://i.imgur.com/VBdPy26.png"
        elif card == '4':
            return "https://i.imgur.com/DiuE5ye.png"
        elif card == '5':
            return "https://i.imgur.com/qSZoZT3.png"
        elif card == '6':
            return "https://i.imgur.com/KYWeqAC.png"
        elif card == '7':
            return "https://i.imgur.com/LblY086.png"
        elif card == '8':
            return "https://i.imgur.com/hj27dUO.png"
        elif card == '9':
            return "https://i.imgur.com/DrehITV.png"
        elif card == '10':
            return "https://i.imgur.com/3qqBau2.png"
        elif card == 'J':
            return "https://i.imgur.com/4XM9H2y.png"
        elif card == 'Q':
            return "https://i.imgur.com/R4bYTZo.png"
        elif card == 'K':
            return "https://i.imgur.com/zAr7vhg.png"
    elif suit == 'H':
        if card == 'A':
            return "https://i.imgur.com/sEqDkMq.png"
        elif card == '2':
            return "https://i.imgur.com/rxaKhG4.png"
        elif card == '3':
            return "https://i.imgur.com/yGcued2.png"
        elif card == '4':
            return "https://i.imgur.com/11yLhfD.png"
        elif card == '5':
            return "https://i.imgur.com/NRQiCiJ.png"
        elif card == '6':
            return "https://i.imgur.com/0lqLY4E.png"
        elif card == '7':
            return "https://i.imgur.com/8WhdL65.png"
        elif card == '8':
            return "https://i.imgur.com/J3sKcoF.png"
        elif card == '9':
            return "https://i.imgur.com/43gwYkW.png"
        elif card == '10':
            return "https://i.imgur.com/0F2KC0D.png"
        elif card == 'J':
            return "https://i.imgur.com/9cDlc0C.png"
        elif card == 'Q':
            return "https://i.imgur.com/y3NLpIF.png"
        elif card == 'K':
            return "https://i.imgur.com/vakonuH.png"
    elif suit == 'S':
        if card == 'A':
            return "https://i.imgur.com/SsNG5L8.png"
        elif card == '2':
            return "https://i.imgur.com/mFdtL9O.png"
        elif card == '3':
            return "https://i.imgur.com/F98Y3CA.png"
        elif card == '4':
            return "https://i.imgur.com/pTlYzW7.png"
        elif card == '5':
            return "https://i.imgur.com/A9Nyxwn.png"
        elif card == '6':
            return "https://i.imgur.com/ntwFoQr.png"
        elif card == '7':
            return "https://i.imgur.com/PNGooTc.png"
        elif card == '8':
            return "https://i.imgur.com/S3BUfV7.png"
        elif card == '9':
            return "https://i.imgur.com/smLknK1.png"
        elif card == '10':
            return "https://i.imgur.com/v9iTjcX.png"
        elif card == 'J':
            return "https://i.imgur.com/UQSjCzN.png"
        elif card == 'Q':
            return "https://i.imgur.com/bXFkuPH.png"
        elif card == 'K':
            return "https://i.imgur.com/N8qoXrl.png"


def hasCommandByName(name: str):
    for command in commands.commands:
        if command.name == name:
            return command
    return None

# Check if a user in participating in a game
def checkInGame(user: discord.Member):
    for GAME in gameList:
        if GAME.hasPlayer(user):
            return True
    return False

# Get a Game object by its 6-digit id
def getGameByid(id):
    for GAME in gameList:
        if GAME.ID == id:
            return GAME

# Check if a Game object exists given a 6-digit id
def hasGame(id):
    for GAME in gameList:
        if GAME.ID == id:
            return True
    return False

# Get a Game object that the user is participating in
def getGame(user: discord.Member):
    for GAME in gameList:
        if GAME.hasPlayer(user):
            return GAME

# Get a Game by channel
def getGameByChannel(channel):
    for GAME in gameList:
        if GAME.channel == channel:
            return GAME
    return None

# Check if message and game channel match
def channelCheck(GAME, CHANNEL):
    return GAME.channel == CHANNEL

# Return a discord File object representing the user's hand
def showHand(user, userHand):
    userHand = sortHand(user, userHand)
    # Find dimensions
    numCards = len(userHand)
    maxWidth = (int(cardWidth / 3) * (numCards - 1)) + cardWidth + 20
    COLOR = DBConnection.fetchUserData("colorPref", str(user.id))
    # Create base hand image
    HAND = Image.new("RGB", (maxWidth, cardHeight + 40), ImageColor.getrgb(COLOR))
    DRAW = ImageDraw.Draw(HAND)
    font = ImageFont.truetype(requests.get('http://geocities.ws/benwyw/calibri.ttf', stream=True).raw, size=24)
    for i in range(0, numCards):
        fname = str(userHand[i].split("/")[1])
        lname = fname.split(".")[0]
        if len(lname) > 2:
            card = fname[0]+fname[1]
            suit = fname[2]
        else:
            card = fname[0]
            suit = fname[1]
        url = findFileName(suit,card)
        card = Image.open(requests.get(url, stream=True).raw)
        card = card.resize((cardWidth, cardHeight))
        HAND.paste(card, (10 + int(cardWidth / 3) * i, 10))
        DRAW.text((30 + int(cardWidth / 3) * i, cardHeight + 15), str(i), fill=ImageColor.getrgb("#ffffff"), font=font)
    with BytesIO() as img:
        HAND.save(img, 'PNG')
        img.seek(0)
        file = discord.File(fp=img, filename='hand.png')
        return file

# Sort user's hand based on their preferred sorting style
def sortHand(user: discord.Member, HAND):
    global ORDER, presOrder, suitOrder, order
    h = []
    sorttype = DBConnection.fetchUserData("sortPref", str(user.id))
    if sorttype== 'p':
        ORDER = presOrder
    elif sorttype == 's':
        ORDER = suitOrder
    else:
        ORDER = order
    for card in HAND:
        val = ORDER[card]
        index = 0
        while index < len(h) and val > ORDER[h[index]]:
            index += 1

        if index >= len(h):
            h.append(card)
        else:
            h.insert(index, card)

    return h

"""
Commands Start Here
"""
#========================RIOT LoL
class RiotApi(object):
    def __init__(self, api_key: str, region="na1"):
        self.__RIOT_API_KEY = api_key
        self.__HEADER = {'X-Riot-Token': self.__RIOT_API_KEY}
        self.__REGION = region
        self.__ROUTING = "americas"
        self.__BASE_URL = ".api.riotgames.com/lol/"
        self.__API_URL_SUMMONER_V4 = "https://" + self.__REGION + self.__BASE_URL + "summoner/v4/summoners/"
        self.__API_URL_MATCH_V5 = "https://" + self.__ROUTING + self.__BASE_URL + "match/v5/matches/by-puuid/"
        self.__API_URL_MATCH_V5_MATCHID = "https://" + self.__ROUTING + self.__BASE_URL + "match/v5/matches/"

    def get_summoner_by_name(self, summoner_name: str) -> dict:
        """Summoner Infos and Ids
        @param summoner_name: LoL summoner name
        @return json object of infos and ids
        """
        url = self.__API_URL_SUMMONER_V4 + "by-name/" + summoner_name
        request = requests.get(url, headers=self.__HEADER)
        return request.json()

    def get_matches_by_name(self, puuid: str) -> dict:
        """Get summoner match history by name"""

        url = self.__API_URL_MATCH_V5 + puuid + "/ids"
        request = requests.get(url, headers=self.__HEADER)
        return request.json()

    def get_matches_by_matchid(self, matchid: str) -> dict:
        """Get matches by match id"""

        url = self.__API_URL_MATCH_V5_MATCHID + matchid
        request = requests.get(url, headers=self.__HEADER)
        return request.json()

    def get_summoner_by_puuid(self, puuid: str) -> dict:
        """Get summoner info by puuid"""

        url = self.__API_URL_SUMMONER_V4 + "by-puuid/" + puuid
        request = requests.get(url, headers=self.__HEADER)
        return request.json()

    #call
    def get_latest_matches_by_name(self, summoner_name:str) -> dict:
        """Latest match history info by summoner name"""

        gsbn = self.get_summoner_by_name(summoner_name)

        if gsbn is not None and int(len(gsbn)) > 0 and 'puuid' in str(gsbn):
            gsbn = gsbn['puuid']

            gmbn = self.get_matches_by_name(gsbn)

            if gmbn is not None and int(len(gmbn)) > 0:
                gmbn = gmbn[0]
                return self.get_matches_by_matchid(gmbn)
        
        return None

#========================Game
class Game(commands.Cog):
    @slash_command(guild_ids=guild_ids, description="遊戲幫助指令。",
                      name="cmd",
                      help="顯示遊戲指令表",
                      pass_context=True)
    async def _cmd(self, ctx: commands.Context, param: str = None):
        if param is None:
            embed = discord.Embed(title="新世界 指令表",
                                  description="要查看幫助頁面，只需在/cmd命令後添加頁面編號。 例如：/cmd 3",
                                  color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            embed.add_field(name="第1頁：賭注",
                            value="德州撲克類遊戲中的博彩相關的指令。", inline=False)
            embed.add_field(name="第2頁：經濟", value="經濟系統相關的指令。",
                            inline=False)
            embed.add_field(name="第3頁：遊戲", value="不同紙牌遊戲的指令。", inline=False)
            embed.add_field(name="第4頁：無類別", value="沒有特定類別的指令。", inline=False)
            embed.set_footer(text="")
            await ctx.send(embed=embed)
            return

        if param.isdecimal():
            embed = discord.Embed(title=None, description=None, color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            if int(param) == 1:
                commands = bot.get_cog('Betting').get_commands()
                embed.title = "賭注 指令"
                embed.description = "要查看特定指令，請在/cmd命令之後輸入指令名稱。 例如：/cmd raise。"

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 2:
                commands = bot.get_cog('Economy').get_commands()
                embed.title = "經濟 指令"
                embed.description = "要查看特定指令，請在/cmd命令之後輸入指令名稱。 例如：/cmd bal。"

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 3:
                embed.title = "遊戲 指令"
                embed.description = "要查看幫助頁面，只需在/cmd命令後添加頁面編號。 例如：/cmd 3"
                embed.add_field(name="第5頁：德州撲克", value="德州撲克的指令。", inline=False)
                embed.add_field(name="Page 6: 大統領", value="大統領的指令。", inline=False)
                await ctx.send(embed=embed)
            elif int(param) == 4:
                embed.title = "未分類的指令"
                embed.description = "要查看特定指令，請在/cmd命令之後輸入指令名稱。 例如：/cmd raise。"

                for name in uncategorized:
                    command = hasCommandByName(name)
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 5:
                embed.title = "德州撲克指令"
                embed.description = "要查看特定指令，請在 /cmd 命令之後輸入命令名稱。 例如：/cmd rc。"
                commands = bot.get_cog('Poker').get_commands()

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 6:
                embed.title = "大統領指令"
                embed.description = "要查看特定指令，請在 /cmd 命令之後輸入命令名稱。 例如：/cmd rc。"
                commands = bot.get_cog('Pres').get_commands()

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)

        else:
            command = hasCommandByName(param)
            if command is None:
                return

            embed = discord.Embed(title=BOT_PREFIX + command.name, description=command.help, color=0x00ff00)
            embed.set_author(name="指令幫助")
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            await ctx.send(embed=embed)

    @slash_command(guild_ids=guild_ids, description="生成隨機卡。 可能會出現重複項。",
                      name="rc",
                    brief="生成隨機卡",
                    help="該命令從52張卡組中生成一張隨機卡。 格式為 /rc。 不需要任何參數。",
                    pass_context=True)
    async def rc(self, ctx: commands.Context):
        embed = discord.Embed(title="隨機卡", description="", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        selectCard = random.choice(cardChoices)
        selectSuit = random.choice(suits)

        if selectSuit == 'D':
            embed.description += "階磚"
        elif selectSuit == 'C':
            embed.description += "梅花"
        elif selectSuit == 'H':
            embed.description += "紅心"
        elif selectSuit == 'S':
            embed.description += "葵扇"

        if selectCard == 'A':
            embed.description += "A"
        elif selectCard == 'J':
            embed.description += "J"
        elif selectCard == 'Q':
            embed.description += "Q"
        elif selectCard == 'K':
            embed.description += "K"
        else:
            embed.description += selectCard

        #imgName = "deck/" + selectCard + selectSuit + ".png"
        embed.set_image(url=findFileName(selectSuit, selectCard))
        #file = discord.File(imgName, filename='card.png')
        embed.set_thumbnail(url="attachment://card.png")
        await ctx.send(embed=embed)


    '''@slash_command(guild_ids=guild_ids, description="從卡組中拉出許多隨機卡。",
                      name="draw",
                    brief="從牌組中抽出若干張牌",
                    help="從卡組中拉出一些指定的隨機卡。\n"
                         "該指令的格式為 $draw <卡數>.\n 卡數應在1到52之間（含1和52）。",
                    pass_context=True)
    async def draw(self, ctx: commands.Context, cards: int = 1):
        embed = discord.Embed(title="抽卡", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
        if cards > 52 or cards <= 0:
            embed.description = "您不能抽出此數量的卡。 提供一個介於1到52（含）之間的數字。"
            await ctx.send(embed=embed)
            return

        drawDeck = ["https://i.imgur.com/VBdPy26.png", "https://i.imgur.com/yGcued2.png", "https://i.imgur.com/5SR155z.png", "https://i.imgur.com/8M9EbWg.png", "https://i.imgur.com/aR5T1do.png", "https://i.imgur.com/A9Nyxwn.png", "https://i.imgur.com/pKv3o52.png",
                    "https://i.imgur.com/sEqDkMq.png", "https://i.imgur.com/rxaKhG4.png", "https://i.imgur.com/11yLhfD.png", "https://i.imgur.com/bq6lb5Z.png", "https://i.imgur.com/0Znul30.png", "https://i.imgur.com/md7LNs3.png", "https://i.imgur.com/GoyjsN6.png",
                    "https://i.imgur.com/J3sKcoF.png", "https://i.imgur.com/0F2KC0D.png", "https://i.imgur.com/KYWeqAC.png", "https://i.imgur.com/smLknK1.png", "https://i.imgur.com/F98Y3CA.png", "https://i.imgur.com/SS7SFsT.png", "https://i.imgur.com/NRQiCiJ.png",
                    "https://i.imgur.com/pTlYzW7.png", "https://i.imgur.com/v9iTjcX.png", "https://i.imgur.com/DiuE5ye.png", "https://i.imgur.com/ntwFoQr.png", "https://i.imgur.com/qSZoZT3.png", "https://i.imgur.com/mFdtL9O.png", "https://i.imgur.com/SsNG5L8.png",
                    "https://i.imgur.com/3qqBau2.png", "https://i.imgur.com/DrehITV.png", "https://i.imgur.com/LblY086.png", "https://i.imgur.com/hj27dUO.png", "https://i.imgur.com/43gwYkW.png", "https://i.imgur.com/2bMLCBW.png", "https://i.imgur.com/0lqLY4E.png",
                    "https://i.imgur.com/kQARj7b.png", "https://i.imgur.com/S3BUfV7.png", "https://i.imgur.com/PNGooTc.png", "https://i.imgur.com/8WhdL65.png", "https://i.imgur.com/PjxnGhg.png", "https://i.imgur.com/9cDlc0C.png", "https://i.imgur.com/4XM9H2y.png",
                    "https://i.imgur.com/y3NLpIF.png", "https://i.imgur.com/7o4C1LX.png", "https://i.imgur.com/zAr7vhg.png", "https://i.imgur.com/R4bYTZo.png", "https://i.imgur.com/N8qoXrl.png", "https://i.imgur.com/MJIoVsk.png", "https://i.imgur.com/WpL2pJI.png",
                    "https://i.imgur.com/bXFkuPH.png", "https://i.imgur.com/UQSjCzN.png", "https://i.imgur.com/vakonuH.png"]
        drawDeck = ["deck/AD.png", "deck/AC.png", "deck/AH.png", "deck/AS.png", "deck/2D.png", "deck/2C.png", "deck/2H.png",
                    "deck/2S.png", "deck/3D.png", "deck/3C.png", "deck/3H.png", "deck/3S.png",
                    "deck/4D.png", "deck/4C.png", "deck/4H.png", "deck/4S.png", "deck/5D.png", "deck/5C.png", "deck/5H.png",
                    "deck/5S.png", "deck/6D.png", "deck/6C.png", "deck/6H.png", "deck/6S.png",
                    "deck/7D.png", "deck/7C.png", "deck/7H.png", "deck/7S.png", "deck/8D.png", "deck/8C.png", "deck/8H.png",
                    "deck/8S.png", "deck/9D.png", "deck/9C.png", "deck/9H.png", "deck/9S.png",
                    "deck/10D.png", "deck/10C.png", "deck/10H.png",
                    "deck/10S.png", "deck/JD.png", "deck/JC.png", "deck/JH.png", "deck/JS.png", "deck/QD.png", "deck/QC.png",
                    "deck/QH.png", "deck/QS.png",
                    "deck/KD.png", "deck/KC.png", "deck/KH.png", "deck/KS.png"]

        dealtCards = []
        for i in range(0, cards):
            cardName = random.choice(drawDeck)
            drawDeck.remove(cardName)
            dealtCards.append(cardName)

        embed.description = "發了 " + str(cards) + "張牌。"
        file = showHand(ctx.author, dealtCards)
        embed.set_image(url="attachment://hand.png")
        await ctx.send(file=file, embed=embed)'''


    @slash_command(guild_ids=guild_ids, description="查看您的手。",
                      name="hand",
                    brief="查看你的手",
                    help="查看您手中的卡。 該機器人將為您PM包含您的手的圖像。 格式為 /hand，不帶任何參數。",
                    pass_context=True)
    async def hand(self, ctx: commands.Context):
        embed = discord.Embed(title=ctx.author.name + "'s Hand", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)

        if checkInGame(ctx.author):
            GAME = getGame(ctx.author)
            if GAME.gameUnderway:
                file = showHand(ctx.author, GAME.playerHands[str(ctx.author.id)])
                embed.set_image(url="attachment://hand.png")
                embed.add_field(name="Number of Cards", value=str(len(GAME.playerHands[str(ctx.author.id)])))
                await ctx.author.send(file=file, embed=embed)
            else:
                embed.description = "您的遊戲尚未開始。"
                await ctx.send(embed=embed)
        else:
            embed.description = "您不在遊戲中。"
            await ctx.send(embed=embed)


    @slash_command(guild_ids=guild_ids, description="Set sorting type. 'p' for (3 low, 2 high), 'd' for (A low, K high), 's' for (diamonds - spades).",
                      name="setsort",
                    brief="Set sorting type",
                    aliases=['ss'],
                    help="/setsort <sorttype>. 'p' for 3 lowest, 2 highest, 'd' for default, 's' for by suit.",
                    pass_context=True)
    async def setsort(self, ctx: commands.Context, sorttype: str = None):
        embed = discord.Embed(title="排序方式", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
        embed.add_field(name="大統領-樣式 (p)", value="3 - K, A, 2", inline=False)
        embed.add_field(name="默認 (d)", value="A - K", inline=False)
        embed.add_field(name="Suits (s)", value="Ace of Diamonds - King of Spades", inline=False)

        global order, presOrder, ORDER

        if sorttype is None:
            embed.description = "沒有提供排序類型。"
            await ctx.send(embed=embed)
            return

        if sorttype == "d":
            embed.description = "排序類型設置為默認(d)。"
            ORDER = order
            DBConnection.updateUserSortPref(str(ctx.author.id), sorttype)
        elif sorttype == "p":
            embed.description = "排序類型設置為“大統領-樣式(p)”。"
            ORDER = presOrder
            DBConnection.updateUserSortPref(str(ctx.author.id), sorttype)
        elif sorttype == "s":
            embed.description = "排序類型設置為 Suits-Style."
            ORDER = suitOrder
            DBConnection.updateUserSortPref(str(ctx.author.id), sorttype)
        else:
            embed.description = "Try 'd', 'p', or 's'."

        await ctx.send(embed=embed)


    @slash_command(guild_ids=guild_ids, description="開始遊戲。",
                      name="game",
                    brief="開始遊戲",
                    aliases=['5card'],
                    help="使用此命令開始新遊戲。 您只能在遊戲之外使用此命令。 格式為 /game，不帶參數。",
                    pass_context=True)
    async def game(self, ctx: commands.Context):
        global gameList

        channelGame = getGameByChannel(ctx.channel)
        if channelGame is not None:
            embed = discord.Embed(title='德州撲克', description="該頻道已經有一個活躍的遊戲。", color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name="遊戲編號", value=str(channelGame.id))
            embed.set_footer(text="使用 /in <遊戲編號> 加入遊戲。")
            await ctx.respond(embed=embed)
            return

        if checkInGame(ctx.author):
            embed = discord.Embed(title='德州撲克', description="您已經在玩遊戲。", color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            await ctx.respond(embed=embed)
            return

        await ctx.defer()

        emoji1 = '1️⃣'
        #emoji2 = '2️⃣'
        embed = discord.Embed(title="遊戲選擇", description="通過使用給定的表情符號對此消息做出反應來選擇遊戲類型。", color=0x00ff00)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
        embed.add_field(name="德州撲克", value=emoji1)
        #embed.add_field(name="大統領", value=emoji2)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(emoji1)
        #await msg.add_reaction(emoji2)
        rxn = None

        def check(reaction, user):
            global rxn
            rxn = reaction
            return not user.bot

        try:
            rxn = await bot.wait_for('reaction_add', timeout=50.0, check=check)
        except asyncio.TimeoutError:
            await ctx.respond(embed=discord.Embed(title="遊戲選擇", description="沒有人及時選擇...", color=0x00ff00))
            return
        else:
            if str(rxn[0].emoji) == emoji1:
                id = randrange(100000, 1000000)
                while hasGame(id):
                    id = randrange(100000, 1000000)
                GAME = TexasHoldEm(ctx.channel, id)
                gameList.append(GAME)
                embed = discord.Embed(title="創建遊戲", description="創建了德州撲克遊戲。", color=0x00ff00)
                embed.add_field(name="遊戲編號", value=str(id))
                embed.add_field(name="加入", value="/in " + str(id))
                embed.set_thumbnail(url=GAME.imageUrl)
                await msg.delete()
                await ctx.send_followup(embed=embed)
            '''elif str(rxn[0].emoji) == emoji2:
                id = randrange(100000, 1000000)
                while hasGame(id):
                    id = randrange(100000, 1000000)
                GAME = President(ctx.channel, id)
                gameList.append(GAME)
                embed = discord.Embed(title="創建遊戲", description="創建了大統領遊戲。", color=0x00ff00)
                embed.add_field(name="遊戲編號", value=str(id))
                embed.add_field(name="加入", value="/in " + str(id))
                embed.set_thumbnail(url=GAME.imageUrl)
                await ctx.send(embed=embed)'''


    @slash_command(guild_ids=guild_ids, description="使用6位數字id參加遊戲。",
                      name="in",
                    brief="加入遊戲。",
                    help="使用其6位數字id加入現有遊戲。 此命令的格式為 /in <6位數id>。",
                    pass_context=True)
    async def _in(self, ctx: commands.Context, id: int = None):
        embed = discord.Embed(title='德州撲克', description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)

        if checkInGame(ctx.author):
            embed.description = "您已經在玩遊戲。"
            await ctx.respond(embed=embed)
            return

        if id is None:
            embed.description = "您未提供6位數字的遊戲id。"
            await ctx.respond(embed=embed)
            return

        if not hasGame(id):
            embed.description = "無效的遊戲id。"
            await ctx.respond(embed=embed)
            return

        if not channelCheck(getGameByid(id), ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.respond(embed=embed)
            return

        GAME = getGameByid(id)

        if GAME.gameUnderway:
            embed.description = "這場比賽已經在進行中。 您現在不能加入。"
            embed.add_field(name="遊戲編號", value=GAME.ID)
            await ctx.respond(embed=embed)
            return

        GAME.players.append(str(ctx.author.id))
        embed.description = "您加入了遊戲。"

        playerList = ""
        for playerid in GAME.players:
            user = bot.get_user(int(playerid))
            playerList += user.name + "\n"

        embed.add_field(name="玩家們", value=playerList)
        embed.add_field(name="遊戲編號", value=GAME.ID)
        embed.set_thumbnail(url=GAME.imageUrl)
        await ctx.respond(embed=embed)


    @slash_command(guild_ids=guild_ids, description="離開遊戲，如果遊戲已經在進行中，則放棄任何下注。",
                      name="out",
                    brief="離開您加入的遊戲，如果該遊戲已經在進行中，則放棄任何下注",
                    help="留下您與眾不同的遊戲，從而放棄您已經進行的任何下注。 格式為 /out，不帶任何參數。",
                    pass_context=True)
    async def out(self, ctx: commands.Context):
        embed = discord.Embed(title='德州撲克', description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
        if not checkInGame(ctx.author):
            embed.description = "您不在遊戲中。"
            await ctx.respond(embed=embed)
            return

        GAME = getGame(ctx.author)
        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.respond(embed=embed)
            return

        GAME.playerStatus[str(ctx.author.id)] = "Fold"
        GAME.players.remove(str(ctx.author.id))

        embed.description = "您離開了遊戲。"
        embed.add_field(name="遊戲編號", value=str(GAME.ID))
        embed.set_thumbnail(url=GAME.imageUrl)
        await ctx.respond(embed=embed)


    @slash_command(guild_ids=guild_ids, description="開始遊戲。",
                      name="start",
                    brief="開始遊戲",
                    help="如果您還沒有開始遊戲，請先開始。 格式為 /start，不帶任何參數。",
                    pass_context=True)
    async def start(self, ctx: commands.Context):
        embed = discord.Embed(title='德州撲克', description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
        if not checkInGame(ctx.author):
            embed.description = "您不在遊戲中。"
            await ctx.respond(embed=embed)
            return

        GAME = getGame(ctx.author)
        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.respond(embed=embed)
            return

        if GAME.gameUnderway:
            embed.description = "您的遊戲已經開始。"
            embed.add_field(name="遊戲編號", value=str(GAME.ID))
            embed.set_thumbnail(url=GAME.imageUrl)
            await ctx.respond(embed=embed)
            return

        if len(GAME.players) == 1:
            embed.description = "你不能一個人玩！"
            await ctx.respond(embed=embed)
            return
        await ctx.respond('開始中...')
        await GAME.startGame()


    @slash_command(guild_ids=guild_ids, description="使用十六進制代碼為您的手設置自定義顏色。",
                      name="setcolor",
                    brief="為您的手設置自定義顏色",
                    aliases=['sc', 'setColour'],
                    help="為顯示您的手的圖像設置自定義顏色。 需要格式為＃123ABC的有效顏色十六進制代碼。 格式為 /setcolor <十六進制代碼>。",
                    pass_context=True)
    async def setcolor(self, ctx: commands.Context, colour: str):
        embed = discord.Embed(title="自定義顏色", description=None, color=0x00ff00)
        embed.set_thumbnail(url="https://i.imgur.com/FCCMHHi.png")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', colour)
        if not match:
            embed.description="無效的顏色十六進制代碼。"
            await ctx.send(embed=embed)
            return

        DBConnection.updateUserHandColor(str(ctx.author.id), colour)

        embed.colour = int(colour[1:], 16)
        embed.description = "自定義顏色設置。"
        embed.add_field(name="顏色", value="<-----")

        await ctx.send(embed=embed)

@loop(seconds=1)
async def gameLoop():
    for GAME in gameList:
        await GAME.gameLoop()

#========================Music========================
# Silence useless bug reports messages
yt_dlp.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass

class OpError(Exception):
    pass

class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'yesplaylist': True,
        'flat_playlist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'cachedir': False,
        'verbose': True
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        sourceList = []
        if 'entries' not in processed_info:
            try:
                info = processed_info
                sourceList.append(cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info))
            except Exception as e:
                timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
                BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                await BDS_Log_Channel.send('{}\n\nError occured in if \'entries\' not in processed_info\n{}'.format(e,timestamp))
        else:
            info = None
            while info is None:
                for pie in processed_info['entries']:
                    try:
                        info = processed_info['entries'].pop(0)
                        sourceList.append(cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info))
                    except Exception as e:
                        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
                        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                        await BDS_Log_Channel.send('{}\n\nError occured in for pie in processed_info[\'entries\']\n{}'.format(e,timestamp))
                    #except IndexError:
                        #raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return sourceList

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} 日'.format(days))
        if hours > 0:
            duration.append('{} 小時'.format(hours))
        if minutes > 0:
            duration.append('{} 分'.format(minutes))
        if seconds > 0:
            duration.append('{} 秒'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='正在播放',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='時間', value=self.source.duration)
                 .add_field(name='要求者', value=self.requester.mention)
                 .add_field(name='上載者', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='網址', value='[點擊]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.prevmsg = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.tempSource = None

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                #async with timeout(1800):  # 3 minutes
                    self.current = await self.songs.get()
                except Exception as e:#asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    print(e)
                    return

                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)

            elif self.loop == True:
                #try:
                #async with timeout(60):
                await self.songs.put(self.current)
                self.current = await self.songs.get()
                #except asyncio.TimeoutError:
                #self.bot.loop.create_task(self.stop())
                #return

                self.tempSource = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS))

                self.tempSource.volume = self._volume
                self.voice.play(self.tempSource, after=self.play_next_song)

            try:
                if self.prevmsg is not None:
                    await self.prevmsg.delete()
            except Exception as e:
                log_channel = bot.get_channel(809527650955296848)
                await log_channel.send(e)

            self.prevmsg = await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        self.prevmsg = None

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('該命令不能在私訊中使用.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('發生錯誤: {}'.format(str(error)))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client

        if voice_state is not None and len(voice_state.channel.members) == 1 or member == bot.user and after.channel is None:
            # You should also check if the song is still playing
            try:
                await voice_state.disconnect()
                '''for task in asyncio.Task.all_tasks(bot.loop):
                    await task.cancel()'''
                #self.voice_states.get(member.guild.id).audio_player.cancel()
                del self.voice_states[member.guild.id]
            except:
                pass
        else:
            return

    @slash_command(guild_ids=guild_ids, name='join', aliases=['j'], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """我要進來了。"""
        
        await ctx.defer()

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.respond(':thumbsup:')
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.send_followup(':thumbsup:')

    @slash_command(guild_ids=guild_ids, name='join2', aliases=['j2'], invoke_without_subcommand=True)
    @commands.has_any_role('Ben AI')
    async def _join2(self, ctx: commands.Context):
        """我要進來了。"""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @slash_command(guild_ids=guild_ids, name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """召喚我去某個語音頻道。
        如果無講明邊個語音頻道，我要進來了。
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('您既未連接到語音通道，也未指定要加入的通道。')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.respond(':thumbsup:')
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.respond(':thumbsup:')

    @slash_command(guild_ids=guild_ids, name='leave', aliases=['disconnect'])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """清除曲列、解除循環播放，離開語音頻道。"""

        if not ctx.voice_state.voice:
            return await ctx.respond('未連接到任何語音通道。')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]
        await ctx.respond(':middle_finger:')

    @slash_command(guild_ids=guild_ids, name='volume', aliases=['v'])
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """較大細聲。"""

        if not ctx.voice_state.is_playing:
            return await ctx.respond('目前沒有任何播放。')

        if 0 > volume > 100:
            return await ctx.respond('音量必須在0到100之間')

        ctx.voice_state.volume = volume / 100
        await ctx.respond('播放器音量設置為 {}%'.format(volume))

    @slash_command(guild_ids=guild_ids, name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """顯示目前播緊嘅歌。"""

        await ctx.respond(embed=ctx.voice_state.current.create_embed())

    @slash_command(guild_ids=guild_ids, name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """暫停目前播緊嘅歌。"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.respond('⏯')

    @slash_command(guild_ids=guild_ids, name='resume', aliases=['r'])
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """恢復目前播緊嘅歌。"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.respond('⏯')

    @slash_command(guild_ids=guild_ids, name='stop', aliases=['st'])
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """停止播放並清除曲列。"""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.respond('⏹')

    @slash_command(guild_ids=guild_ids, name='skip', aliases=['s'])
    async def _skip(self, ctx: commands.Context):
        """跳過一首歌。 請求者可以自動跳過。
        要跳過該歌曲，需要3個跳過票。
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('依家冇嘢播緊...')
        '''
        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)
        
            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('已增加跳過投票，目前位於 **{}/3**'.format(total_votes))
        
        else:
            await ctx.send('您已經投票跳過這首歌。')
        '''
        await ctx.respond('⏭')
        ctx.voice_state.skip()
    @slash_command(guild_ids=guild_ids, name='queue', aliases=['q'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """顯示曲列。
        您可以選擇指定要顯示的頁面。 每頁包含10個曲目。
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('曲列有堆空氣。')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} 首曲目:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='頁數 {}/{}'.format(page, pages)))
        await ctx.respond(embed=embed)

    @slash_command(guild_ids=guild_ids, name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """洗牌曲列。"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('曲列有堆空氣。')

        ctx.voice_state.songs.shuffle()
        await ctx.respond('✅')

    @slash_command(guild_ids=guild_ids, name='remove', aliases=['rm'])
    async def _remove(self, ctx: commands.Context, index: int):
        """從曲列中刪除指定索引嘅歌曲。"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('曲列有堆空氣。')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.respond('✅')

    @slash_command(guild_ids=guild_ids, name='loop', aliases=['l'])
    async def _loop(self, ctx: commands.Context):
        """循環播放目前播放的歌曲。
        再次使用此指令以解除循環播放。
        """

        if not ctx.voice_state.is_playing:
            return await ctx.respond('空白一片。')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop:
            await ctx.respond('✅')
        elif not ctx.voice_state.loop:
            await ctx.respond('❎')

    @slash_command(guild_ids=guild_ids, name='play', aliases=['p'])
    async def _play(self, ctx: commands.Context, *, search: str):
        """播放歌曲。
        如果隊列中有歌曲，它將一直排隊，直到其他歌曲播放完畢。
        如果未提供URL，此指令將自動從各個站點搜索。
        個站點的列表可以喺呢到揾到：https://rg3.github.io/youtube-dl/supportedsites.html
        """

        #ctx.voice_stats.voice --> ctx.voice_client
        #ctx.invoke --> commands.Context.invoke, 'cmd name' | (original) | ctx
        await ctx.defer()

        if not ctx.voice_client:
            await commands.Context.invoke('join2', self._join2, ctx)

        async with ctx.typing():
            try:
                sourceList = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            #except YTDLError as e:
            except Exception as e:
                timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
                BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                await BDS_Log_Channel.send('{}\n\nError occured in YTDLSource.create_source\n{}'.format(e,timestamp))
                #await ctx.send_followup('處理此請求時發生錯誤: {}'.format(str(e)))
            
            for source in sourceList:
                try:
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send_followup('加咗首 {}'.format(str(source)))
                except Exception as e:
                    BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                    await BDS_Log_Channel.send('{}\n\nError occured in for source in sourceList\n{}'.format(e,timestamp))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

#========================General========================
dmList = [254517813417476097,525298794653548751,562972196880777226,199877205071888384,407481608560574464,346518519015407626,349924747686969344,270781455678832641,363347146080256001,272977239014899713,262267347379683329,394354007650336769,372395366986940416,269394999890673664]

@loop(minutes=10)
async def twLolLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    #try:
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

    summonerNames = DBConnection.getLolSummonerNames(getRegion('tw'))
    print(summonerNames)
    if summonerNames is None or int(len(summonerNames)) == 0:
        print(str(summonerNames)+' is None or len = 0')
        return

    for summonerName in summonerNames:
        print(summonerNames)
        summonerName = str(summonerName[0])

        print(summonerName)

        url_construct = "https://twlolstats.com/summoner/?summoner={}".format(summonerName)
        url = Request(url_construct, headers=hdr)
        html_page = urlopen(url)
        soup = BeautifulSoup(html_page, "lxml")

        for title in soup.findAll("input", class_="loadMore btn btn-primary"):
            uuid = str(title).split(',',1)[1].split(', \'',1)[1].split('\'',1)[0]
            break

        for content in soup.findAll("div", class_="col-sm-6"):
            soup_section = BeautifulSoup(str(content), "lxml")
            for section in soup_section.findAll("div"):
                if '<div>Level ' in str(section):
                    summonerLevel = str(section).split('<div>Level ')[1].split('</div>')[0]
                    break
        print(uuid)
        url = Request("https://twlolstats.com/moreGames/{}/game1".format(uuid), headers=hdr)
        html_page = urlopen(url)
        soup = BeautifulSoup(html_page, "lxml")

        gameMode = ''
        dt = ''
        gameDuration = ''

        for content in soup.findAll("tr"):

            soup_section = BeautifulSoup(str(content), "lxml")
            for section in soup_section.findAll("img"):
                thumbnail = str(section).split('\"',1)[1].split('\\"',1)[0]
                break

            for section in soup_section.findAll("b"):
                title = str(section).split('>',1)[1].split('<',1)[0].encode('utf-8').decode('unicode_escape')
                break
            
            for section in soup_section.findAll("div"):
                if section is not None and str(section) != '' and str(section) != ' ' and '<' in str(section) and '>' in str(section):
                    tempSection = str(section).split('>',1)[1].split('<',1)[0]

                if '/' in tempSection and dt == '':
                    dt = tempSection
                elif 'min' in tempSection and 's' in tempSection and gameDuration == '':
                    gameDuration = tempSection
                elif '\\' not in tempSection and gameMode == '':
                    gameMode = tempSection

            count = 0
            for section in soup_section.findAll("span"):
                if section is not None and str(section) != '' and str(section) != ' ' and '<' in str(section) and '>' in str(section):
                    tempSection = str(section).split('>',1)[1].split('<',1)[0]
                
                if tempSection != '/':
                    if count == 0:
                        kills = tempSection
                    elif count == 1:
                        deaths = tempSection
                    elif count == 2:
                        assists = tempSection

                    count += 1

            break

        #DB operations
        if ' ' in gameDuration:
            dt_gD = gameDuration.replace(' ','')
        if 'min' in gameDuration:
            dt_gD = gameDuration.replace('min','')
        if 's' in gameDuration:
            dt_gD = gameDuration.replace('s','')
        dt_duration = '{}{}{}{}{}{}'.format(gameMode, dt, dt_gD, kills, deaths, assists) #format for unique id
        dt_duration_30 = dt_duration[:min(len(dt_duration), 30)] #limit length to 30 char
        dt_db = DBConnection.getLolPublishedAt(getRegion('tw'), summonerName)[0][0]
        if str(dt_duration_30) != str(dt_db):
            DBConnection.updateLolPublishedAt(getRegion('tw'), dt_duration_30, summonerName)
            print('else with {}'.format(summonerName))

            color = 0x000000
            print('title: '+str(title))
            print('title sumName: '+str(summonerName))
            if '勝利' in str(title):
                color = 0x00ff00
            else:
                color = 0xff0000

            title = title.format('{} {}'.format(summonerName, title))
            url = url_construct
            championName = thumbnail.split('champion/')[1].split('.')[0]

            #embed construct
            embed = discord.Embed()
            embed.title = title
            embed.color = color
            embed.url = url
            #embed.description = desc
            embed.set_author(name='League of Legends (TW)', icon_url='https://i.imgur.com/tkjOxrX.png')
            embed.set_thumbnail(url=thumbnail)

            embed.add_field(name="召喚師等級", value='{}'.format(summonerLevel), inline=True)
            embed.add_field(name="英雄名字", value='{}'.format(championName), inline=True)
            #embed.add_field(name="獲得金幣", value='{}'.format(goldEarned), inline=True)

            embed.add_field(name="遊戲時長", value='{} 分鐘'.format(gameDuration), inline=True)
            embed.add_field(name="遊戲模式", value='{}'.format(gameMode), inline=True)
            #embed.add_field(name="遊戲類型", value='{}'.format(gameType), inline=True)

            embed.add_field(name="擊殺", value='{}'.format(kills), inline=True)
            embed.add_field(name="死亡", value='{}'.format(deaths), inline=True)
            embed.add_field(name="助攻", value='{}'.format(assists), inline=True)

            #embed.add_field(name="雙殺", value='{}'.format(doubleKills), inline=True)
            #embed.add_field(name="三連殺", value='{}'.format(tripleKills), inline=True)
            #embed.add_field(name="四連殺", value='{}'.format(quadraKills), inline=True)
            #embed.add_field(name="五連殺", value='{}'.format(pentaKills), inline=True)

            embed.set_footer(text=dt)

            #BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
            BLG_ST_Channel = bot.get_channel(815568098001813555) #BrianLee Server - satellie
            #BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

            #await BDS_PD_Channel.send(embed=embed)
            #await BLG_ST_Channel.send(embed=embed)
            print('end with {}'.format(summonerName))
            #await BMS_OT_Channel.send(embed=embed)

    #except Exception as e:
        #BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
        #await BDS_Log_Channel.send('{}\n\nError occured in twLolLoop\n{}'.format(e,timestamp))

@loop(minutes=10)
async def naLolLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:

        count = 0
        #totalcount = 0
        summonerNames = DBConnection.getLolSummonerNames(getRegion('na'))

        load_dotenv()
        riotApi = RiotApi(os.getenv('RIOT_API_KEY'))

        for summonerName in summonerNames:
            if count == 20:
                asyncio.sleep(1)
                count = 0
                #totalcount += count

            count += 1
            summonerName = str(summonerName[0])
            match = riotApi.get_latest_matches_by_name(summonerName)

            if match is None:
                BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                await BDS_Log_Channel.send('{}\n\nError occured in lolloop summoner: {} possibly not found\n'.format(timestamp, summonerName))
                continue

            matchId = match['metadata']['matchId']

            #DB operations
            dt_db = DBConnection.getLolPublishedAt(getRegion('na'), summonerName)[0][0]
            if str(matchId) == str(dt_db):
                continue
            else:
                DBConnection.updateLolPublishedAt(getRegion('na'), matchId, summonerName)

                gameDuration = match['info']['gameDuration']
                gameMode = match['info']['gameMode']
                gameType = match['info']['gameType']
                gameStartTimestamp = match['info']['gameStartTimestamp']

                for participant in match['info']['participants']:

                    #if a list of participant names...
                    if participant['summonerName'] == summonerName:
                        #general
                        summonerLevel = participant['summonerLevel']
                        championName = participant['championName']
                        win = participant['win']

                        #economy
                        goldEarned = participant['goldEarned']
                        goldSpent = participant['goldSpent']

                        #KDA
                        kills = participant['kills']
                        deaths = participant['deaths']
                        assists = participant['assists']

                        #double triple quadra penta kill
                        doubleKills = participant['doubleKills']
                        tripleKills = participant['tripleKills']
                        quadraKills = participant['quadraKills']
                        pentaKills = participant['pentaKills']

                        break

                title = str(summonerName)
                color = 0x000000
                if win is True:
                    title += ' 勝利'
                    color = 0x00ff00
                else:
                    title += ' 失敗'
                    color = 0xff0000

                summonerNameFormat = summonerName.replace(' ', '%20')
                url = 'https://na.op.gg/summoner/userName={}'.format(summonerNameFormat)
                thumbnail = 'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{}_0.jpg'.format(championName)
                dt = str(datetime.utcfromtimestamp(int(gameStartTimestamp)/1000).strftime('%Y-%m-%d %H:%M:%S'))

                #embed construct
                embed = discord.Embed()
                embed.title = title
                embed.color = color
                embed.url = url
                #embed.description = desc
                embed.set_author(name='League of Legends (NA)', icon_url='https://i.imgur.com/tkjOxrX.png')
                embed.set_thumbnail(url=thumbnail)

                embed.add_field(name="召喚師等級", value='{}'.format(summonerLevel), inline=True)
                embed.add_field(name="英雄名字", value='{}'.format(championName), inline=True)
                embed.add_field(name="獲得金幣", value='{}'.format(goldEarned), inline=True)

                embed.add_field(name="遊戲時長", value='{} 分鐘'.format(int(gameDuration)/60), inline=True)
                embed.add_field(name="遊戲模式", value='{}'.format(gameMode), inline=True)
                embed.add_field(name="遊戲類型", value='{}'.format(gameType), inline=True)

                embed.add_field(name="擊殺", value='{}'.format(kills), inline=True)
                embed.add_field(name="死亡", value='{}'.format(deaths), inline=True)
                embed.add_field(name="助攻", value='{}'.format(assists), inline=True)

                embed.add_field(name="雙殺", value='{}'.format(doubleKills), inline=True)
                embed.add_field(name="三連殺", value='{}'.format(tripleKills), inline=True)
                embed.add_field(name="四連殺", value='{}'.format(quadraKills), inline=True)
                embed.add_field(name="五連殺", value='{}'.format(pentaKills), inline=True)

                embed.set_footer(text=dt)

                #BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
                BLG_ST_Channel = bot.get_channel(815568098001813555) #BrianLee Server - satellie
                #BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

                #await BDS_PD_Channel.send(embed=embed)
                await BLG_ST_Channel.send(embed=embed)
                #await BMS_OT_Channel.send(embed=embed)

                '''print('\n\n')
                print('matchId: {}\ngameDuration: {}\ngameMode: {}\ngameType: {}\n \
                    summonerLevel: {}\nchampionName: {}\nwin: {}\n \
                    goldEarned: {}\ngoldSpent: {}\n \
                    kills: {}\ndeaths: {}\nassists: {}\n \
                    doubleKills: {}\ntripleKills: {}\nquardraKills: {}\npentaKills: {}'.format(matchId, gameDuration, gameMode, gameType, summonerLevel, championName, win, goldEarned, goldSpent, kills, deaths, assists, doubleKills, tripleKills, quadraKills, pentaKills))'''
    except Exception as e:
        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
        await BDS_Log_Channel.send('{}\n\nError occured in naLolLoop\n{}'.format(e,timestamp))

@loop(minutes=15)
async def hypebeastLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

        url = Request("https://hypebeast.com/zh/latest", headers=hdr)
        html_page = urlopen(url)
        soup = BeautifulSoup(html_page, "lxml")

        text = '' #game title
        link = '' #game url
        img = '' #image url
        desc = '' #game desc
        dt = '' #posted dt
        for title in soup.findAll("div", class_="post-box"):
            if "post-box sticky-post" in str(title):
                continue

            soup_section = BeautifulSoup(str(title), "lxml")

            for section in soup_section.findAll("time", class_="timeago"):
                dt = str(section).split('datetime=\"')[1].split('\">',1)[0]
                break
            dt_db = DBConnection.getPublishedAt('hypebeast')[0][0]
            if str(dt) == str(dt_db):
                return
            else:
                DBConnection.updatePublishedAt(dt, 'hypebeast')

                for section in soup_section.findAll("a", class_="title"):
                    title = str(section)
                    link = title.split('href=\"')[1].split('\"')[0]
                    text = title.split('title=\"')[1].split('\"')[0].strip()
                    break

                for section in soup_section.findAll("div", class_="post-box-content-excerpt"):
                    desc = str(section).split('\">',1)[1].split('</',1)[0].strip()
                    break

                for section in soup_section.findAll("img", class_="img-fluid lazy-load"):
                    img_text = str(section).split('alt=\"',1)[1].split('\"')[0].strip()
                    if text == img_text:
                        img = str(section).split('data-srcset=\"',1)[1].split(' 1x',1)[0]
                        break

                #embed construct
                embed = discord.Embed()
                embed.title = text
                embed.description = desc
                embed.set_author(name='Hypebeast', icon_url='https://i.imgur.com/9IvVe1D.png')
                embed.set_thumbnail(url=img)
                embed.set_footer(text=dt)

                #url handlings
                url = link
                if url is not None and 'http' in url and '://' in url:
                    url2 = url.rsplit('/',1)[1]
                    url1 = url.rsplit('/',1)[0]
                    if url2 is not None and url2 != '' and not url2.isalnum():
                        url2 = quote(url2)
                        url = url1 +'/'+ url2
                    embed.url = url

                BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
                BLG_ST_Channel = bot.get_channel(815568098001813555) #BrianLee Server - satellie
                BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

                await BDS_PD_Channel.send(embed=embed)
                await BLG_ST_Channel.send(embed=embed)
                await BMS_OT_Channel.send(embed=embed)

            break
    except Exception as e:
        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
        await BDS_Log_Channel.send('{}\n\nError occured in hypebeastLoop\n{}'.format(e,timestamp))

@loop(hours=1)
async def gamesLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

        url = Request("https://www.indiegamebundles.com/category/free/", headers=hdr)
        html_page = urlopen(url)
        soup = BeautifulSoup(html_page, "lxml")

        text = '' #game title
        link = '' #game url
        desc = '' #game desc
        dt = '' #posted dt
        img = '' #image url

        for title in soup.findAll("div", class_="td-module-container"):
            soup_section = BeautifulSoup(str(title), "lxml")

            for section in soup_section.findAll("div", class_="td-module-thumb"):
                soup_section = BeautifulSoup(str(section), "lxml")

                for section in soup_section.findAll("span", class_="entry-thumb td-thumb-css rocket-lazyload"):
                    img = str(section).split('data-bg=\"')[1].split('\"',1)[0]
                    break
            
                break
            break


        for title in soup.findAll("div", class_="td-module-meta-info"):
            soup_section = BeautifulSoup(str(title), "lxml")

            for section in soup_section.findAll("time", class_="entry-date updated td-module-date"):
                dt = str(section).split('datetime=\"')[1].split('\">',1)[0]
                #print(dt+'\n') #text_30 = text[:min(len(text), 30)]
                break
            dt_db = DBConnection.getPublishedAt('indiegamebundles')[0][0]
            if str(dt) == str(dt_db):
                return
            else:
                DBConnection.updatePublishedAt(dt, 'indiegamebundles')
                #continue else

                for section in soup_section.findAll("h3", class_="entry-title td-module-title"):
                    title = str(section)
                    link = title.split('<a href=\"')[1].split('\" rel=\"bookmark\" title=\"')[0]
                    text = title.split('<a href=\"')[1].split('\" rel=\"bookmark\" title=\"')[1].split('</a></h3>')[0].split('\">')[0]
                    break

                for section in soup_section.findAll("div", class_="td-excerpt"):
                    desc = str(section).split('\">',1)[1].split('</',1)[0]
                    break

                #embed construct
                embed = discord.Embed()
                embed.title = text
                embed.color = 0xb50024
                embed.description = desc
                embed.set_author(name='Indie Game Bundles', icon_url='https://i.imgur.com/RWIVDRN.png')
                embed.set_thumbnail(url=img)
                embed.set_footer(text=dt)

                #url handlings
                url = link
                if url is not None and 'http' in url and '://' in url:
                    url2 = url.rsplit('/',1)[1]
                    url1 = url.rsplit('/',1)[0]
                    if url2 is not None and url2 != '' and not url2.isalnum():
                        url2 = quote(url2)
                        url = url1 +'/'+ url2
                    embed.url = url

                BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
                BLG_ST_Channel = bot.get_channel(815568098001813555) #BrianLee Server - satellie
                BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

                await BDS_PD_Channel.send(embed=embed)
                await BLG_ST_Channel.send(embed=embed)
                await BMS_OT_Channel.send(embed=embed)

            break
    except Exception as e:
        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
        await BDS_Log_Channel.send('{}\n\nError occured in gamesLoop\n{}'.format(e,timestamp))

@loop(hours=1)
async def newsLoop():
    newsList = ['Rthk.hk', 'Bloomberg', 'IGN']
    for newsId in newsList:
        embed = await getNewsEmbed(newsId)
        if embed is not None:
            BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
            BLG_ST_Channel = bot.get_channel(815568098001813555) #BrianLee Server - satellie
            BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

            await BDS_PD_Channel.send(embed=embed)
            await BLG_ST_Channel.send(embed=embed)
            await BMS_OT_Channel.send(embed=embed)

@loop(minutes=15)
async def covLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:
        #api / json
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
        #api = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fbuilding_list_chi.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%2C%22sorts%22%3A%5B%5B4%2C%22desc%22%5D%5D%7D"
        api = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fenhanced_sur_covid_19_chi.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%2C%22sorts%22%3A%5B%5B1%2C%22desc%22%5D%5D%2C%22filters%22%3A%5B%5B2%2C%22ct%22%2C%5B%222022%22%5D%5D%5D%7D"
        url = Request(api, headers=hdr)
        data_json = json.loads(urlopen(url).read())
        data = max(data_json, key=lambda ev: ev['個案編號'])

        caseNo = data['個案編號']
        reportedDate = data['報告日期']
        onsetDate = data['發病日期']
        sex = data['性別']
        age = data['年齡']
        hospital = data['入住醫院名稱']
        humanStatus = data['住院/出院/死亡']
        local = data['香港/非香港居民']
        category = data['分類*']
        caseStatus = data['個案狀況*']
        #print('{} {} {} {} {} {} {} {} {} {}'.format(caseNo, reportedDate, onsetDate, sex, age, hospital, humanStatus, local, category, caseStatus))

        #db
        db_case_no = DBConnection.getCaseNo()[0][0]

        if int(caseNo) == int(db_case_no):
            return
        else:
            DBConnection.updateCaseNo(caseNo)

            embed = discord.Embed(title='2019冠狀病毒病的本地最新情況', url='https://data.gov.hk/tc-data/dataset/hk-dh-chpsebcddr-novel-infectious-agent/resource/f350a865-03a0-4b82-b3ce-2b7d3a817688')
            embed.color = 0x00c1ae
            embed.set_author(name='data.gov.hk', icon_url='https://i.imgur.com/64ivaYA.png')
            embed.set_thumbnail(url='https://i.imgur.com/CrepYT5.png')

            if hospital is not None and hospital != "":
                embed.description = '入住醫院名稱: {}'.format(hospital)

            embed.add_field(name="個案編號	", value=caseNo, inline=True)
            embed.add_field(name="報告日期", value=reportedDate, inline=True)
            embed.add_field(name="發病日期", value=onsetDate, inline=True)

            embed.add_field(name="性別", value=sex, inline=True)
            embed.add_field(name="年齡", value=age, inline=True)
            embed.add_field(name="住院/出院/死亡", value=humanStatus, inline=True)

            embed.add_field(name="香港/非香港居民", value=local, inline=True)
            embed.add_field(name="分類*", value=category, inline=True)
            embed.add_field(name="個案狀況*", value=caseStatus, inline=True)
            
            embed.set_footer(text='{}'.format(timestamp))

            BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
            BLG_ST_Channel = bot.get_channel(815568098001813555) #BrianLee Server - satellie
            BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

            #Google Map
            '''try:
                lat, lon = getLatLonByAddress('{},+{}'.format(district,building))
                image = getMapsImageByLatLon(lat, lon, 18)

                with BytesIO() as img:
                    image.save(img, 'PNG')
                    img.seek(0)
                    imgfile = discord.File(fp=img, filename='gMapLocation.png')
                await BDS_PD_Channel.send(embed=embed, file=imgfile)

                with BytesIO() as img:
                    image.save(img, 'PNG')
                    img.seek(0)
                    imgfile = discord.File(fp=img, filename='gMapLocation.png')
                await BLG_ST_Channel.send(embed=embed, file=imgfile)

                with BytesIO() as img:
                    image.save(img, 'PNG')
                    img.seek(0)
                    imgfile = discord.File(fp=img, filename='gMapLocation.png')
                await BMS_OT_Channel.send(embed=embed, file=imgfile)
            except Exception as e:
                BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                await BDS_Log_Channel.send('{}\n\nError occured in covLoop Google Map, switched to normal embed\n{}'.format(e,timestamp))
                await BDS_PD_Channel.send(embed=embed)
                await BLG_ST_Channel.send(embed=embed)
                await BMS_OT_Channel.send(embed=embed)'''

            await BDS_PD_Channel.send(embed=embed)
            await BLG_ST_Channel.send(embed=embed)
            await BMS_OT_Channel.send(embed=embed)

    except Exception as e:
        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
        await BDS_Log_Channel.send('{}\n\nError occured in covLoop\n{}'.format(e,timestamp))

class Special(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.is_owner()
    @slash_command(guild_ids=guild_ids, name='autocheckdbusers')
    async def _autocheckdbusers(self, ctx: commands.Context):
        '''Automatically search and add missing user to DB'''

        await ctx.defer()

        counter = 0

        for guild in bot.guilds:
            print(guild)
            for member in guild.members:
                print(member)
                if not DBConnection.checkUserInDB(str(member.id)):
                    DBConnection.addUserToDB(str(member.id))
                    counter += 1
        
        await ctx.send_followup('Found {} missing members in DB, added to DB.'.format(counter))

    @slash_command(guild_ids=guild_ids, name='meme')
    async def _meme(self, ctx: commands.Context, url, text, txtsize, pos, color):
        '''圖片網址(.jpg .png .gif) 文字(自己唸啦屌) 文字大小(數字) 位置(up center down) 顏色(red)'''

        await ctx.defer()

        try:
            image = Image.open(BytesIO(requests.get(url).content))
            draw = ImageDraw.Draw(image)
            txt = text
            fontsize = int(txtsize)
            ttf = 'https://www.dropbox.com/s/cq2bainz70cpbu4/ArialUnicodeMS.ttf?dl=1'

            W, H = image.size

            font = ImageFont.truetype(requests.get(ttf, stream=True).raw, fontsize)

            w, h = draw.textsize(txt, font=font)

            if pos == 'up':
                draw.text(((W-w)/2,(H-h)/50), txt, font=font, fill=color)
            elif pos == 'center' or pos == 'middle':
                draw.text(((W-w)/2,(H-h)/2), txt, font=font, fill=color)
            elif pos == 'down':
                draw.text(((W-w)/2,(H-h)-((H-h)/50)), txt, font=font, fill=color)
        except Exception as e:
            image = Image.open(BytesIO(requests.get('https://i.imgur.com/fYe7MrH.jpg').content))
            draw = ImageDraw.Draw(image)
            txt = "屌屌屌屌屌屌屌你呀"
            fontsize = 80
            ttf = 'https://www.dropbox.com/s/cq2bainz70cpbu4/ArialUnicodeMS.ttf?dl=1'
            color = 'red' #default

            W, H = image.size

            font = ImageFont.truetype(requests.get(ttf, stream=True).raw, fontsize)

            w, h = draw.textsize(txt, font=font)

            print('{} {} {} {}'.format((H-h), (H-h)/10, (H-h)/5, (H-h)/2))

            draw.text(((W-w)/2,(H-h)/50), txt, font=font, fill=color) #up

            await ctx.send_followup('{}\n出現了以上問題所以用了預設梗圖'.format(e))
        with BytesIO() as img:
            image.save(img, 'PNG')
            img.seek(0)
            file = discord.File(fp=img, filename='memeup.png')
        await ctx.send_followup(file=file)

    @slash_command(guild_ids=guild_ids, name='deletelol')
    @commands.is_owner()
    async def _deletelol(self, ctx:commands.Context, region:str, summonername:str):
        '''Delete summoner name tw na'''

        await ctx.defer()
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
        try:
            region = getRegion(region)
            DBConnection.deleteLol(region, summonername)
            await ctx.send_followup('Deleted {} to {}'.format(summonername, region))
        except Exception as e:
            BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
            await BDS_Log_Channel.send('{}\n\nError occured in deletelol\n{}'.format(e,timestamp))

    @slash_command(guild_ids=guild_ids, name='insertlol')
    @commands.is_owner()
    async def _insertlol(self, ctx:commands.Context, region:str, summonername:str):
        '''Insert summoner name tw na'''

        await ctx.defer()
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
        try:
            region = getRegion(region)
            DBConnection.insertLol(region, summonername)
            await ctx.send_followup('Inserted {} to {}'.format(summonername, region))
        except Exception as e:
            BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
            await BDS_Log_Channel.send('{}\n\nError occured in insertlol\n{}'.format(e,timestamp))

    @slash_command(guild_ids=guild_ids, name='map')
    async def _map(self, ctx:commands.Context, location:str):
        '''Retrieve location map by location name'''

        await ctx.defer()
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
        try:
            if ' ' in location:
                location = location.replace(' ','+')

            lat, lon = getLatLonByAddress('{}'.format(location))
            image = getMapsImageByLatLon(lat, lon, 18)
            with BytesIO() as img:
                image.save(img, 'PNG')
                img.seek(0)
                imgfile = discord.File(fp=img, filename='gMapLocation.png')

            await ctx.send_followup(file=imgfile)

            '''with BytesIO() as img:
                image.save(img, 'PNG')
                img.seek(0)
                imgfile = discord.File(fp=img, filename='gMapLocation.png')
            await ctx.send_followup(file=imgfile)

            with BytesIO() as img:
                image.save(img, 'PNG')
                img.seek(0)
                imgfile = discord.File(fp=img, filename='gMapLocation.png')
            await ctx.send_followup(file=imgfile)'''
        except Exception as e:
            BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
            await BDS_Log_Channel.send('{}\n\nError occured in map\n{}'.format(e,timestamp))

    @slash_command(guild_ids=guild_ids, name='testgamesloop')
    @commands.is_owner()
    async def _testgamesloop(self, ctx: commands.Context):
        '''Test command for gamesLoop'''

        await ctx.defer()
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
        try:
            hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

            url = Request("https://www.indiegamebundles.com/category/free/", headers=hdr)
            html_page = urlopen(url)
            soup = BeautifulSoup(html_page, "lxml")

            text = '' #game title
            link = '' #game url
            desc = '' #game desc
            dt = '' #posted dt
            for title in soup.findAll("div", class_="td-module-meta-info"): #entry-title td-module-title
                soup_section = BeautifulSoup(str(title), "lxml")

                for section in soup_section.findAll("time", class_="entry-date updated td-module-date"):
                    dt = str(section).split('datetime=\"')[1].split('\">',1)[0]
                    #print(dt+'\n') #text_30 = text[:min(len(text), 30)]
                    break
                dt_db = DBConnection.getPublishedAt('indiegamebundles')[0][0]
                if str(dt) == str(dt_db):
                    return
                else:
                    DBConnection.updatePublishedAt(dt, 'indiegamebundles')

                    for section in soup_section.findAll("h3", class_="entry-title td-module-title"):
                        title = str(section)
                        link = title.split('<a href=\"')[1].split('\" rel=\"bookmark\" title=\"')[0]
                        text = title.split('<a href=\"')[1].split('\" rel=\"bookmark\" title=\"')[1].split('</a></h3>')[0].split('\">')[0]
                        break

                    for section in soup_section.findAll("div", class_="td-excerpt"):
                        desc = str(section).split('\">',1)[1].split('</',1)[0]
                        break

                    #embed construct
                    embed = discord.Embed()
                    embed.title = text
                    embed.color = 0xb50024
                    embed.description = desc
                    embed.set_author(name='Indie Game Bundles', icon_url='https://i.imgur.com/UdkSDcb.png')
                    embed.set_thumbnail(url='https://i.imgur.com/RWIVDRN.png')
                    embed.set_footer(text=dt)

                    #url handlings
                    url = link
                    if url is not None and 'http' in url and '://' in url:
                        url2 = url.rsplit('/',1)[1]
                        url1 = url.rsplit('/',1)[0]
                        if url2 is not None and url2 != '' and not url2.isalnum():
                            url2 = quote(url2)
                            url = url1 +'/'+ url2
                        embed.url = url

                    BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
                    #BLG_ST_Channel = bot.get_channel(815568098001813555) #BrianLee Server - satellie
                    #BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

                    await BDS_PD_Channel.send(embed=embed)
                    #await BLG_ST_Channel.send(embed=embed)
                    #await BMS_OT_Channel.send(embed=embed)

                    await ctx.send_followup(embed=embed)

                break
        except Exception as e:
            BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
            await BDS_Log_Channel.send('{}\n\nError occured in newsLoop\n{}'.format(e,timestamp))
    
    @slash_command(guild_ids=guild_ids, name='testnewsloop')
    @commands.is_owner()
    async def _testnewsloop(self, ctx: commands.Context):
        '''Test command for newsLoop'''

        await ctx.defer()
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
        #try:
        # /v2/top-headlines
        top_headlines = newsapi.get_top_headlines(category='general', language='zh', country='hk')
        print('after api')
        selected_top_headline = ''
        for top_headline in top_headlines['articles']:
            #if top_headline['author'] == '香港經濟日報HKET':
            if top_headline['source']['name'] == 'Rthk.hk':
                selected_top_headline = top_headline
                break

        if selected_top_headline == '' or selected_top_headline is None:
            print('hadline none')
            return

        publishedAt = selected_top_headline['publishedAt']
        db_published_at = DBConnection.getPublishedAt('RTHK')[0][0]

        if str(publishedAt) == str(db_published_at):
            print('published same')
            return
        else:
            DBConnection.updatePublishedAt(publishedAt, 'RTHK')

            title = selected_top_headline['title']
            url = selected_top_headline['url']
            urlToImage = selected_top_headline['urlToImage'] if selected_top_headline['urlToImage'] is not None and 'http' in selected_top_headline['urlToImage'] and '://' in selected_top_headline['urlToImage'] else 'https://i.imgur.com/UdkSDcb.png'
            authorName = selected_top_headline['source']['name']
            author = selected_top_headline['author']
            description = selected_top_headline['description']
            footer = '{}'.format(publishedAt) if author is None else '{}\n{}'.format(author, publishedAt)

            embed = discord.Embed(title=title)

            #url handlings
            if url is not None and 'http' in url and '://' in url:
                url2 = url.rsplit('/',1)[1]
                url1 = url.rsplit('/',1)[0]
                if url2 is not None and url2 != '' and not url2.isalnum():
                    url2 = quote(url2)
                    url = url1 +'/'+ url2
                embed.url = url

            embed.description = description
            embed.set_author(name=authorName, icon_url='https://i.imgur.com/UdkSDcb.png')
            embed.set_thumbnail(url=urlToImage)
            embed.set_footer(text=footer)

            ##BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
            #BLG_MC_Channel = bot.get_channel(356782441777725440) #BrianLee Server - main channel
            #BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

            #await BDS_PD_Channel.send(embed=embed)
            #await BLG_MC_Channel.send(embed=embed)
            #await BMS_OT_Channel.send(embed=embed)

            await ctx.send_followup(embed=embed)
        '''except Exception as e:
            BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
            await BDS_Log_Channel.send('{}\n\nError occured in newsLoop\n{}'.format(e,timestamp))
            await ctx.send_followup('Error')'''


    @slash_command(guild_ids=guild_ids, name='log')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    async def log(self, ctx: commands.Context, message):
        '''Change log release'''
        
        if ctx.channel.id == 692466531447210105:

            #timezone
            tz = pytz.timezone('Asia/Hong_Kong')
            hk_now = datetime.now(tz)
            timestamp = str(hk_now)

            #channels
            changelog_channel = bot.get_channel(903541645411237889)
            logs_channel = bot.get_channel(809527650955296848)

            #changelog embed
            embed_changelog = discord.Embed()
            embed_changelog.set_author(name="Ben's Minecraft Server", icon_url="https://i.imgur.com/NssQKDi.png")
            embed_changelog.title = "Changelog"
            embed_changelog.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            embed_changelog.description = message
            embed_changelog.set_footer(text=timestamp)

            #send changelog
            try:
                await changelog_channel.send(embed=embed_changelog)
            except Exception as e:
                await ctx.respond("Unable to send message to change-log channel")
                await logs_channel.send(str(e))
                return

            #response embed
            embed = discord.Embed()
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.title = "已發布變更日誌"
            embed.description = str(message)
            embed.set_footer(text=timestamp)

            #send reponse
            await ctx.respond(embed=embed)
            await logs_channel.send("Changelog: {} --> {}".format(ctx.author,message))
        else:
            await ctx.respond("請去 <#692466531447210105>")
        
    @slash_command(guild_ids=guild_ids, name='testwelcome')
    @commands.is_owner()
    async def testwelcome(self, ctx: commands.Context):
        '''Test welcome message'''
        
        bot_channel_embed_to_staff = discord.Embed()
        bot_channel_embed_to_member = discord.Embed()

        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))

        bot_channel_embed_to_staff.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        bot_channel_embed_to_staff.title = "已加入Discord伺服器"
        bot_channel_embed_to_staff.add_field(name="Discord", value='<@{}>'.format(ctx.author.id), inline=True)
        bot_channel_embed_to_staff.set_footer(text=timestamp)

        bot_channel_embed_to_member.set_author(name="Ben's Minecraft Server", icon_url="https://i.imgur.com/NssQKDi.png")
        bot_channel_embed_to_member.title = "Welcome to Ben\'s Minecraft server"
        bot_channel_embed_to_member.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
        bot_channel_embed_to_member.add_field(name="IP (Survival)", value="mc.benwyw.com", inline=True)
        bot_channel_embed_to_member.add_field(name="Version", value="latest", inline=True)
        bot_channel_embed_to_member.add_field(name="Java & Bedrock", value="Support both Java & Bedrock. Bedrock requires Port `19132`", inline=False)
        bot_channel_embed_to_member.add_field(name="Verify guide", value="Reply this bot with your Minecraft username, please join the server at least once before requesting.", inline=False)
        bot_channel_embed_to_member.add_field(name="In-game guide", value="`/ibooks list` `/ibooks get (book)`", inline=False)
        bot_channel_embed_to_member.add_field(name="Website", value="www.benwyw.com", inline=True)
        bot_channel_embed_to_member.add_field(name="Map", value="map.benwyw.com", inline=True)
        bot_channel_embed_to_member.add_field(name="Instagram", value="ig.benwyw.com", inline=True)
        bot_channel_embed_to_member.set_footer(text=timestamp)

        #wmsg = "Welcome!\n\nTo verify yourself: https://www.benwyw.com/forums/request-verified/\nVerify Guide: https://www.benwyw.com/faq/\n@Staff in-game if you come up with any server related issues.\n\nPublic Relations Team\nBen's Minecraft Server\n\nMinecraft Server IP: mc.benwyw.com\nWebsite: https://www.benwyw.com"
        bot_channel = bot.get_channel(692466531447210105)
        try:
            await ctx.author.send(embed=bot_channel_embed_to_member)
            bot_channel_embed_to_staff.description = "歡迎信息發送成功"
            bot_channel_embed_to_staff.color = 0x00ff00
        except Exception as e:
            bot_channel_embed_to_staff.description = "無法發送歡迎信息"
            bot_channel_embed_to_staff.color = 0xff0000
            logs_channel = bot.get_channel(809527650955296848)
            await logs_channel.send(str(e))
        await bot_channel.send(embed=bot_channel_embed_to_staff)
        await ctx.respond('Completed')

    @slash_command(guild_ids=guild_ids, name='updateserverpw')
    @commands.is_owner()
    async def updateserverpw(self, ctx: commands.Context, id, pw):
        '''Update server pw by (id pw)'''

        await ctx.defer()
        result = "No operations."

        try:
            DBConnection.updateServerPw(str(id), str(pw))
            result = "Successfully updated password for `{}` in serverlist".format(id)
        except Exception as e:
            result = "Failed to update password for `{}` in serverlist".format(id)

        await ctx.send_followup(result)
        await bot.get_channel(356782441777725440).send("私人伺服器已更新密碼 | `/getserver {}`".format(id))
        await bot.get_channel(772038210057535488).send("私人伺服器已更新密碼 | `/getserver {}`".format(id))

    @slash_command(guild_ids=guild_ids, name='deleteserver')
    @commands.is_owner()
    async def deleteserver(self, ctx: commands.Context, id):
        '''Delete server by (id)'''

        await ctx.defer()
        result = "No operations."

        DBConnection.deleteServer(str(id))
        result = "Successfully deleted `{}` in serverlist".format(id)
        
        await ctx.send_followup(result)

    @slash_command(guild_ids=guild_ids, name='updateserver')
    @commands.is_owner()
    async def updateserver(self, ctx: commands.Context, id, pw=None, game: str=None, port: int=None, remarks: str=None):
        '''Update server pw by (id$pw[nullable]$game$port[nullable]$remarks)'''

        await ctx.defer()
        result = "No operations."

        if pw is not None:
            remarks = "Private | {} | `/getserver {}`".format(remarks,id) if remarks is not None else "Private | `/getserver {}`".format(id)
        else:
            remarks = "Public | {}".format(remarks) if remarks is not None else "Public"

        DBConnection.updateServer(id, pw, game, port, remarks)
        result = "Successfully updated `{}` in serverlist".format(id)
        
        await ctx.send_followup(result)

    @slash_command(guild_ids=guild_ids, name='createserver')
    @commands.is_owner()
    async def createserver(self, ctx: commands.Context, id, pw=None, game: str=None, port: int=None, remarks: str=None):
        '''Create server id pw by (id$pw[nullable]$game$port[nullable]$remarks)'''

        result = "No operations."
        await ctx.defer()

        if pw is not None:
            remarks = "Private | {} | `/getserver {}`".format(remarks, id) if remarks is not None else "Private | `/getserver {}`".format(id)
        else:
            remarks = "Public | {}".format(remarks) if remarks is not None else "Public"

        DBConnection.createServer(id, pw, game, port, remarks)
        result = "Successfully created `{}` in serverlist".format(id)
        await ctx.send_followup(result)

    @slash_command(guild_ids=guild_ids, name='getserver')
    async def _getserver(self, ctx: commands.Context, code):
        '''在__私訊__收到 play.benwyw.com 既 Private Server 資訊'''
        
        await ctx.defer()

        game = ""
        port = ""
        remarks = ""
        password = ""
        status = ""
        baroUserList = [254517813417476097, 346518519015407626, 270781455678832641, 49924747686969344, 372395366986940416, 363347146080256001, 313613491816890369]
        #254517813417476097 Ben
        #346518519015407626 Pok
        #270781455678832641 Daniel
        #349924747686969344 Chest
        #372395366986940416 Nelson
        #363347146080256001 Kei
        #313613491816890369 keith   Pok's friend
        terrariaUserList = [254517813417476097, 232833713648435200, 311425525732212736]
        #232833713648435200 Sheep
        #311425525732212736 Willy


        embed = discord.Embed(title="Private server info | 私人伺服器資訊", color=0x00ff00)
        embed.description = "IP: `play.benwyw.com`"
        embed.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        code = code.lower()

        '''
        if code is not None and ctx.author.id in baroUserList:
            selectServer = DBConnection.selectServer(code)
            if  selectServer is not None:
                if selectServer[1] != "-":
                    game = selectServer[2]
                    port = selectServer[3]
                    remarks = selectServer[4]
                    password = "||`{}`||".format(selectServer[1])
                    status = "Success"
                else:
                    status = "No password"
            else:
                status = "Code not found"
        else:
            embed.add_field(name="Error", value='You are not permitted, please contact Ben.'.format(code))
            status = "No permission"
        '''

        if code is not None:
            selectServer = DBConnection.selectServer(code)
            if selectServer is not None:
                if selectServer[1] != "-":
                    if code == "baro":
                        if ctx.author.id in baroUserList:
                            game = selectServer[2]
                            port = selectServer[3]
                            remarks = selectServer[4]
                            password = "||`{}`||".format(selectServer[1])
                            status = "Success"
                        else:
                            embed.add_field(name="Error", value='You are not permitted, please contact Ben.'.format(code))
                            status = "No permission"
                    if code == "terraria":
                        if discord.utils.get(ctx.guild.roles, id=720669342550720663) in ctx.author.roles or discord.utils.get(ctx.guild.roles, id=735956800750223430) in ctx.author.roles or ctx.author.id in terrariaUserList:
                            game = selectServer[2]
                            port = selectServer[3]
                            remarks = selectServer[4]
                            password = "||`{}`||".format(selectServer[1])
                            status = "Success"
                        else:
                            embed.add_field(name="Error", value='You are not permitted, please contact Ben.'.format(code))
                            status = "No permission"
                else:
                    status = "No password"
            else:
                status = "Code not found"
            
                            


        if status == "No password":
            await ctx.send_followup("Requesting code is not a private server!")
        elif status == "Code not found":
            await ctx.send_followup("Requesting code does not exist.")
        else:
            if status == "Success":
                embed.add_field(name="Game", value=game, inline=True)
                embed.add_field(name="Port", value=port, inline=True)
                embed.add_field(name="Remarks", value=remarks, inline=True)
                embed.add_field(name="Password", value=password, inline=True)
            
            embed.set_footer(text="www.benwyw.com")

            #Private Message:
            await ctx.author.send(embed=embed)

            #Channel Message:
            await ctx.send_followup("請查閱私人訊息。")

            #log Message:
            await bot.get_channel(809527650955296848).send("{} 已查詢私人伺服器資訊 (Code = {}, Status = {})".format(ctx.author,code, status))

    @slash_command(guild_ids=guild_ids, name='server', aliases=['ser','serverlist'])
    async def _server(self, ctx: commands.Context):
        '''所有 play.benwyw.com 既 Server 列表'''

        await ctx.defer()

        embed1 = discord.Embed(title="Main Server | 主要伺服器", color=0x00ff00)
        embed1.description = "End of service 17Dec2021"
        '''
        "IP: `mc.benwyw.com`"
        '''
        embed1.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")

        embed1.add_field(name="Game", value='Minecraft (Survival)', inline=True)
        embed1.add_field(name="Port", value='`25565`', inline=True)
        embed1.add_field(name="Remarks", value='Public | Latest | Java & Bedrock', inline=True)

        embed1.set_footer(text="www.benwyw.com")

        embed = discord.Embed(title="List of Servers Enabled | 已啟用的伺服器列表", color=0x00ff00)
        embed.description = "IP: `play.benwyw.com`"
        #embed.set_author(name='Test Name', icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")

        #embed.add_field(name="Game", value='Minecraft (Survival)\nMinecraft (Pixelmon)\nTerraria (Expert)\nBarotrauma', inline=True)
        #embed.add_field(name="Port", value='`25565`\n-\n`7777`\n-', inline=True)
        #embed.add_field(name="Remarks", value='Public | 1.17.1 | Java & Bedrock\nPublic | Pixelmon Reforged 8.3.0\nPublic | Vanilla\nPrivate | `$get baro`', inline=True)
        #embed.add_field(name="Password", value='使用__相應Remarks指令__，在__私訊__收到Private資訊', inline=False)

        serverList = DBConnection.selectAllServer()
        count = 0
        for server in serverList:
            #id = server[0]
            #pw = server[1]
            game = server[2]
            port = server[3]
            remarks = server[4]

            if count == 0:
                embed.add_field(name="Game", value=game, inline=True)
                embed.add_field(name="Port", value=port, inline=True)
                embed.add_field(name="Remarks", value=remarks, inline=True)
            else:
                embed.add_field(name="\u200b", value=game, inline=True)
                if port != "-":
                    port = "`{}`".format(port)
                else:
                    port = "{}".format(port)
                embed.add_field(name="\u200b", value=port, inline=True)
                embed.add_field(name="\u200b", value=remarks, inline=True)

            count += 1

        '''
        embed.add_field(name="Game", value='Minecraft (Survival)', inline=True)
        embed.add_field(name="Port", value='`25565`', inline=True)
        embed.add_field(name="Remarks", value='Public | 1.17.1 | Java & Bedrock', inline=True)

        embed.add_field(name="\u200b", value='Minecraft (Pixelmon)', inline=True)
        embed.add_field(name="\u200b", value='-', inline=True)
        embed.add_field(name="\u200b", value='Public | Pixelmon Reforged 8.3.0', inline=True)

        embed.add_field(name="\u200b", value='Terraria (Expert)', inline=True)
        embed.add_field(name="\u200b", value='`7777`', inline=True)
        embed.add_field(name="\u200b", value='Public | Vanilla', inline=True)

        if DBConnection.selectServer("baro") is not None:
            embed.add_field(name="\u200b", value='Barotrauma', inline=True)
            embed.add_field(name="\u200b", value='-', inline=True)
            embed.add_field(name="\u200b", value='Private | `/get baro`', inline=True)
        '''

        embed.add_field(name="Password", value='使用__相應Remarks指令__，在__私訊__收到Private資訊。', inline=False)

        embed.set_footer(text="www.benwyw.com")

        await ctx.send_followup(embed=embed1)
        await ctx.send_followup(embed=embed)

    @slash_command(guild_ids=guild_ids, name='bind')
    #@commands.cooldown(1, 60, commands.BucketType.user)
    async def _bind(self, ctx: commands.Context, message):
        '''與Minecraft伺服器綁定 /bind (username)'''

        await ctx.defer()

        id = ctx.author.id
        mc_Username = message
        DBConnection.updateUserMcName(id, mc_Username)

        embed = discord.Embed(title="伺服器綁定", color=0x00ff00)
        embed.description = "Minecraft名: {}".format(mc_Username)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
        embed.set_footer(text="IP: mc.benwyw.com")

        await ctx.send_followup(embed=embed)

    @slash_command(guild_ids=guild_ids, name='unbind')
    #@commands.cooldown(1, 60, commands.BucketType.user)
    async def _unbind(self, ctx: commands.Context):
        '''與Minecraft伺服器解除綁定'''

        await ctx.defer()

        id = ctx.author.id
        DBConnection.updateUserMcName(id, None)

        embed = discord.Embed(title="伺服器綁定", color=0x00ff00)
        embed.description = "Minecraft名: 已解除綁定"
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
        embed.set_footer(text="IP: mc.benwyw.com")

        await ctx.send_followup(embed=embed)

    @slash_command(guild_ids=guild_ids, name='bound')
    async def _bound(self, ctx: commands.Context):
        '''檢閱Minecraft伺服器綁定狀態'''
        
        await ctx.defer()

        id = ctx.author.id
        mc_Username = DBConnection.fetchUserMcName(id)[0]
        embed = discord.Embed(title="伺服器綁定", color=0x00ff00)

        if mc_Username is None:
            embed.description = "Minecraft名: 尚未綁定伺服器，\n請使用 /bind (Minecraft名)"
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            embed.set_footer(text="IP: mc.benwyw.com")
        else:
            embed.description = "Minecraft名: {}".format(mc_Username)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            embed.set_footer(text="IP: mc.benwyw.com")

        await ctx.send_followup(embed=embed)

    @slash_command(guild_ids=guild_ids, name='rank')
    async def _rank(self, ctx: commands.Context):
        '''查閱全宇宙排行榜 及 你的排名'''
        await ctx.defer()

        embed = discord.Embed(title="全宇宙首十名 排行榜",
                              description="根據德州撲克勝場已定。",
                              color=0x00ff00)
        embed.set_thumbnail(url="https://i.imgur.com/1DDTG0z.png")

        embed2 = discord.Embed(title="你的排名", color=0x00ff00)
        embed2.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed2.set_thumbnail(url="https://i.imgur.com/1DDTG0z.png")

        embed3 = discord.Embed(title="全宇宙首十名 排行榜",
                              description="根據德州撲克金錢已定。",
                              color=0x00ff00)
        embed3.set_thumbnail(url="https://i.imgur.com/1DDTG0z.png")

        rankData = DBConnection.fetchAllRankData()
        moneyData = DBConnection.fetchAllMoneyData()

        count = 1
        for user in rankData:
            tempid = user[0]
            tempWIN = user[1]

            if count <= 10:
                user = await bot.fetch_user(tempid)

                embed.add_field(name="{}. {}".format(count,user.display_name),
                                value="勝場: {}".format(tempWIN), inline=False)

            if int(ctx.author.id) == int(tempid):
                userWin = DBConnection.fetchUserData("userWin", tempid)

                embed2.description = "勝場: {}".format(userWin)
                embed2.add_field(name="全宇宙排行(勝場)", value="No.{} | 勝場: {}".format(count,tempWIN))

            count += 1

        count = 1
        for user in moneyData:
            tempid = user[0]
            tempMONEY = user[1]

            if count <= 10:
                user = await bot.fetch_user(tempid)

                embed3.add_field(name="{}. {}".format(count,user.display_name),
                                 value="金錢: {}".format(tempMONEY), inline=False)

            if int(ctx.author.id) == int(tempid):
                userBalance = DBConnection.fetchUserData("userBalance", tempid)

                embed2.description += " | 金錢: {}".format(userBalance)
                embed2.add_field(name="全宇宙排行(金錢)", value="No.{} | 金錢: {}".format(count,tempMONEY))

            count += 1

        await ctx.send_followup(embed=embed)
        await ctx.send_followup(embed=embed3)
        await ctx.send_followup(embed=embed2)


    @slash_command(guild_ids=guild_ids, name='draw', aliases=['bonus','prize','b','reward'], pass_context=True)
    #@commands.cooldown(1, 600, commands.BucketType.user)
    async def _reward(self, ctx: commands.Context):
        '''隨機獎金'''
        await ctx.defer()

        chanceList = [0,1,2,3,4]

        first = str(ctx.author.name)
        middle = "抽中了"

        e = discord.Embed()

        id = ctx.author.id
        console_channel = bot.get_channel(686911996309930006)
        serverchat_channel = bot.get_channel(684024056944787489)
        console_seasonal_channel = bot.get_channel(888429949873172570)

        seed = random.choices(chanceList, weights=(1.5, 5.5, 15, 33, 45), k=1)
        seed = int(str(seed).replace("[","").replace("]",""))

        if seed == 4:
            img = "https://i.imgur.com/IfZS8xe.gif"
            end = "星蛋 $100~300區間"
            money = randrange(100,300+1,1)
        elif seed == 3:
            img = "https://i.imgur.com/k0SQ1Lt.png"
            end = "銀蛋 $301~500區間"
            money = randrange(301,500+1,1)
        elif seed == 2:
            img = "https://i.imgur.com/JyDHamm.gif"
            end = "金蛋 $501~700區間"
            money = randrange(501,700+1,1)
        elif seed == 1:
            img = "https://i.imgur.com/crdEb6i.gif"
            end = "鑽蛋 $701~1000區間"
            money = randrange(701,1000+1,1)
        elif seed == 0:
            img = "https://i.imgur.com/WBfgmgL.png"
            end = "壞蛋 -$500~1500區間"
            money = randrange(-1500,-500+1,1)

        oldTotal = DBConnection.fetchUserData("userBalance", id)

        newTotal = oldTotal + money
        if newTotal <= 0:
            newTotal = 0

        DBConnection.updateUserBalance(id, newTotal)
        newTotal = DBConnection.fetchUserData("userBalance", id)

        msg = first+" "+middle+end

        e.set_image(url=img)
        e.set_author(name=msg, url=e.Empty, icon_url=e.Empty)

        default_content = "{}得到了 ${} | ${} --> ${}".format(first,money,oldTotal,newTotal)

        # if user binded with MC name:
        binded = False

        mc_Username = DBConnection.fetchUserMcName(id)[0]

        if mc_Username is None:
            binded = False
        else:
            binded = True

        if binded is True:
            if mc.status() == 'online':
                await console_channel.send("eco give {} {}".format(mc_Username, money))
                await serverchat_channel.send("{} received ${} from per-10 mins lucky draw '/draw'!".format(mc_Username, money))
                mc_content_1 = "\n{}得到了 ${}".format(mc_Username,money)
                if mc.status_seasonal() == 'online':
                    await console_seasonal_channel.send("!cmd say {} received ${} from per-10 mins lucky draw '/draw'!".format(mc_Username, money))
            else:
                mc_content_1 = "\nServer is offline"
        else:
            mc_content_1 = "\n尚未綁定伺服器 /bind"

        mc_content_2 = "\nmc.benwyw.com | play.benwyw.com"
        mc_content = mc_content_1 + mc_content_2

        final_content = default_content + mc_content

        e.set_footer(text=final_content)

        await ctx.send_followup(embed=e)

    @slash_command(guild_ids=guild_ids, name='announce')
    @commands.is_owner()
    async def _announce(self, ctx: commands.Context, message):
        '''特別指令。公告。'''

        #client.get_channel("182583972662")
        '''
        logs_channel = bot.get_channel(809527650955296848)

        for guild in bot.guilds:
            try:
                await guild.system_channel.send(message)
            except Exception as e:
                # do logs
                await ctx.send("Default channel not found, sent to text 01")
                await logs_channel.send(str(e))

                # backup announce method
                await guild.text_channels[0].send(message)

        embed = discord.Embed()
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        tz = pytz.timezone('Asia/Hong_Kong')
        hk_now = datetime.now(tz)
        timestamp = str(hk_now)

        embed.title = "Announced"
        embed.description = str(message)
        embed.set_footer(text=timestamp)

        await ctx.send(embed=embed)
        await logs_channel.send("Announced: {}".format(message))
        await ctx.message.delete()
        '''
        if ctx.channel.id == 810511993449742347:
            #timezone
            tz = pytz.timezone('Asia/Hong_Kong')
            hk_now = datetime.now(tz)
            timestamp = str(hk_now)

            #channels
            botupdates_channel = bot.get_channel(910000426240340009)
            logs_channel = bot.get_channel(809527650955296848)
            main_channel = bot.get_channel(356782441777725440) #BrianLee Game Discord
            crows_channel = bot.get_channel(925673962283884584) #Ben Discord Bot

            #images related
            bot_member = ctx.guild.get_member(809526579389792338)

            #botupdates embed
            embed_botupdates = discord.Embed()
            embed_botupdates.set_author(name="Ben AI", icon_url=bot_member.display_avatar.url)
            embed_botupdates.title = "Bot Updates"
            embed_botupdates.set_thumbnail(url=bot_member.display_avatar.url)
            embed_botupdates.description = message
            embed_botupdates.set_footer(text=timestamp)

            #preview
            #await ctx.respond(embed=embed_botupdates)

            #loading
            await ctx.defer()

            #send botupdates
            try:
                await botupdates_channel.send(embed=embed_botupdates)
            except Exception as e:
                await ctx.send_followup("Unable to send message to bot-updates channel")
                await logs_channel.send(str(e))

            #send main
            try:
                await main_channel.send(embed=embed_botupdates)
            except Exception as e:
                await ctx.send_followup("Unable to send message to 主頻道")
                await logs_channel.send(str(e))

            #send crows
            try:
                await crows_channel.send(embed=embed_botupdates)
            except Exception as e:
                await ctx.send_followup("Unable to send message to 鎹鴉")
                await logs_channel.send(str(e))

            #response embed
            embed = discord.Embed()
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.title = "已發布Bot Updates"
            embed.description = str(message)
            embed.set_footer(text=timestamp)

            #send reponse
            await ctx.send_followup(embed=embed)
            await logs_channel.send("Bot Updates: {} --> {}".format(ctx.author,message))
        else:
            await ctx.respond("請去 <#810511993449742347>")

    @slash_command(guild_ids=guild_ids, name='status')
    @commands.is_owner()
    async def _status(self, ctx: commands.Context, status):
        '''特別指令。更改狀態。'''

        if status != "reset":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/ | {}".format(status)))
        else:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/ | 冇野幫到你"))
        
        await ctx.respond('Request processed.')

    @slash_command(guild_ids=guild_ids, name='block')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _tempblk(self, ctx: commands.Context, message):
        '''特別指令。Temp block verification request。'''
        if ctx.channel.id == 878538264762527744 or ctx.channel.id == 692466531447210105:
            await ctx.respond('Request processed.')

            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
            req_ver_channel = bot.get_channel(878538264762527744)
            req_ver_embed_to_staff = discord.Embed()
            req_ver_embed_to_staff.title = "已被暫時封鎖驗證請求"
            req_ver_embed_to_staff.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            req_ver_embed_to_staff.set_footer(text=timestamp)

            if "!" in message:
                user = bot.get_user(int(str(message).replace("<@!","").replace(">","")))
            else:
                user = bot.get_user(int(str(message).replace("<@","").replace(">","")))
            member = ctx.guild.get_member(user.id)

            if user.id in temp_blocked_list:
                req_ver_embed_to_staff.description = "已在臨時封鎖驗證名單中"
                req_ver_embed_to_staff.color = 0x000000
            else:
                temp_blocked_list.append(user.id)
                req_ver_embed_to_staff.description = "已放入臨時封鎖驗證名單中"
                req_ver_embed_to_staff.color = 0xff0000
                await member.send("You have been blocked from sending verification request temporarily.")
            temp_blocked_list_names = ""
            if temp_blocked_list:
                for name in temp_blocked_list:
                    name_displayname = bot.get_user(name)
                    temp_blocked_list_names += "{}\n".format(name_displayname)
            else:
                temp_blocked_list_names = "(empty)"

            req_ver_embed_to_staff.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            req_ver_embed_to_staff.add_field(name="臨時封鎖驗證名單", value=str(temp_blocked_list_names), inline=True)
            req_ver_embed_to_staff.add_field(name="執行者", value=ctx.author.display_name, inline=True)

            await req_ver_channel.send(embed=req_ver_embed_to_staff)

    @slash_command(guild_ids=guild_ids, name='unblock')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _unblk(self, ctx: commands.Context, message):
        '''特別指令。Unblock verification request。'''
        if ctx.channel.id == 878538264762527744 or ctx.channel.id == 692466531447210105:
            await ctx.respond('Request processed.')

            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
            req_ver_channel = bot.get_channel(878538264762527744)
            req_ver_embed_to_staff = discord.Embed()
            req_ver_embed_to_staff.title = "已被解除封鎖驗證請求"
            req_ver_embed_to_staff.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            req_ver_embed_to_staff.set_footer(text=timestamp)

            if "!" in message:
                user = bot.get_user(int(str(message).replace("<@!","").replace(">","")))
            else:
                user = bot.get_user(int(str(message).replace("<@","").replace(">","")))

            member = ctx.guild.get_member(user.id)

            if user.id in temp_blocked_list:
                temp_blocked_list.remove(user.id)
                req_ver_embed_to_staff.description = "已從臨時封鎖驗證名單移除"
                req_ver_embed_to_staff.color = 0x00ff000
                await member.send("You have been unblocked from sending verification request.")
            else:
                req_ver_embed_to_staff.description = "不在臨時封鎖驗證名單中"
                req_ver_embed_to_staff.color = 0x000000

            temp_blocked_list_names = ""
            if temp_blocked_list:
                for name in temp_blocked_list:
                    name_displayname = bot.get_user(name)
                    temp_blocked_list_names += "{}\n".format(name_displayname)
            else:
                temp_blocked_list_names = "(empty)"

            req_ver_embed_to_staff.set_author(name=member.display_name, icon_url=member.display_avatar.url)
            req_ver_embed_to_staff.add_field(name="臨時封鎖驗證名單", value=str(temp_blocked_list_names), inline=True)
            req_ver_embed_to_staff.add_field(name="執行者", value=ctx.author.display_name, inline=True)

            await req_ver_channel.send(embed=req_ver_embed_to_staff)

    @slash_command(guild_ids=guild_ids, name='blocklist')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _blklist(self, ctx: commands.Context):
        '''特別指令。Unblock verification request。'''
        await ctx.defer()
        if ctx.channel.id == 878538264762527744 or ctx.channel.id == 692466531447210105:
            await ctx.send_followup('Request processed.')

            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
            req_ver_channel = bot.get_channel(878538264762527744)
            req_ver_embed_to_staff = discord.Embed()
            req_ver_embed_to_staff.title = "臨時封鎖驗證名單"
            req_ver_embed_to_staff.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            req_ver_embed_to_staff.set_footer(text=timestamp)

            temp_blocked_list_names = ""
            if temp_blocked_list:
                for name in temp_blocked_list:
                    name_displayname = bot.get_user(name)
                    temp_blocked_list_names += "{}\n".format(name_displayname)
            else:
                temp_blocked_list_names = "(empty)"

            req_ver_embed_to_staff.description = str(temp_blocked_list_names)

            await req_ver_channel.send(embed=req_ver_embed_to_staff)
        else:
            await ctx.send_followup('請去 <#878538264762527744> 或 <#692466531447210105>')

    @slash_command(guild_ids=guild_ids, name='dm')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _dm(self, ctx: commands.Context, target, content):
        """特別指令。Bot DM for Minecraft Staff usage。"""
        await ctx.defer()
        if ctx.channel.id == 878538264762527744 or ctx.channel.id == 692466531447210105:
            req_ver_channel = bot.get_channel(878538264762527744)
            target = target.lower()

            if 'ben' in target:
                memberid = 254517813417476097
            #elif 'ronald' in target:
                #memberid = 525298794653548751
            #elif 'chris' in target:
                #memberid = 562972196880777226
            #elif 'anson' in target:
                #memberid = 199877205071888384
            #elif 'andy' in target:
                #memberid = 407481608560574464

            elif 'pok' in target:
                memberid = 346518519015407626
            elif 'chester' in target:
                memberid = 349924747686969344
            elif 'daniel' in target:
                memberid = 270781455678832641
            elif 'kei' in target:
                memberid = 363347146080256001
            #elif 'olaf' in target:
                #memberid = 272977239014899713
            elif 'brian' in target:
                memberid = 262267347379683329
            #elif 'blue' in target:
                #memberid = 394354007650336769
            elif 'nelson' in target:
                memberid = 372395366986940416
            elif 'ivan' in target:
                memberid = 269394999890673664
            else:
                memberid = int(target)

            person = bot.get_user(memberid)
            try:
                await person.send(content)
            except Exception as e:
                await ctx.send_followup("無法傳訊至: "+str(person))
                await req_ver_channel.send(str(e))
            else:
                await ctx.send_followup("成功傳訊至: "+str(person))
        else:
            await ctx.send_followup('請去 <#878538264762527744> 或 <#692466531447210105>')

    @slash_command(guild_ids=guild_ids, name='ver')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _ver(self, ctx: commands.Context, message):
        '''特別指令。驗證玩家Minecraft。'''
        if ctx.channel.id == 878538264762527744 or ctx.channel.id == 692466531447210105:
            await ctx.respond('Request processed.')

            channel_console = bot.get_channel(686911996309930006)
            req_ver_channel = bot.get_channel(878538264762527744)

            vmsg = "You're now verified. Lands Guide: https://www.benwyw.com/forums/news-and-announcements/lands-protected-areas-regions/. Discord: https://discord.gg/wtp85zc"
            player_name = str(message)
            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
            req_ver_embed_to_staff = discord.Embed()

            req_ver_embed_to_staff.title = "已處理Minecraft驗證請求"
            req_ver_embed_to_staff.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            req_ver_embed_to_staff.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            req_ver_embed_to_staff.add_field(name="Minecraft", value=player_name, inline=True)
            req_ver_embed_to_staff.set_footer(text=timestamp)

            try:
                if player_name.lower not in mc_ops:
                    await channel_console.send("lp user " + player_name + " parent set member")
                    await channel_console.send("msg " + player_name + " " + vmsg)
                    await channel_console.send("mail send " + player_name + " " + vmsg)
                else:
                    raise OpError("不能Verify具OP權限的管理員。")

                req_ver_embed_to_staff.color = 0x00ff00
                req_ver_embed_to_staff.description = "處理成功"
            except Exception as e:
                req_ver_embed_to_staff.color = 0xff0000
                req_ver_embed_to_staff.description = str(e)

            await req_ver_channel.send(embed=req_ver_embed_to_staff)
        else:
            await ctx.respond('請去 <#878538264762527744> 或 <#692466531447210105>')

    @slash_command(guild_ids=guild_ids, name='discver')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _discver(self, ctx: commands.Context, message):
        '''特別指令。驗證玩家Discord。'''
        if ctx.channel.id == 878538264762527744 or ctx.channel.id == 692466531447210105:
            await ctx.respond('Request processed.')

            req_ver_channel = bot.get_channel(878538264762527744)
            log_channel = bot.get_channel(809527650955296848)
            #vmsg = "Hi,\n\nYou've been moved to __Verified__ group in our Discord server due to successful verification.\nLands Guide: https://www.benwyw.com/forums/news-and-announcements/lands-protected-areas-regions/\n\nStaff Team\nBen's Minecraft Server\n\nMinecraft Server IP: mc.benwyw.com\nWebsite: https://www.benwyw.com"

            if "!" in message:
                user = bot.get_user(int(str(message).replace("<@!","").replace(">","")))
            else:
                user = bot.get_user(int(str(message).replace("<@","").replace(">","")))

            member = ctx.guild.get_member(user.id)
            role = discord.utils.find(lambda r: r.name == 'Verified', ctx.message.guild.roles)
            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
            req_ver_embed_to_staff = discord.Embed()
            req_ver_embed_to_member = discord.Embed()

            req_ver_embed_to_staff.title = "已處理Discord驗證請求"
            req_ver_embed_to_staff.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            req_ver_embed_to_staff.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            req_ver_embed_to_staff.add_field(name="Discord", value=user, inline=True)
            req_ver_embed_to_staff.set_footer(text=timestamp)

            req_ver_embed_to_member.title = "Verification"
            req_ver_embed_to_member.description = "Your Discord verification request was approved"
            req_ver_embed_to_member.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            req_ver_embed_to_member.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
            req_ver_embed_to_member.add_field(name="Discord", value=user, inline=True)
            req_ver_embed_to_member.add_field(name="Lands Guide", value="https://www.benwyw.com/forums/news-and-announcements/lands-protected-areas-regions/", inline=False)
            req_ver_embed_to_member.set_footer(text=timestamp)

            if not role in member.roles:
                await member.add_roles(role)
                try:
                    await user.send(embed=req_ver_embed_to_member)
                    req_ver_embed_to_staff.description = "處理成功"
                    req_ver_embed_to_staff.color = 0x00ff00
                except Exception as e:
                    req_ver_embed_to_staff.description = "無法回覆 {} 請求提交成功".format(str(user))
                    req_ver_embed_to_staff.color = 0xff0000
                    await log_channel.send(str(e))
            else:
                req_ver_embed_to_staff.description = "{} 已驗證".format(str(user))
                req_ver_embed_to_staff.color = 0xff0000

            await req_ver_channel.send(embed=req_ver_embed_to_staff)

    @slash_command(guild_ids=guild_ids, name='menu')
    async def _menu(self, ctx: commands.Context):
        """Menu測試"""
        page1 = discord.Embed (
            title = '頁 1/3',
            description = '早',
            colour = discord.Colour.orange()
        )
        page2 = discord.Embed (
            title = '頁 2/3',
            description = '晨',
            colour = discord.Colour.orange()
        )
        page3 = discord.Embed (
            title = '頁 3/3',
            description = '呀',
            colour = discord.Colour.orange()
        )

        pages = [page1, page2, page3]

        message = await ctx.respond(embed = page1)

        await message.add_reaction('⏮')
        await message.add_reaction('◀')
        await message.add_reaction('▶')
        await message.add_reaction('⏭')

        i = 0
        emoji = ''

        def check(reaction, user):
            return message == message

        try:
            while True:
                if emoji == '⏮':
                    i = 0
                    await message.edit(embed = pages[i])
                elif emoji == '◀':
                    if i > 0:
                        i -= 1
                        await message.edit(embed = pages[i])
                elif emoji == '▶':
                    if i < 2:
                        i += 1
                        await message.edit(embed = pages[i])
                elif emoji == '⏭':
                    i = 2
                    await message.edit(embed=pages[i])
                res = await bot.wait_for('reaction_add', timeout = 30.0, check = check)
                if res == None:
                    break
                if str(res[1]) != 'Ben AI#0649':  #Example: 'MyBot#1111'
                    emoji = str(res[0].emoji)
                    await message.remove_reaction(res[0].emoji, res[1])

        except:
            await message.clear_reactions()

    @slash_command(guild_ids=guild_ids, name='chest')
    async def _chest(self, ctx: commands.Context, code, key):
        """/chest CivilCodeMenu網址 關鍵字"""

        await ctx.defer()
        response = requests.get(code)
        if response.status_code == 200:
            for line in response.content.decode('utf-8').splitlines():
                if 'pdfIcon after' in line:
                    pdf_url = line.split("=\"")[1].split("\" class")[0].replace("../../../../","https://www.bd.gov.hk/")

                    pdfFile = parser.from_file(pdf_url)

                    if key.lower() in str(pdfFile["content"]).lower():
                        await ctx.send_followup("在 {} 找到 {}".format(pdf_url,key))
        else:
            await ctx.send_followup('Response.status_code != 200. <@{}>'.format(bot.owner_id))

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @slash_command(guild_ids=guild_ids, name='hello')
    async def _hello(self, ctx: commands.Context):
        '''Say Hello to the AI'''

        await ctx.respond("你好呀 "+str(ctx.author.display_name))
        await ctx.send_followup("你好你好")

    @slash_command(guild_ids=guild_ids, name='ping')
    async def _ping(self, ctx: commands.Context, target):
        '''Ping爆佢!!!'''

        if '<@' not in target and '>' not in target:
            await ctx.respond("我唔會Ping: 空氣 / 其他Bot")
        else:
            embed = discord.Embed()
            embed.set_author(name="{} 揾你".format(ctx.author.display_name))
            await ctx.respond("Ping爆佢!!!")
            for count in range(10):
                await ctx.send_followup("{}".format(target))
                await ctx.send_followup(embed=embed)

    @slash_command(guild_ids=guild_ids, name='news')
    async def _news(self, ctx:commands.Context, search=None, language=None):
        """新聞 zh=中文 en=英文 默認中文"""

        if ctx.guild.id == 351742829254410250 and ctx.channel.id == 356782441777725440 or ctx.guild.id == 671654280985313282 and ctx.channel.id in [684024056944787489, 903247995682824242, 717424039387201536, 684024142135296059]:
            await ctx.respond('由於指令結果會洗版，已在主頻道禁用，請在其他頻道執行。')
            return
            
        await ctx.defer()
        results = None

        if language is None or language in ('cn', 'chi', 'chinese', 'tw', 'hk', 'hongkong', 'zh', 'taiwan'):
            language = 'zh'
        else:
            language = 'en'


        if search is None:
            # /v2/top-headlines
            results = newsapi.get_top_headlines(#q='bitcoin',
                                                #sources='bbc-news,the-verge',
                                                #category='business',
                                                language=language,
                                                country='hk')
        else:
            # /v2/everything
            results = newsapi.get_everything(q=search,
                                            #sources='bbc-news,the-verge',
                                            #domains='bbc.co.uk,techcrunch.com',
                                            language=language,
                                            sort_by='publishedAt',
                                            page=1)
        for result in results['articles']:

            title = result['title']
            url = result['url']
            urlToImage = result['urlToImage'] if result['urlToImage'] is not None and 'http' in result['urlToImage'] and '://' in result['urlToImage'] else 'https://i.imgur.com/UdkSDcb.png'
            authorName = result['source']['name']
            author = result['author']
            description = result['description']
            publishedAt = result['publishedAt']
            footer = '{}'.format(publishedAt) if author is None else '{}\n{}'.format(author, publishedAt)

            embed = discord.Embed(title=title)

            #url handlings
            if url is not None and 'http' in url and '://' in url:
                url2 = url.rsplit('/',1)[1]
                url1 = url.rsplit('/',1)[0]
                if url2 is not None and url2 != '' and not url2.isalnum():
                    url2 = quote(url2)
                    url = url1 +'/'+ url2
                embed.url = url

            embed.description = description
            embed.set_author(name=authorName, icon_url='https://i.imgur.com/UdkSDcb.png')
            embed.set_thumbnail(url=urlToImage)
            embed.set_footer(text=footer)

            await ctx.send_followup(embed=embed)

    @slash_command(guild_ids=guild_ids, name='stock')
    async def _stock(self, ctx:commands.Context, stock_name):
        """股市圖表"""
        await ctx.defer()

        response = requests.get('https://www.marketwatch.com/tools/quotes/lookup.asp?siteid=mktw&Lookup={}&Country=us&Type=All'.format(stock_name))
        if response.status_code == 200:
            for line in response.content.decode('utf-8').splitlines():
                if '<td class="bottomborder">' in line:
                    stock_name = line.split('<',3)[2].split('>')[-1]
                    break
                if '<span class="company__ticker">' in line:
                    stock_name = line.split('>',1)[1].split('<',1)[0]
                    break

        else:
            await ctx.send_followup("marketwatch連線失敗！？")
            return

        response.close()
        e = discord.Embed()

        # Initialize IO
        data_stream = io.BytesIO()

        data, meta_data = ts.get_intraday(symbol=stock_name,interval='1min', outputsize='full')
        if str(data.head(2)) is not None:
            pass
        else:
            await ctx.send_followup("symbol搜尋失敗！？")
            return
        #ctx.send(str(data.head(2)))

        data = data.drop(columns='5. volume',axis=1)
        data.plot()
        plt.title('Intraday Times Series for the {} stock (1 min)'.format(stock_name))
        plt.grid()
        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()
        #plt.show()

        #create file
        data_stream.seek(0)
        chart = discord.File(data_stream,filename="stock_chart.png")
        data_stream.close()

        e.set_image(
            url="attachment://stock_chart.png"
        )

        await ctx.send_followup(embed=e, file=chart)

    @slash_command(guild_ids=guild_ids, name='cov', aliases=['covid','cov19','covid-19'])
    async def _cov(self, ctx:commands.Context):
        """本港冠狀病毒病的最新情況"""
        await ctx.defer()

        csv_url="http://www.chp.gov.hk/files/misc/latest_situation_of_reported_cases_covid_19_chi.csv"
        response = requests.get(csv_url)

        response.close()
        e = discord.Embed()

        # Initialize IO
        data_stream = io.BytesIO()

        file_object = io.StringIO(response.content.decode('utf-8'))
        pd.set_option('display.max_rows', 60)
        pd.set_option('display.max_columns', None)
        data = pd.read_csv(file_object)

        data = data.tail(60)

        try:
            #data['更新日期'] = data['更新日期'].map(lambda x: datetime.strptime(str(x), '%d/%m/%y'))
            #data['更新日期'] = pd.to_date(data['更新日期'])
            pass
            #df['date'] = pd.to_datetime(df['date'])  
            #print(data['更新日期'])
        except Exception as e:
            await ctx.send_followup('<@{}>\n{}\n{}'.format(bot.owner_id,e,data['更新日期']))
            return
        x = data['更新日期']
        y = data['確診個案']
        y2 = data['死亡']
        y3 = data['出院']
        y4 = data['疑似個案']
        y5 = data['住院危殆個案']
        y6 = data['嚴重急性呼吸綜合症冠狀病毒2的陽性檢測個案']

        plt.plot(x, y, label="confirmed")
        plt.plot(x, y2, label="death")
        plt.plot(x, y3, label="discharge")
        plt.plot(x, y4, label="probable")
        plt.plot(x, y5, label="hospitalised and critical")
        plt.plot(x, y6, label="positive for SARS-CoV-2")
        plt.title("Latest situation of reported cases of COVid-19 in Hong Kong")
        plt.xlabel('past 60 days')
        plt.ylabel('amount')
        plt.gcf().autofmt_xdate()

        #print(data.tail(1))
        plt.legend()
        plt.grid()
        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()

        #create file
        data_stream.seek(0)
        chart = discord.File(data_stream,filename="cov_latest.png")
        data_stream.close()

        e.set_image(
            url="attachment://cov_latest.png"
        )

        latest = data['確診個案'].iloc[-1]
        if latest is None or str(latest) == 'nan':
            latest = data['嚴重急性呼吸綜合症冠狀病毒2的陽性檢測個案'].iloc[-1]

        await ctx.send_followup(content='__確診個案__\n最高: {}\n最低: {}\n平均: {}\n中位: {}\n現時: {}'.format(data['確診個案'].max(), data['確診個案'].min(), data['確診個案'].mean(), data['確診個案'].median(), latest), embed=e, file=chart)


bot = commands.Bot(BOT_PREFIX, description='使用Python的Ben AI，比由Java而成的Ben Kaneki更有效率。', guild_subscriptions=True, intents=discord.Intents.all())
bot.load_extension('Poker')
bot.load_extension('Economy')
bot.load_extension('Betting')
bot.load_extension('Pres')
bot.add_cog(Music(bot))
bot.add_cog(Special(bot))
bot.add_cog(General(bot))
bot.add_cog(Game(bot))

'''@bot.slash_command(name="modaltest1", guild_ids=guild_ids)
async def modal_slash(ctx):
    """Shows an example of a modal dialog being invoked from a slash command."""
    modal = MyModal()
    await ctx.interaction.response.send_modal(modal)'''

@bot.slash_command(name="modaltest", guild_ids=guild_ids)
async def modaltest(ctx):
    """模態demo"""
    #await ctx.delete()
    #await ctx.respond('Completed', ephemeral=True)

    class MyModal(Modal):
        def __init__(self, person) -> None:
            super().__init__(person)
            self.add_item(InputText(label="is", placeholder="gay"))
            self.add_item(
                InputText(
                    label="because",
                    value="gay",
                    style=discord.InputTextStyle.long,
                )
            )
            self.person = person

        async def callback(self, interaction: discord.Interaction):
            embed = discord.Embed(title=self.person, color=discord.Color.random())
            embed.add_field(name="is", value=self.children[0].value, inline=False)
            embed.add_field(name="because", value=self.children[1].value, inline=False)
            await interaction.response.send_message(embeds=[embed])

    class MyView(discord.ui.View):
        person = None
        @discord.ui.button(label="開始評論", style=discord.ButtonStyle.primary, row=4)
        async def button_callback(self, button, interaction):
            if self.person is not None:
                modal = MyModal(self.person)
                await interaction.response.send_modal(modal)

        @discord.ui.select(
            placeholder="評論一條友",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="Pok", description="Pok is"
                ),
                discord.SelectOption(
                    label="Kei", description="Kei is"
                ),
            ],
        )
        async def select_callback(self, select, interaction):
            modal = MyModal(select.values[0])
            #modal.title = select.values[0]
            self.person = select.values[0]
            #await interaction.response.send_modal(modal)

    view = MyView()
    await ctx.interaction.response.send_message(content="\u200b", view=view)

'''@bot.slash_command(name="groups", guild_ids=guild_ids)
async def pagetest_groups(ctx: discord.ApplicationContext):
    """Demonstrates using page groups to switch between different sets of pages."""
    page_buttons = [
        pages.PaginatorButton("first", label="<<-", style=discord.ButtonStyle.green, row=1),
        pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green, row=1),
        pages.PaginatorButton("page_indicator", style=discord.ButtonStyle.gray, disabled=False, row=1),
        pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green, row=1),
        pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green, row=1),
    ]
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Test Button, Does Nothing", row=2))
    view.add_item(
        discord.ui.Select(
            placeholder="Test Select Menu, Does Nothing",
            options=[
                discord.SelectOption(
                    label="Example Option",
                    value="Example Value",
                    description="This menu does nothing!",
                )
            ],
        )
    )
    page_groups = [
        pages.PageGroup(
            pages=get_pages(),
            label="Main Page Group",
            description="Main Pages for Main Things",
            default_button_row=1,
            custom_view=view,
        ),
        pages.PageGroup(
            pages=[
                "Second Set of Pages, Page 1",
                "Second Set of Pages, Page 2",
                "Look, it's group 2, page 3!",
            ],
            label="Second Page Group",
            description="Secondary Pages for Secondary Things",
            custom_buttons=page_buttons,
            use_default_buttons=False,
            custom_view=view,
        ),
    ]
    paginator = pages.Paginator(pages=page_groups, show_menu=True, custom_view=view, default_button_row=1)
    await paginator.respond(ctx.interaction, ephemeral=False)'''

@bot.event
async def on_ready():
    status = "/ | 冇野幫到你"
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))
    gameLoop.start()
    covLoop.start()
    newsLoop.start()
    gamesLoop.start()
    hypebeastLoop.start()
    naLolLoop.start()
    #twLolLoop.start() #Server error 500 24/7
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        seed = randrange(8)
        if seed == 0:
            img = "https://i.imgur.com/UPSOyNB.jpg"
            msg = "**無效的令咒。 請使用** `/` **來找出強制命令！**"
        elif seed == 1:
            msg = "**NANI！？** `/`"
        elif seed == 2:
            msg = "**What 7 command is this ah, use** `/` **la 7 head**"
        elif seed == 3:
            msg = "**JM9? 試下睇下個** `/`"
        elif seed == 4:
            msg = "**Kys, u need some** `/`"
        elif seed == 5:
            msg = "**打咩！！** `/` **！！**"
        elif seed == 6:
            msg = "**Trash... use** `/` **la**"
        elif seed == 7:
            msg = "**都冇呢個指令！！！！！！！ 用** `/` **啦！！！！！！！**"

        if seed == 0:
            e = discord.Embed()
            e.set_image(url=img)
            e.set_footer(text=msg)
            await ctx.send(embed=e)
        else:
            await ctx.send(msg)
    if isinstance(error, commands.MissingRequiredArgument):
        seed = randrange(6)
        if seed == 0:
            msg = "**打漏野呀Ching**"
        if seed == 1:
            msg = "**你漏咗...個腦**"
        if seed == 2:
            msg = "**乜你唔覺得怪怪dick?**"
        if seed == 3:
            msg = "**「行返屋企」，你只係打咗「行返」，我點lung知行返去邊？**"
        if seed == 4:
            msg = "**你食飯未呀？Sor9完全無興趣知，我只知你打漏咗野呀。**"
        if seed == 5:
            msg = "**你係想我fill in the blanks? 填充題？？**"

        await ctx.send(msg)
    if isinstance(error, commands.MissingPermissions):
        seed = randrange(2)
        if seed == 0:
            msg = "**Sor9弱小的你冇權限用呢個指令:angry:**"
        elif seed == 1:
            msg = "**你確定你有lung力用呢個指令？**"

        await ctx.send(msg)

    if isinstance(error, commands.CommandOnCooldown):
        hour = 0
        min = 0
        sec = 0

        while error.retry_after >= 60*60:
            hour += 1
            error.retry_after -= 60*60
        while error.retry_after >= 60:
            min += 1
            error.retry_after -= 60

        sec += error.retry_after

        start = "請於 **"
        end = "** 後再使用。"
        middle = ""

        if hour != 0:
            middle += "{}時".format(hour)
        if min != 0:
            middle += "{}分".format(min)
        if sec != 0:
            middle += "{:.0f}秒".format(sec)

        msg = start+middle+end

        await ctx.send(msg)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.guild is None:
        if not str(message.content).startswith("$") and message.author.id not in temp_blocked_list:
            req_ver_author = message.author
            req_ver_author_id = message.author.id
            req_ver_mc_name = message.content
            req_ver_channel = bot.get_channel(878538264762527744)
            req_ver_reply = bot.get_user(req_ver_author_id)
            req_ver_embed_to_staff = discord.Embed()
            req_ver_embed_to_member = discord.Embed()

            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))

            req_ver_embed_to_staff.set_author(name=req_ver_author.display_name, icon_url=req_ver_author.display_avatar.url)
            #req_ver_embed_to_staff.title = "請求驗證 | Request Verify"
            req_ver_embed_to_staff.title = "已拒絕驗證請求 | Refused Verify"
            #req_ver_embed_to_staff.color = 0x00ff00
            req_ver_embed_to_staff.color = 0xff0000
            req_ver_embed_to_staff.add_field(name="Minecraft", value=req_ver_mc_name, inline=True)
            req_ver_embed_to_staff.add_field(name="Discord", value=req_ver_author, inline=True)
            #req_ver_embed_to_staff.add_field(name="驗證指令", value="Minecraft: `$ver {}`\nDiscord: `$discver @{}`".format(req_ver_mc_name,req_ver_author), inline=False)
            req_ver_embed_to_staff.add_field(name="其他指令", value="發送提醒: `$dm {} \"請輸入提醒\"`\n臨時封鎖: `$block @{}`\n移除封鎖: `$unblock @{}`".format(req_ver_author_id,req_ver_author,req_ver_author), inline=True)
            req_ver_embed_to_staff.set_footer(text=timestamp)

            req_ver_embed_to_member.set_author(name=req_ver_author.display_name, icon_url=req_ver_author.display_avatar.url)
            #req_ver_embed_to_member.title = "Verification"
            req_ver_embed_to_member.title = "Verification (Disabled)"
            #req_ver_embed_to_member.description = "You will be moved to Verified once review completed"
            req_ver_embed_to_member.description = "2019~2021 | End of service: 17Dec2021"
            #req_ver_embed_to_member.color = 0x00ff00
            req_ver_embed_to_member.color = 0xff0000
            req_ver_embed_to_member.add_field(name="Minecraft", value=req_ver_mc_name, inline=True)
            req_ver_embed_to_member.add_field(name="Discord", value=req_ver_author, inline=True)
            req_ver_embed_to_member.set_footer(text=timestamp)

            try:
                await req_ver_reply.send(embed=req_ver_embed_to_member)
            except Exception as e:
                log_channel = bot.get_channel(809527650955296848)
                req_ver_embed_to_staff.description = "無法回覆 {} 請求提交正在處理".format(str(req_ver_author))
                await log_channel.send(str(e))
            else:
                #req_ver_embed_to_staff.description = "已回覆 {} 請求提交正在處理".format(str(req_ver_author))
                req_ver_embed_to_staff.description = "2019~2021 | End of service: 17Dec2021"

            if message.author.id not in dmList:
                await req_ver_channel.send(embed=req_ver_embed_to_staff)
            else:
                await req_ver_channel.send(embed=req_ver_embed_to_staff)

    '''
    if message.guild.id == 671654280985313282 and message.channel == bot.get_channel(910017157675503637):
        logs_channel = bot.get_channel(809527650955296848)
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))

        embed_generated = discord.Embed()
        embed_generated.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed_generated.title = "Suggestion received"
        embed_generated.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
        embed_generated.description = message.content
        embed_generated.set_footer(text=timestamp)

        embed_generated_ind = discord.Embed()
        embed_generated_ind.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed_generated_ind.title = "Suggested sent"
        embed_generated_ind.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
        embed_generated_ind.description = message.content
        embed_generated_ind.add_field(name="Acknowledgement", value="If your suggestion was adopted, it will be shown in #changelog.", inline=False)
        embed_generated_ind.set_footer(text=timestamp)

        embed_generated_public = discord.Embed()
        embed_generated_public.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
        embed_generated_public.title = "Submitted a suggestion"
        embed_generated_public.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
        embed_generated_public.description = "Content sent to staff team directly and privately"
        embed_generated_public.set_footer(text=timestamp)

        await message.channel.send(embed=embed_generated_public)
        await bot.get_channel(910016880029339688).send(embed=embed_generated)
        await message.author.send(embed=embed_generated_ind)
        await logs_channel.send("Suggestion: {} --> {}".format(message.author,message))
        await message.delete()
    '''

    if str(message.content).startswith("$") and len(str(message.content)) > 1:
        if str(message.content).split("$", 1)[1].isnumeric():
            return

    '''if str(message.author.id) in ['407481608560574464','794228652547375104','805046279377387521'] and message.content.startswith('$'):
        author_nick = message.author.display_name

        ai_cheng_embed = discord.Embed()
        ai_cheng_embed.set_image(url='https://i.imgur.com/C1E8ANa.png')

        seed = randrange(3)
        if seed == 0:
            msg = "{}，天蠍AI很記仇的。".format(author_nick)
        elif seed == 1:
            msg = "叫聲爸爸。"
        elif seed == 2:
            msg = "?"

        ai_cheng_embed.set_footer(text=msg)
        await message.channel.send(embed=ai_cheng_embed)
        return'''

    #Delete after execute
    music_command_List = ['/join','/leave','/loop','/now','/pause','/play','/queue','/remove','/resume','/shuffle','/skip','/stop','/summon','/volume',
                          '/j','/disconnect','/v','/current','/playing','/r','/st','/s','/q','/rm','/l','/p',
                          '/stock','/cov','/covid','/cov19','/covid-19']
    casino_command_List = ['/call','/fold','/highest','/pot','/raise',
                           '/bal','/pay','/setbal',
                           '/game','/hand','/in','/out','/rc','/setcolor','/setsort','/start',
                           '/cards','/next',
                           '/ctb','/enter','/pass',
                           '/reward','/bonus','/b','/prize','/rank','/draw']
    minecraft_command_List = ['/bind', '/bound', '/unbind', '/ver', '/discver' '/dm', '/block', '/unblock', '/blocklist']

    '''if message.content.split(' ')[0] in casino_command_List:
        if not DBConnection.checkUserInDB(str(message.author.id)):
            DBConnection.addUserToDB(str(message.author.id))'''

    await bot.process_commands(message)

    '''if (message.content.split(' ')[0] in casino_command_List or message.content.split(' ')[0] in music_command_List or message.content.split(' ')[0] in minecraft_command_List) and \
            not(message.guild is None and message.author != bot.user):
        await message.delete()'''


    #Mentions Ben AI
    if bot.user.mentioned_in(message) and '@everyone' not in message.content and '@here' not in message.content:
        e = discord.Embed()
        seed = randrange(6)
        if seed == 0:
            img = "https://i.imgur.com/CWOMg81.jpg"
            msg = "你就是我的Master嗎"
        elif seed == 1:
            img = "https://i.imgur.com/UatUsA5.jpg"
            msg = "此後吾之劍與Ben同在，Ben之命運與吾共存。"
        elif seed == 2:
            img = "https://i.imgur.com/NeEknCF.jpg"
            msg = "Ben心之所向，即為我劍之所指。"
        elif seed == 3:
            img = "https://i.imgur.com/PzzfeIx.gif"
            msg = "I am the bone of my sword.\n" \
                  "Steel is my body, and fire is my blood.\n" \
                  "I have created over a thousand blades.\n" \
                  "Unknown to death,Nor known to life.\n" \
                  "Have withstood pain to create many weapons.\n" \
                  "Yet, those hands will never hold anything.\n" \
                  "So as I pray, unlimited blade works."
        elif seed == 4:
            img = "https://i.imgur.com/QPMalxQ.jpg"
            msg = "Ben來承認，Ben來允許，Ben來背負整個世界。"
        elif seed == 5:
            img = "https://i.imgur.com/o8EHHMV.gif"
            msg = "輸給誰都可以，但是，決不能輸給自己。"

        e.set_image(url=img)
        e.set_footer(text=msg)
        await message.channel.send(embed=e)

    #Troll
    if '888' in message.content and message.content.startswith('8'):
        seed = randrange(8)
        if seed == 0:
            msg = "8888"
        elif seed == 1:
            msg = "7777"
        elif seed == 2:
            msg = "6666"
        elif seed == 3:
            msg = "9999"
        elif seed == 4:
            msg = "爸爸爸爸"
        elif seed == 5:
            msg = "伯伯伯伯"
        elif seed == 6:
            msg = "八八八八"
        elif seed == 7:
            msg = "西八"

        await message.channel.send(msg, tts=True)

    #Shield
    # if 'ben' in message.content.lower() and 'gay' in message.content.lower():
    #     try:
    #         await message.delete()
    #     except:
    #         pass

    #     if 'ben' in message.author.display_name.lower() or 'ben' in message.author.name.lower():
    #         seed = randrange(5)
    #         if seed == 0:
    #             msg = "Pok is gay"
    #         elif seed == 1:
    #             msg = "Pok is fucking gay"
    #         elif seed == 2:
    #             msg = "Pok guy jai"
    #         elif seed == 3:
    #             msg = "Wow! Jennifer Pok-pez?"
    #         elif seed == 4:
    #             msg = "POKemon鳩"

    #         await message.channel.send(msg)
    #     else:
    #         await message.channel.send(str(message.author.display_name)+" is gay")

@bot.event
async def on_guild_join(guild):
    for member in guild.members:
        if not DBConnection.checkUserInDB(str(member.id)):
            DBConnection.addUserToDB(str(member.id))

@bot.event
async def on_member_join(member):
    if member == bot.user:
        return

    if member.guild.id == 671654280985313282:
        bot_channel_embed_to_staff = discord.Embed()
        bot_channel_embed_to_member = discord.Embed()

        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))

        bot_channel_embed_to_staff.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        bot_channel_embed_to_staff.title = "已加入Discord伺服器"
        bot_channel_embed_to_staff.add_field(name="Discord", value='<@{}>'.format(member.id), inline=True)
        bot_channel_embed_to_staff.set_footer(text=timestamp)

        bot_channel_embed_to_member.set_author(name="Ben's Minecraft Server", icon_url="https://i.imgur.com/NssQKDi.png")
        bot_channel_embed_to_member.title = "Welcome to Ben\'s Minecraft server"
        bot_channel_embed_to_member.set_thumbnail(url="https://i.imgur.com/NssQKDi.png")
        bot_channel_embed_to_member.add_field(name="IP (Survival)", value="mc.benwyw.com", inline=True)
        bot_channel_embed_to_member.add_field(name="Version", value="latest", inline=True)
        bot_channel_embed_to_member.add_field(name="Java & Bedrock", value="Support both Java & Bedrock. Bedrock requires Port `19132`", inline=False)
        bot_channel_embed_to_member.add_field(name="Verify guide", value="Reply this bot with your Minecraft username, please join the server at least once before requesting.", inline=False)
        bot_channel_embed_to_member.add_field(name="In-game guide", value="`/ibooks list` `/ibooks get (book)`", inline=False)
        bot_channel_embed_to_member.add_field(name="Website", value="www.benwyw.com", inline=True)
        bot_channel_embed_to_member.add_field(name="Map", value="map.benwyw.com", inline=True)
        bot_channel_embed_to_member.add_field(name="Instagram", value="ig.benwyw.com", inline=True)
        bot_channel_embed_to_member.set_footer(text=timestamp)

        #wmsg = "Welcome!\n\nTo verify yourself: https://www.benwyw.com/forums/request-verified/\nVerify Guide: https://www.benwyw.com/faq/\n@Staff in-game if you come up with any server related issues.\n\nPublic Relations Team\nBen's Minecraft Server\n\nMinecraft Server IP: mc.benwyw.com\nWebsite: https://www.benwyw.com"
        bot_channel = bot.get_channel(692466531447210105)
        try:
            await member.send(content='2019~2021 | End of service: 17Dec2021', embed=bot_channel_embed_to_member)
            bot_channel_embed_to_staff.description = "歡迎信息發送成功"
            bot_channel_embed_to_staff.color = 0x00ff00
        except Exception as e:
            bot_channel_embed_to_staff.description = "無法發送歡迎信息"
            bot_channel_embed_to_staff.color = 0xff0000
            logs_channel = bot.get_channel(809527650955296848)
            await logs_channel.send(str(e))
        await bot_channel.send(embed=bot_channel_embed_to_staff)

    if member.guild.id == 351742829254410250:
        try:
            pok_channel = bot.get_channel(858022877450600458)
            await pok_channel.send("{} 加入了這個伺服器\n<@{}>".format(member,member.guild.owner.id))
        except:
            pass

    if not DBConnection.checkUserInDB(str(member.id)):
        DBConnection.addUserToDB(str(member.id))

@bot.event
async def on_member_remove(member):
    if member == bot.user:
        return
    if member.guild.id != 351742829254410250:
        return

    try:
        pok_channel = bot.get_channel(858022877450600458)

        await pok_channel.send("{} 離開了這個伺服器\n<@{}>".format(member,member.guild.owner.id))

    except:
        pass

@bot.event
async def on_member_update(before, after):
    if before == bot.user:
        return
    if before.guild.id != 351742829254410250:
        return

    try:
        pok_channel = bot.get_channel(858022877450600458)

        if str(before.nick) != str(after.nick):
            await pok_channel.send("{} 已由 __{}__ 改名至 __{}__".format(before,before.nick,after.nick))

    except:
        pass

@bot.event
async def on_presence_update(before, after):
    if before == bot.user:
        return
    if before.guild.id != 351742829254410250:
        return

    try:
        if str(before.status) in ("online", "offline", "idle", "dnd", "streaming"):
            pok_channel = bot.get_channel(858022877450600458)

            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
            embed = discord.Embed()
            #embed.set_author(name=str(before.display_name), icon_url=before.display_avatar.url)
            #embed.description = '<@{}>'.format(before.id)
            embed.set_footer(text=timestamp)

            if str(before.status) == "offline":
                if str(after.status) in ("online", "idle", "dnd", "streaming"):
                    #embed.title = "已上線"
                    embed.color = 0x00ff00
                    embed.description = '<@{}>已上線'.format(before.id)
                    #embed.set_thumbnail(url="https://i.imgur.com/CUkeFip.png")
                    await pok_channel.send(embed=embed)

            if str(before.status) in ("online", "idle", "dnd", "streaming"):
                if str(after.status) == "offline":
                    #embed.title = "已離線"
                    embed.color = 0xff0000
                    embed.description = '<@{}>已離線'.format(before.id)
                    #embed.set_thumbnail(url="https://i.imgur.com/8tG00SB.png")
                    await pok_channel.send(embed=embed)
    except:
        pass

@bot.event
async def on_raw_message_delete(payload):
    if payload.guild_id != 351742829254410250:
        return

    try:
        pok_channel = bot.get_channel(858022877450600458)
        await pok_channel.send("__信息已被刪除__\n{}".format(payload.cached_message.content))

    except:
        pass

@bot.event
async def on_voice_state_update(member, before, after): # Pok
    # Protection
    if member == bot.user:
        if after.channel is not None and member.voice.self_deaf == False:
            await member.guild.change_voice_state(channel=after.channel, self_deaf=True)
        return
    if member.guild.id != 351742829254410250:
        return

    try:
        pok_channel = bot.get_channel(858022877450600458)

        if before.channel is None and after.channel is not None:
            await pok_channel.send("{} 進入了 __{}__".format(member, after.channel))

        if before.channel is not None and after.channel is not None:
            if before.channel == after.channel:
                await pok_channel.send("{} 在 __{}__ 已靜音或拒聽".format(member, after.channel))
            else:
                await pok_channel.send("{} 由 __{}__ 移入了 __{}__".format(member, before.channel, after.channel))

        if before.channel is not None and after.channel is None:
            await pok_channel.send("{} 離開了 __{}__".format(member, before.channel))

    except:
        pass

    '''if voice_state is not None and len(voice_state.channel.members) == 1 or member == bot.user and after.channel is None:
        # You should also check if the song is still playing
        try:
            await voice_state.disconnect()
            #for task in asyncio.Task.all_tasks(bot.loop):
                #await task.cancel()
            #self.voice_states.get(member.guild.id).audio_player.cancel()
            del self.voice_states[member.guild.id]
        except:
            pass
    else:
        return'''

'''counter = 0

@tasks.loop(minutes=1.0, count=None)
async def my_background_task():
    global counter
    channel = bot.get_channel(123456789) # channel id as an int
    counter += 1
    await channel.send(f'{counter}')
my_background_task.start()'''

try:
    
    load_dotenv()
    bot.owner_id = 254517813417476097
    bot.run(os.getenv('TOKEN'))
except:
    pass
finally:
    try:
        if DBConnection.botDB.is_connected():
            DBConnection.DBCursor.close()
            DBConnection.botDB.close()
    except:
        pass
