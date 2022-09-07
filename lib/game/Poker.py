# Work with Python 3.6
# USED IMPORTS
from lib.GlobalImport import *
from random import randrange
import asyncio
import discord
from discord.ext import commands
import discord.ext.commands
from discord.ext.commands import Bot, has_permissions, CheckFailure
from discord.ext import tasks
import json
import sys
import io
from timeit import default_timer as timer
from PIL import Image, ImageDraw, ImageColor

from cogs.Game import *

def betCheck(GAME):
    needToMatch = []
    for player, status in GAME.playerStatus.items():
        if status == "Active":
            needToMatch.append(player)
    return needToMatch


class Poker(commands.Cog):
    poker = SlashCommandGroup(guild_ids=guild_ids, name="poker", description='Poker', description_localizations={"zh-TW": "撲克"})

    @poker.command(guild_ids=guild_ids, name="next", description="在德州撲克中抽下一張卡片。",
                      brief="在德州撲克中抽下一張卡片",
                      help="在德州撲克遊戲中分發下一張檯上卡片。 您必須參與德州撲克才能使用此指令。",
                      pass_context=True)
    async def next(self, ctx):

        await ctx.defer()

        embed = discord.Embed(colour=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)

        if not checkInGame(ctx.author):
            embed.description = "您沒有參加任何遊戲。"
            embed.set_footer(text="使用 /in <遊戲ID> 來加入現有遊戲。")
            await ctx.send_followup(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.send_followup(embed=embed)
            return

        if not isinstance(GAME, TexasHoldEm):
            embed.add_field(name="遊戲編號", value=str(GAME.ID))
            embed.description = "您不在德州撲克遊戲中。"
            await ctx.send_followup(embed=embed)
            return

        embed.set_thumbnail(url=TexasHoldEm.imageUrl)
        embed.title = "德州撲克"

        if not GAME.gameUnderway:
            embed.add_field(name="遊戲編號", value=str(GAME.ID))
            embed.description = "該遊戲尚未開始。"
            embed.set_footer(text="使用 /start 啟動此遊戲。")
            await ctx.send_followup(embed=embed)
            return

        if GAME.playerStatus[str(ctx.author.id)] == "Fold":
            embed.add_field(name="Game ID", value=str(GAME.ID))
            embed.description = "您沒有參與這手牌。 等待下一隻手開始。"
            await ctx.send_followup(embed=embed)
            return

        if len(GAME.communityCards) >= 5 and GAME.lastBet is True:
            return

        embed.set_author(name="", icon_url="")
        embed.set_footer(text="使用 /out 退出此遊戲。")
        needToMatch = betCheck(GAME)
        me = bot.get_user(814558209859518555)
        file = showHand(ctx.author, GAME.communityCards)
        embed.set_image(url="attachment://hand.png")

        if len(needToMatch):
            embed.description = "並非所有玩家都匹配最高下注或棄牌。"
            playersToMatch = ""
            for ID in needToMatch:
                user = bot.get_user(int(ID))
                playersToMatch += user.name + "\n"

            embed.add_field(name="需要跟注(Call)/蓋牌(Fold)", value=playersToMatch)
            embed.add_field(name="彩池(Pot)", value="$" + str(GAME.pot))
            embed.add_field(name="遊戲編號", value=str(GAME.ID))
            embed.add_field(name="檯上卡片", value="已發的牌: " + str(len(GAME.communityCards)), inline=False)

            await ctx.send_followup(file=file, embed=embed)
            return
        if len(GAME.communityCards) == 0:
            GAME.deal(bot.get_user(814558209859518555), 3)
            embed.description = "頭三張卡發了。"
        elif len(GAME.communityCards) < 5:
            GAME.deal(me, 1)
        file = showHand(bot.get_user(814558209859518555), GAME.communityCards)
        embed.set_image(url="attachment://hand.png")

        playerList = ""

        for playerID in GAME.players:
            user = bot.get_user(int(playerID))
            playerList += user.name + "\n"

        if len(GAME.communityCards) == 5 and GAME.pre_lastBet is True:
            embed.description = "回合結束，露出所有玩家的手..."
            GAME.lastBet = True
        elif len(GAME.communityCards) == 5:
            GAME.pre_lastBet = True
        elif len(GAME.communityCards) > 3:
            embed.description = "下一張卡發了。"
        embed.add_field(name="玩家們", value=playerList)
        embed.add_field(name="彩池(Pot)", value="$" + str(GAME.pot))
        embed.add_field(name="遊戲編號", value=str(GAME.ID))
        embed.add_field(name="檯上卡片", value="已發的牌: " + str(len(GAME.communityCards)), inline=False)

        await ctx.send_followup(file=file, embed=embed)

    @poker.command(guild_ids=guild_ids, name="cards", description="出示檯上卡片。",
                      brief="出示檯上卡片",
                      help="顯示德州撲克遊戲的當前已發的檯上卡片。 您必須在德州撲克遊戲中才能使用此指令。",
                      pass_context=True)
    async def cards(self, ctx):
        embed = discord.Embed(colour=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)

        if not checkInGame(ctx.author):
            embed.description = "您沒有參加任何遊戲。"
            embed.set_footer(text="使用 /in <遊戲ID> 來加入現有遊戲。")
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.send(embed=embed)
            return

        if not isinstance(GAME, TexasHoldEm):
            embed.add_field(name="遊戲編號", value=str(GAME.ID))
            embed.description = "您不在德州撲克遊戲中。"
            await ctx.send(embed=embed)
            return

        embed.set_thumbnail(url=TexasHoldEm.imageUrl)
        embed.title = "德州撲克"

        if not GAME.gameUnderway:
            embed.add_field(name="遊戲編號", value=str(GAME.ID))
            embed.description = "該遊戲尚未開始。"
            embed.set_footer(text="使用 /start 啟動此遊戲。")
            await ctx.send(embed=embed)
            return

        embed.set_author(name="", icon_url="")
        file = showHand(bot.get_user(814558209859518555), GAME.communityCards)
        embed.set_image(url="attachment://hand.png")

        playerList = ""

        for playerID in GAME.players:
            user = bot.get_user(int(playerID))
            playerList += user.name + "\n"

        embed.add_field(name="玩家們", value=playerList)
        embed.add_field(name="彩池(Pot)", value="$" + str(GAME.pot))
        embed.add_field(name="遊戲編號", value=str(GAME.ID))
        embed.add_field(name="檯上卡片", value="已發的牌: " + str(len(GAME.communityCards)), inline=False)

        await ctx.send(file=file, embed=embed)
  
def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Poker(bot))
