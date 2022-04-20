# Work with Python 3.6
# USED IMPORTS
from discord.ext import commands
from DBConnection import DBConnection
import discord.ext.commands
from discord.ext.commands import Bot, has_permissions, CheckFailure

from globalImport import *

imgUrl = "https://i.imgur.com/ydS4u8P.png"

class Economy(commands.Cog):
    @slash_command(guild_ids=guild_ids, description="Check user balance.",
                      brief="Check user balance",
                      name="bal",
                      help="Check a user's balance. Mention a user to check their balance, or none to check your own. Format is $bal <mention user/none>.",
                      pass_context=True)
    async def bal(self, ctx, user: discord.Member = None):
        await ctx.defer()
        if user is None:
            user = ctx.author
        temp = DBConnection.checkUserInDB(str(user.id))
        if not temp:
            DBConnection.addUserToDB(str(user.id))
        money = DBConnection.fetchUserData("userBalance", str(user.id))
        embed = discord.Embed(title="用戶餘額", color=0x00ff00)
        embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=imgUrl)
        embed.description = "$" + str(money)
        await ctx.send_followup(embed=embed)

    @bal.error
    async def bal_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Command Error", color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=imgUrl)
            embed.description = "Invalid user provided."
            embed.set_footer(text="Mention a user to check their balance.")
            await ctx.send(embed=embed)

    @slash_command(guild_ids=guild_ids, description="Set money for user. Requires administrator permissions.",
                      brief="Set money for user",
                      name="setbal",
                      help="Set the balance of a user to a specified value. Requires administrator permissions for use. Mention a user to"
                           " set their balance. Format is $setbal <mention user> <balance amount>.",
                      pass_context=True)
    @commands.is_owner()
    #@commands.check_any(commands.has_permissions(administrator=True), commands.is_owner())
    async def setbal(self, ctx, user: discord.Member = None, amount: float = None):
        await ctx.defer()
        embed = discord.Embed(title="Set User Balance", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=imgUrl)

        if amount is None or user is None:
            embed.description = "指令格式無效。 嘗試 $setbal <提及用戶> <金額>。"
            await ctx.send(embed=embed)
            return

        DBConnection.updateUserBalance(str(user.id), amount)

        embed.description = user.display_name + " 的餘額已設置為 $" + str(amount) + "."
        await ctx.send_followup(embed=embed)

    @setbal.error
    async def setbal_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="Command Error",
                                  description="Invalid arguments detected for command 'setbal'. Check $help setbal for more details.",
                                  color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=imgUrl)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="權限錯誤",
                                  description="您無權使用此指令。",
                                  color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=imgUrl)
            await ctx.send(embed=embed)

    @slash_command(guild_ids=guild_ids, description="Pay a user.",
                      brief="Pay a user",
                      name="pay",
                      help="Pay a user from your own balance. You must have sufficient funds to pay the value you specified. Mention"
                           " the user who you'd like to pay. Format is $pay <mention user> <payment amount>.",
                      pass_context=True)
    async def pay(self, ctx, user: discord.Member = None, amount: float = None):
        await ctx.defer()
        embed = discord.Embed(title="支付", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=imgUrl)
        if user is None:
            embed.description = "沒有提供收款人。"
            await ctx.send_followup(embed=embed)
            return

        if user == ctx.author:
            embed.description = "俾錢自己JM9"
            await ctx.send_followup(embed=embed)
            return

        if amount is None:
            embed.description = "沒有提供金額。"
            await ctx.send_followup(embed=embed)
            return

        if amount <= 0:
            embed.description = "付款必須大於 $0。"
            await ctx.send_followup(embed=embed)
            return

        authorMoney = DBConnection.fetchUserData("userBalance", str(ctx.author.id))
        recipientMoney = DBConnection.fetchUserData("userBalance", str(user.id))

        if amount > authorMoney:
            embed.description = "付款資金不足。"
            embed.add_field(name="您的餘額", value="$" + str(authorMoney))
            await ctx.send_followup(embed=embed)
            return

        authorMoney -= amount
        recipientMoney += amount
        DBConnection.updateUserBalance(str(ctx.author.id), authorMoney)
        DBConnection.updateUserBalance(str(user.id), recipientMoney)

        embed.description = "付了 $" + str(amount) + " 予 " + user.display_name + "."
        embed.add_field(name="您的新餘額", value="$" + str(authorMoney))
        embed.add_field(name=user.display_name + "的新餘額", value="$" + str(recipientMoney), inline=False)
        await ctx.send_followup(embed=embed)

    @pay.error
    async def pay_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(title="指令錯誤", color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=imgUrl)
            embed.description = "檢測到指令為 \'pay\' 的無效參數。 嘗試 $pay <提及用戶> <金額>"
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))