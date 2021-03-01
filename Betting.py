# CARDS BOT
from discord.ext import commands
from DBConnection import DBConnection

import discord
import main
from main import checkInGame, getGame, channelCheck

class Betting(commands.Cog):
    @commands.command(description="提高您的賭注。",
                      brief="提高您的賭注",
                      name='raise',
                      help="將您的賭注提高指定的數量。 該命令的格式為 $raise <amount>。 需要足夠的資金才能使用。",
                      pass_context=True)
    async def __raise(self, ctx, raiseBy: float = None):
        ID = str(ctx.author.id)
        embed = discord.Embed(title="Bet Raise", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        from main import bot
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)

        authorMoney = DBConnection.fetchUserData("userBalance", ID)

        if not checkInGame(ctx.author):
            embed.description = "您不在遊戲中。"
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.send(embed=embed)
            return

        embed.add_field(name="遊戲編號", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "該遊戲尚未開始。"
            embed.set_footer(text="使用 $start 啟動此遊戲。")
            await ctx.send(embed=embed)
            return

        embed.set_footer(text="格式為 $raise <加注金額>。")
        embed.add_field(name="Your Balance", value="$" + str(authorMoney), inline=False)

        if GAME.playerStatus[ID] == "Fold":
            embed.description = "您不參與當前的一手牌。 等待下一個開始。"
            await ctx.send(embed=embed)
            return

        if authorMoney < raiseBy:
            embed.description = "您沒有足夠資金來加注 $" + str(raiseBy) + "."
            await ctx.send(embed=embed)
            return

        if raiseBy + GAME.bets[ID] <= GAME.maxBet:
            embed.add_field(name="當前最高賭注", value="$" + str(GAME.maxBet), inline=False)
            embed.description = "沒有擊敗當前最高的賭注。"
            await ctx.send(embed=embed)
            return

        GAME.bets[ID] += raiseBy
        authorMoney -= raiseBy
        GAME.maxBet = GAME.bets[ID]
        GAME.pot += raiseBy
        DBConnection.updateUserBalance(ID, authorMoney)

        embed.remove_field(1)
        embed.add_field(name="您的新餘額", value="$" + str(authorMoney), inline=False)
        embed.add_field(name="當前最高賭注", value="$" + str(GAME.maxBet), inline=False)
        embed.add_field(name="彩池(Pot)", value="$" + str(GAME.pot))
        embed.description = "你把賭注提高到 $" + str(GAME.bets[ID])

        await ctx.send(embed=embed)

    @__raise.error
    async def raise_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Command Error", description="Invalid arguments detected for command 'raise'. Check $help raise for more details.", color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            from main import bot
            embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
            await ctx.send(embed=embed)

    @commands.command(description="跟注最高賭注。",
                      brief="跟注最高賭注",
                      name='call',
                      help="匹配當前最高賭注。 格式為 $call。 不需要任何參數。 需要足夠的資金才能使用。",
                      pass_context=True)
    async def __call(self, ctx):
        ID = str(ctx.author.id)
        authorMoney = DBConnection.fetchUserData("userBalance", ID)
        embed = discord.Embed(title="賭注", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        from main import bot
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

        embed.add_field(name="遊戲編號", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "該遊戲尚未開始。"
            embed.set_footer(text="使用 $start 啟動此遊戲。")
            await ctx.send(embed=embed)
            return

        embed.set_footer(text="格式為 $raise <加注金額>。")
        embed.add_field(name="Your Balance", value="$" + str(authorMoney), inline=False)

        if GAME.playerStatus[ID] == "Fold":
            embed.description = "您不參與當前的一手牌。 等待下一個開始。"
            await ctx.send(embed=embed)
            return

        embed.add_field(name="當前最高賭注", value="$" + str(GAME.maxBet), inline=False)
        if str(ID) in GAME.bets:
            if GAME.bets[ID] == GAME.maxBet:
                embed.description = "您的下注已經與最高下注匹配。"
                await ctx.send(embed=embed)
                return

        if authorMoney < GAME.maxBet - GAME.bets[ID]:
            embed.description = "您沒有足夠的資金來匹配最高的賭注。"
            await ctx.send(embed=embed)
            return

        if ID in GAME.bets:
            difference = GAME.maxBet - GAME.bets[ID]
            GAME.pot += difference
            GAME.bets[ID] = GAME.maxBet
            authorMoney -= difference
        else:
            GAME.pot += GAME.maxBet
            GAME.bets[ID] = GAME.maxBet
            authorMoney -= GAME.maxBet

        DBConnection.updateUserBalance(ID, authorMoney)

        embed.set_field_at(1, name="Your New Balance", value ="$" + str(authorMoney), inline=False)
        embed.add_field(name="Pot", value="$" + str(GAME.pot))
        embed.description = "您與最高下注 $" + str(GAME.maxBet) + "跟注了。"
        await ctx.send(embed=embed)

    @commands.command(description="放棄您的賭注，放下您的手。",
                      brief="放棄您的賭注",
                      name='fold',
                      help="棄牌棄牌，不再參與。 您將輸掉任何您已經下注的金額。 格式為 $fold。 不需要任何參數。",
                      pass_context=True)
    async def __fold(self, ctx):
        ID = str(ctx.author.id)
        embed = discord.Embed(title="Fold", color=0x00ff00)
        from main import bot
        embed.set_thumbnail(url=bot.get_user(814558209859518555).avatar_url)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        if not checkInGame(ctx.author):
            embed.description = "您不在遊戲中。"
            await ctx.send(embed=embed)
            return

        GAME = getGame(ctx.author)

        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.send(embed=embed)
            return

        embed.add_field(name="遊戲編號", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "該遊戲尚未開始。"
            embed.set_footer(text="使用 $start 啟動此遊戲。")
            await ctx.send(embed=embed)
            return

        GAME.playerStatus[ID] = "Fold"
        embed.description = "你已經蓋牌了。"
        await ctx.send(embed=embed)

    @commands.command(description="View the money in the pot.",
                      brief="View the money in the pot",
                      name='pot',
                      help="看看目前有多少錢可以贏得彩池。 格式為 $pot。 不需要任何參數。",
                      pass_context=True)
    async def __pot(self, ctx):
        embed = discord.Embed(title="Pot", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        from main import bot
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

        embed.add_field(name="遊戲編號", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "該遊戲尚未開始。"
            embed.set_footer(text="使用 $start 啟動此遊戲。")
            await ctx.send(embed=embed)
            return

        embed.description = "彩池當前總值 $" + str(GAME.pot) + "."
        await ctx.send(embed=embed)

    @commands.command(description="檢查當前最高賭注。",
                      brief="查看當前最高賭注",
                      name='highest',
                      help="檢查當前最高賭注是多少。 格式為 $highest。 不需要任何參數。",
                      pass_context=True)
    async def __highest(self, ctx):
        embed = discord.Embed(title="Highest Bet", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        from main import bot
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

        embed.add_field(name="遊戲編號", value=str(GAME.ID), inline=False)
        embed.set_thumbnail(url=GAME.imageUrl)

        if not GAME.gameUnderway:
            embed.description = "該遊戲尚未開始。"
            embed.set_footer(text="使用 $start 啟動此遊戲。")
            await ctx.send(embed=embed)
            return

        embed.description = "當前最高賭注是 $" + str(GAME.maxBet) + "."
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Betting(bot))