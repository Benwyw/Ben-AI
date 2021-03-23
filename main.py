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
import requests

import discord
import youtube_dl
import pandas as pd
from discord.ext import commands
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

#========================Alpha Vantage========================
from alpha_vantage.timeseries import TimeSeries
import matplotlib
import matplotlib.pyplot as plt

#Make plots bigger
matplotlib.rcParams['figure.figsize'] = (20.0, 10.0)

#API Key
load_dotenv()
ts = TimeSeries(key=os.getenv('API_KEY'), output_format='pandas')

#========================Game========================
# Card constants
offset = 10
cardWidth = 138
cardHeight = 210

gameList = []

uncategorized = ['game', 'hand',  'in', 'rc', 'setColor', 'setSort', 'start']

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

# Get a Game object by its 6-digit ID
def getGameByID(ID):
    for GAME in gameList:
        if GAME.ID == ID:
            return GAME

# Check if a Game object exists given a 6-digit ID
def hasGame(ID):
    for GAME in gameList:
        if GAME.ID == ID:
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
    sortType = DBConnection.fetchUserData("sortPref", str(user.id))
    if sortType== 'p':
        ORDER = presOrder
    elif sortType == 's':
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
class Game(commands.Cog):
    @commands.command(description="遊戲幫助指令。",
                      name="cmd",
                      help="顯示遊戲指令表",
                      pass_context=True)
    async def _cmd(self, ctx: commands.Context, param: str = None):
        if param is None:
            embed = discord.Embed(title="新世界 指令表",
                                  description="要查看幫助頁面，只需在$cmd命令後添加頁面編號。 例如：$cmd 3",
                                  color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
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
            embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
            if int(param) == 1:
                commands = bot.get_cog('Betting').get_commands()
                embed.title = "賭注 指令"
                embed.description = "要查看特定指令，請在$cmd命令之後輸入指令名稱。 例如：$cmd raise。"

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 2:
                commands = bot.get_cog('Economy').get_commands()
                embed.title = "經濟 指令"
                embed.description = "要查看特定指令，請在$cmd命令之後輸入指令名稱。 例如：$cmd bal。"

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 3:
                embed.title = "遊戲 指令"
                embed.description = "要查看幫助頁面，只需在$cmd命令後添加頁面編號。 例如：$cmd 3"
                embed.add_field(name="第5頁：德州撲克", value="德州撲克的指令。", inline=False)
                embed.add_field(name="Page 6: 大統領", value="大統領的指令。", inline=False)
                await ctx.send(embed=embed)
            elif int(param) == 4:
                embed.title = "未分類的指令"
                embed.description = "要查看特定指令，請在$cmd命令之後輸入指令名稱。 例如：$cmd raise。"

                for name in uncategorized:
                    command = hasCommandByName(name)
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 5:
                embed.title = "德州撲克指令"
                embed.description = "要查看特定指令，請在 $cmd 命令之後輸入命令名稱。 例如：$cmd rc。"
                commands = bot.get_cog('Poker').get_commands()

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 6:
                embed.title = "大統領指令"
                embed.description = "要查看特定指令，請在 $cmd 命令之後輸入命令名稱。 例如：$cmd rc。"
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
            embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
            await ctx.send(embed=embed)

    @commands.command(description="生成隨機卡。 可能會出現重複項。",
                      name="rc",
                    brief="生成隨機卡",
                    help="該命令從52張卡組中生成一張隨機卡。 格式為 $rc。 不需要任何參數。",
                    pass_context=True)
    async def rc(self, ctx: commands.Context):
        embed = discord.Embed(title="隨機卡", description="", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
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


    '''@commands.command(description="從卡組中拉出許多隨機卡。",
                      name="draw",
                    brief="從牌組中抽出若干張牌",
                    help="從卡組中拉出一些指定的隨機卡。\n"
                         "該指令的格式為 $draw <卡數>.\n 卡數應在1到52之間（含1和52）。",
                    pass_context=True)
    async def draw(self, ctx: commands.Context, cards: int = 1):
        embed = discord.Embed(title="抽卡", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
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


    @commands.command(description="查看您的手。",
                      name="hand",
                    brief="查看你的手",
                    help="查看您手中的卡。 該機器人將為您PM包含您的手的圖像。 格式為 $hand，不帶任何參數。",
                    pass_context=True)
    async def hand(self, ctx: commands.Context):
        embed = discord.Embed(title=ctx.author.name + "'s Hand", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)

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


    @commands.command(description="Set sorting type. Use 'p' for president-style sorting (3 low, 2 high), 'd' for default sorting (A low, K high), 's' for suit sorting (diamonds - spades).",
                      name="setSort",
                    brief="Set sorting type",
                    aliases=['ss'],
                    help="Set your preferred hand sorting style. Format for this command is $setSort <sortType>.\nUse 'p' for president-style 3 lowest, 2 highest sorting.\n "
                         "Use 'd' for default ace low, king high sorting.\n Use 's' for sorting by suit.\n",
                    pass_context=True)
    async def setSort(self, ctx: commands.Context, sortType: str = None):
        embed = discord.Embed(title="排序方式", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
        embed.add_field(name="大統領-樣式 (p)", value="3 - K, A, 2", inline=False)
        embed.add_field(name="默認 (d)", value="A - K", inline=False)
        embed.add_field(name="Suits (s)", value="Ace of Diamonds - King of Spades", inline=False)

        global order, presOrder, ORDER

        if sortType is None:
            embed.description = "沒有提供排序類型。"
            await ctx.send(embed=embed)
            return

        if sortType == "d":
            embed.description = "排序類型設置為默認(d)。"
            ORDER = order
            DBConnection.updateUserSortPref(str(ctx.author.id), sortType)
        elif sortType == "p":
            embed.description = "排序類型設置為“大統領-樣式(p)”。"
            ORDER = presOrder
            DBConnection.updateUserSortPref(str(ctx.author.id), sortType)
        elif sortType == "s":
            embed.description = "排序類型設置為 Suits-Style."
            ORDER = suitOrder
            DBConnection.updateUserSortPref(str(ctx.author.id), sortType)
        else:
            embed.description = "Try 'd', 'p', or 's'."

        await ctx.send(embed=embed)


    @commands.command(description="開始遊戲。",
                      name="game",
                    brief="開始遊戲",
                    aliases=['5card'],
                    help="使用此命令開始新遊戲。 您只能在遊戲之外使用此命令。 格式為 $game，不帶參數。",
                    pass_context=True)
    async def game(self, ctx: commands.Context):
        global gameList

        channelGame = getGameByChannel(ctx.channel)
        if channelGame is not None:
            embed = discord.Embed(title=None, description="該頻道已經有一個活躍的遊戲。", color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name="遊戲編號", value=str(channelGame.ID))
            embed.set_footer(text="使用 $in <遊戲編號> 加入遊戲。")
            await ctx.send(embed=embed)
            return

        if checkInGame(ctx.author):
            embed = discord.Embed(title=None, description="您已經在玩遊戲。", color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return

        emoji1 = '1️⃣'
        #emoji2 = '2️⃣'
        embed = discord.Embed(title="遊戲選擇", description="通過使用給定的表情符號對此消息做出反應來選擇遊戲類型。", color=0x00ff00)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
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
            await ctx.send(embed=discord.Embed(title="遊戲選擇", description="沒有人及時選擇...", color=0x00ff00))
            return
        else:
            if str(rxn[0].emoji) == emoji1:
                ID = randrange(100000, 1000000)
                while hasGame(ID):
                    ID = randrange(100000, 1000000)
                GAME = TexasHoldEm(ctx.channel, ID)
                gameList.append(GAME)
                embed = discord.Embed(title="創建遊戲", description="創建了德州撲克遊戲。", color=0x00ff00)
                embed.add_field(name="遊戲編號", value=str(ID))
                embed.add_field(name="加入", value="$in " + str(ID))
                embed.set_thumbnail(url=GAME.imageUrl)
                await ctx.send(embed=embed)
            '''elif str(rxn[0].emoji) == emoji2:
                ID = randrange(100000, 1000000)
                while hasGame(ID):
                    ID = randrange(100000, 1000000)
                GAME = President(ctx.channel, ID)
                gameList.append(GAME)
                embed = discord.Embed(title="創建遊戲", description="創建了大統領遊戲。", color=0x00ff00)
                embed.add_field(name="遊戲編號", value=str(ID))
                embed.add_field(name="加入", value="$in " + str(ID))
                embed.set_thumbnail(url=GAME.imageUrl)
                await ctx.send(embed=embed)'''


    @commands.command(description="使用6位數字ID參加遊戲。",
                      name="in",
                    brief="加入遊戲。",
                    help="使用其6位數字ID加入現有遊戲。 此命令的格式為 $in <6位數ID>。",
                    pass_context=True)
    async def _in(self, ctx: commands.Context, ID: int = None):
        embed = discord.Embed(title=None, description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)

        if checkInGame(ctx.author):
            embed.description = "您已經在玩遊戲。"
            await ctx.send(embed=embed)
            return

        if ID is None:
            embed.description = "您未提供6位數字的遊戲ID。"
            await ctx.send(embed=embed)
            return

        if not hasGame(ID):
            embed.description = "無效的遊戲ID。"
            await ctx.send(embed=embed)
            return

        if not channelCheck(getGameByID(ID), ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.send(embed=embed)
            return

        GAME = getGameByID(ID)

        if GAME.gameUnderway:
            embed.description = "這場比賽已經在進行中。 您現在不能加入。"
            embed.add_field(name="遊戲編號", value=GAME.ID)
            await ctx.send(embed=embed)
            return

        GAME.players.append(str(ctx.author.id))
        embed.description = "您加入了遊戲。"

        playerList = ""
        for playerID in GAME.players:
            user = bot.get_user(int(playerID))
            playerList += user.name + "\n"

        embed.add_field(name="玩家們", value=playerList)
        embed.add_field(name="遊戲編號", value=GAME.ID)
        embed.set_thumbnail(url=GAME.imageUrl)
        await ctx.send(embed=embed)


    @commands.command(description="離開遊戲，如果遊戲已經在進行中，則放棄任何下注。",
                      name="out",
                    brief="離開您加入的遊戲，如果該遊戲已經在進行中，則放棄任何下注",
                    help="留下您與眾不同的遊戲，從而放棄您已經進行的任何下注。 格式為 $out，不帶任何參數。",
                    pass_context=True)
    async def out(self, ctx: commands.Context):
        embed = discord.Embed(title=None, description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
        if not checkInGame(ctx.author):
            embed.description = "您不在遊戲中。"
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)
        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.send(embed=embed)
            return

        GAME.playerStatus[str(ctx.author.id)] = "Fold"
        GAME.players.remove(str(ctx.author.id))

        embed.description = "您離開了遊戲。"
        embed.add_field(name="遊戲編號", value=str(GAME.ID))
        embed.set_thumbnail(url=GAME.imageUrl)
        await ctx.send(embed=embed)


    @commands.command(description="開始遊戲。",
                      name="start",
                    brief="開始遊戲",
                    help="如果您還沒有開始遊戲，請先開始。 格式為 $start，不帶任何參數。",
                    pass_context=True)
    async def start(self, ctx: commands.Context):
        embed = discord.Embed(title=None, description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
        if not checkInGame(ctx.author):
            embed.description = "您不在遊戲中。"
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)
        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.send(embed=embed)
            return

        if GAME.gameUnderway:
            embed.description = "您的遊戲已經開始。"
            embed.add_field(name="遊戲編號", value=str(GAME.ID))
            embed.set_thumbnail(url=GAME.imageUrl)
            await ctx.send(embed=embed)
            return

        if len(GAME.players) == 1:
            embed.description = "你不能一個人玩！"
            await ctx.send(embed=embed)
            return
        await GAME.startGame()


    @commands.command(description="使用十六進制代碼為您的手設置自定義顏色。",
                      name="setColor",
                    brief="為您的手設置自定義顏色",
                    aliases=['sc', 'setColour'],
                    help="為顯示您的手的圖像設置自定義顏色。 需要格式為＃123ABC的有效顏色十六進制代碼。 格式為 $setColor <十六進制代碼>。",
                    pass_context=True)
    async def setColor(self, ctx: commands.Context, colour: str):
        embed = discord.Embed(title="自定義顏色", description=None, color=0x00ff00)
        embed.set_thumbnail(url="https://i.imgur.com/FCCMHHi.png")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
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
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

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

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

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
                #try:
                #async with timeout(1800):  # 3 minutes
                self.current = await self.songs.get()
                #except asyncio.TimeoutError:
                #self.bot.loop.create_task(self.stop())
                #return

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

    @commands.command(name='join', aliases=['j'], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """我要進來了。"""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
        self.prevmsg = None

    @commands.command(name='summon')
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
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """清除曲列、解除循環播放，離開語音頻道。"""

        if not ctx.voice_state.voice:
            return await ctx.send('未連接到任何語音通道。')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume', aliases=['v'])
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """較大細聲。"""

        if not ctx.voice_state.is_playing:
            return await ctx.send('目前沒有任何播放。')

        if 0 > volume > 100:
            return await ctx.send('音量必須在0到100之間')

        ctx.voice_state.volume = volume / 100
        await ctx.send('播放器音量設置為 {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """顯示目前播緊嘅歌。"""

        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """暫停目前播緊嘅歌。"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume', aliases=['r'])
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """恢復目前播緊嘅歌。"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop', aliases=['st'])
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """停止播放並清除曲列。"""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip', aliases=['s'])
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
        await ctx.message.add_reaction('⏭')
        ctx.voice_state.skip()
    @commands.command(name='queue', aliases=['q'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """顯示曲列。
        您可以選擇指定要顯示的頁面。 每頁包含10個曲目。
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('曲列有堆空氣。')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} 首曲目:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='頁數 {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """洗牌曲列。"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('曲列有堆空氣。')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove', aliases=['rm'])
    async def _remove(self, ctx: commands.Context, index: int):
        """從曲列中刪除指定索引嘅歌曲。"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('曲列有堆空氣。')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop', aliases=['l'])
    async def _loop(self, ctx: commands.Context):
        """循環播放目前播放的歌曲。
        再次使用此指令以解除循環播放。
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('空白一片。')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop:
            await ctx.message.add_reaction('✅')
        elif not ctx.voice_state.loop:
            await ctx.message.add_reaction('❎')

    @commands.command(name='play', aliases=['p'])
    async def _play(self, ctx: commands.Context, *, search: str):
        """播放歌曲。
        如果隊列中有歌曲，它將一直排隊，直到其他歌曲播放完畢。
        如果未提供URL，此指令將自動從各個站點搜索。
        個站點的列表可以喺呢到揾到：https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('處理此請求時發生錯誤: {}'.format(str(e)))
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                if self.prevmsg is not None:
                    await self.prevmsg.delete()
                self.prevmsg = await ctx.send('加咗首 {}'.format(str(source)))

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

class Special(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='rank')
    async def _rank(self, ctx: commands.Context):
        '''查閱全宇宙排行榜 及 你的排名'''

        embed = discord.Embed(title="全宇宙首五名 排行榜",
                              description="根據德州撲克勝場已定。",
                              color=0x00ff00)
        embed.set_thumbnail(url="https://i.imgur.com/1DDTG0z.png")

        rankData = DBConnection.fetchAllRankData()

        count = 1
        for user in rankData:
            tempID = user[0]
            tempWIN = user[1]

            if count <= 5:
                user = await bot.fetch_user(tempID)

                embed.add_field(name="{}. {}".format(count,user.display_name),
                                value="勝場: {}".format(tempWIN), inline=False)

            if int(ctx.author.id) == int(tempID):
                userWin = DBConnection.fetchUserData("userWin", tempID)

                embed2 = discord.Embed(title="你的排名", color=0x00ff00)
                embed2.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                embed2.set_thumbnail(url="https://i.imgur.com/1DDTG0z.png")
                embed2.description = "勝場: {}".format(userWin)
                embed2.add_field(name="全宇宙排行", value="No.{} | 勝場: {}".format(count,tempWIN))

            count += 1

        await ctx.send(embed=embed)
        await ctx.send(embed=embed2)


    @commands.command(name='reward', aliases=['bonus','prize','b','draw'], pass_context=True)
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def _reward(self, ctx: commands.Context):
        '''隨機獎金 $bonus $b'''

        chanceList = [0,1,2,3,4]

        first = str(ctx.author.name)
        middle = "抽中了"

        e = discord.Embed()
        ID = ctx.author.id

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

        oldTotal = DBConnection.fetchUserData("userBalance", ID)

        newTotal = oldTotal + money
        if newTotal <= 0:
            newTotal = 0

        DBConnection.updateUserBalance(ID, newTotal)
        newTotal = DBConnection.fetchUserData("userBalance", ID)

        msg = first+" "+middle+end

        e.set_image(url=img)
        e.set_author(name=msg, url=e.Empty, icon_url=e.Empty)
        e.set_footer(text="{}得到了 ${} | ${} --> ${}".format(first,money,oldTotal,newTotal))
        await ctx.send(embed=e)

    @commands.command(name='announce')
    @commands.is_owner()
    async def _announce(self, ctx: commands.Context, message):
        '''特別指令。公告。'''

        #client.get_channel("182583972662")
        for guild in bot.guilds:
            await guild.text_channels[0].send(message)

    @commands.command(name='status')
    @commands.is_owner()
    async def _status(self, ctx: commands.Context, status):
        '''特別指令。更改狀態。'''

        if status != "reset":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="$help | {}".format(status)))
        else:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="$help | 冇野幫到你"))

    @commands.command(name='dm')
    @commands.is_owner()
    async def _dm(self, ctx: commands.Context, target, content):
        """特別指令。同Bot DM，會由Bot DM Ben。"""

        target = target.lower()

        if 'ben' in target:
            memberID = 254517813417476097
        elif 'ronald' in target:
            memberID = 525298794653548751
        elif 'chris' in target:
            memberID = 562972196880777226
        elif 'anson' in target:
            memberID = 199877205071888384
        elif 'andy' in target:
            memberID = 407481608560574464

        elif 'pok' in target:
            memberID = 346518519015407626
        elif 'chester' in target:
            memberID = 349924747686969344
        elif 'daniel' in target:
            memberID = 270781455678832641
        elif 'kei' in target:
            memberID = 363347146080256001
        elif 'olaf' in target:
            memberID = 272977239014899713
        elif 'brian' in target:
            memberID = 262267347379683329
        elif 'blue' in target:
            memberID = 394354007650336769
        elif 'nelson' in target:
            memberID = 372395366986940416
        elif 'ivan' in target:
            memberID = 269394999890673664
        else:
            memberID = int(target)

        person = bot.get_user(memberID)
        try:
            await person.send(content)
        except Exception as e:
            channel = bot.get_channel(809527650955296848)
            await ctx.send("Unable to send message to: "+str(person))
            await channel.send(str(e))
        else:
            await ctx.send("Sent a message to: "+str(person))

    @commands.command(name='menu')
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

        message = await ctx.send(embed = page1)

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

    @commands.command(name='chest')
    async def _chest(self, ctx: commands.Context, code, key):
        """$chest CivilCodeMenu網址 關鍵字"""

        response = requests.get(code)
        if response.status_code == 200:
            for line in response.content.decode('utf-8').splitlines():
                if 'pdfIcon after' in line:
                    pdf_url = line.split("=\"")[1].split("\" class")[0].replace("../../../../","https://www.bd.gov.hk/")

                    pdfFile = parser.from_file(pdf_url)

                    if key.lower() in str(pdfFile["content"]).lower():
                        await ctx.send("在 {} 找到 {}".format(pdf_url,key))

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='hello')
    async def _hello(self, ctx: commands.Context):
        '''Say Hello to the AI'''

        await ctx.send("你好呀 "+str(ctx.author.display_name))

    @commands.command(name='ping')
    async def _ping(self, ctx: commands.Context):
        '''Ping爆佢!!!'''

        if len(ctx.message.mentions) == 0:
            await ctx.send("我唔會Ping: 空氣 / 其他Bot")
        else:
            embed = discord.Embed()
            embed.set_author(name="{} 揾你".format(ctx.author.display_name))
            for count in range(10):
                await ctx.send("<@{}>".format(ctx.message.mentions[0].id))
                await ctx.send(embed=embed)

    @commands.command(name='stock')
    async def _stock(self, ctx:commands.Context, stock_name):
        """股市圖表"""
        tempmsg = await ctx.send("處理資料中...")

        response = requests.get('https://www.marketwatch.com/tools/quotes/lookup.asp?siteID=mktw&Lookup={}&Country=us&Type=All'.format(stock_name))
        if response.status_code == 200:
            for line in response.content.decode('utf-8').splitlines():
                if '<td class="bottomborder">' in line:
                    stock_name = line.split('<',3)[2].split('>')[-1]
                    break
                if '<span class="company__ticker">' in line:
                    stock_name = line.split('>',1)[1].split('<',1)[0]
                    break

        else:
            ctx.send("marketwatch連線失敗！？")

        response.close()
        e = discord.Embed()

        # Initialize IO
        data_stream = io.BytesIO()

        data, meta_data = ts.get_intraday(symbol=stock_name,interval='1min', outputsize='full')
        if str(data.head(2)) is not None:
            pass
        else:
            ctx.send("symbol搜尋失敗！？")
        #ctx.send(str(data.head(2)))

        data = data.drop('5. volume',1)
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

        await tempmsg.delete()
        await ctx.send(embed=e, file=chart)

    @commands.command(name='cov', aliases=['covid','cov19','covid-19'])
    async def _cov(self, ctx:commands.Context):
        """本港冠狀病毒病的最新情況"""
        tempmsg = await ctx.send("從data.gov.hk獲取資料中...")

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
            data['更新日期'] = data['更新日期'].map(lambda x: datetime.strptime(str(x), '%d/%m/%y'))
        except:
            pass
        x = data['更新日期']
        y = data['確診個案']
        y2 = data['死亡']
        y3 = data['出院']
        y4 = data['疑似個案']
        y5 = data['住院危殆個案']

        plt.plot(x, y, label="confirmed")
        plt.plot(x, y2, label="death")
        plt.plot(x, y3, label="discharge")
        plt.plot(x, y4, label="probable")
        plt.plot(x, y5, label="hospitalised and critical")
        plt.title("Latest situation of reported cases of COVID-19 in Hong Kong")
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

        await tempmsg.delete()
        await ctx.send(embed=e, file=chart)


bot = commands.Bot(BOT_PREFIX, description='使用Python的Ben AI，比由Java而成的Ben Kaneki更有效率。', intents=discord.Intents.all())
bot.add_cog(Music(bot))
bot.add_cog(Special(bot))
bot.add_cog(General(bot))
bot.add_cog(Game(bot))


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="$help | 冇野幫到你"))
    gameLoop.start()
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        seed = randrange(8)
        if seed == 0:
            img = "https://i.imgur.com/UPSOyNB.jpg"
            msg = "**無效的令咒。 請使用** `$help` **來找出強制命令！**"
        elif seed == 1:
            msg = "**NANI！？** `$help`"
        elif seed == 2:
            msg = "**What 7 command is this ah, use** `$help` **la 7 head**"
        elif seed == 3:
            msg = "**JM9? 試下睇下個** `$help`"
        elif seed == 4:
            msg = "**Kys, u need some** `$help`"
        elif seed == 5:
            msg = "**打咩！！** `$help` **！！**"
        elif seed == 6:
            msg = "**Trash... use** `$help` **la**"
        elif seed == 7:
            msg = "**都冇呢個指令！！！！！！！ 用** `$help` **啦！！！！！！！**"

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
    if message.guild is None and message.author != bot.user and message.author != bot.get_user(254517813417476097):
        #await channel.send("{}: {}".format(message.author,message.content))
        if message.author.id not in dmList:
            await bot.get_user(254517813417476097).send("{}({}): {}".format(message.author,message.author.id,message.content))
        else:
            await bot.get_user(254517813417476097).send("{}: {}".format(message.author,message.content))

    if message.author == bot.user:
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
    music_command_List = ['$join','$leave','$loop','$now','$pause','$play','$queue','$remove','$resume','$shuffle','$skip','$stop','$summon','$volume',
                          '$j','$disconnect','$v','$current','$playing','$r','$st','$s','$q','$rm','$l','$p',
                          '$stock','$cov','$covid','$cov19','$covid-19']
    casino_command_List = ['$call','$fold','$highest','$pot','$raise',
                           '$bal','$pay','$setbal',
                           '$game','$hand','$in','$out','$rc','$setColor','$setSort','$start',
                           '$cards','$next',
                           '$ctb','$enter','$pass',
                           '$reward','$bonus','$b','$prize','$rank','$draw']

    if message.content.split(' ')[0] in casino_command_List:
        if not DBConnection.checkUserInDB(str(message.author.id)):
            DBConnection.addUserToDB(str(message.author.id))

    await bot.process_commands(message)

    if message.content.split(' ')[0] in casino_command_List or message.content.split(' ')[0] in music_command_List:
        await message.delete()


    #Mentions Ben AI
    if bot.user.mentioned_in(message) and message.content not in ('@everyone','@here'):
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
    if 'ben' in message.content.lower() and 'gay' in message.content.lower():
        try:
            await message.delete()
        except:
            pass

        if 'ben' in message.author.display_name.lower() or 'ben' in message.author.name.lower():
            seed = randrange(5)
            if seed == 0:
                msg = "Pok is gay"
            elif seed == 1:
                msg = "Pok is fucking gay"
            elif seed == 2:
                msg = "Pok guy jai"
            elif seed == 3:
                msg = "Wow! Jennifer Pok-pez?"
            elif seed == 4:
                msg = "POKemon鳩"

            await message.channel.send(msg)
        else:
            await message.channel.send(str(message.author.display_name)+" is gay")

@bot.event
async def on_guild_join(guild):
    for member in guild.members:
        if not DBConnection.checkUserInDB(str(member.id)):
            DBConnection.addUserToDB(str(member.id))

'''counter = 0

@tasks.loop(minutes=1.0, count=None)
async def my_background_task():
    global counter
    channel = bot.get_channel(123456789) # channel id as an int
    counter += 1
    await channel.send(f'{counter}')
my_background_task.start()'''

try:
    bot.load_extension('Poker')
    bot.load_extension('Economy')
    bot.load_extension('Betting')
    bot.load_extension('Pres')
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