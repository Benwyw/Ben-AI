# -*- coding: utf-8 -*-

"""
pip install -U discord.py pynacl youtube-dl
Requires FFmpeg in PATH environment variable or bot's directory
"""
from lib.GlobalImport import *
from cogs.Game import gameLoop
from lib.Loop import *

"""
Commands Start Here
"""

bot.load_extension('lib.game.Poker')
bot.load_extension('lib.game.Economy')
bot.load_extension('lib.game.Betting')
bot.load_extension('lib.game.Pres')
bot.load_extension('cogs.Music') #bot.add_cog(Music(bot))
bot.load_extension('cogs.Special') #bot.add_cog(Special(bot))
bot.load_extension('cogs.General') #bot.add_cog(General(bot))
bot.load_extension('cogs.Game') #bot.add_cog(Game(bot))
bot.load_extension('cogs.CyberSecurity')
bot.load_extension('cogs.Playlist')
bot.load_extension('cogs.Admin')

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
    load_dotenv()
    if os.getenv('TOKEN')[0:3] == 'ODA':
        gameLoop.start()
        #newsLoop.start()
        gamesLoop.start()
        #hypebeastLoop.start()
        naLolLoop.start()
        #covLoop.start()
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
            msg = "**What command is this ah, use** `/` **la**"
        elif seed == 3:
            msg = "** 做咩? 試下睇下個** `/`"
        elif seed == 4:
            msg = "**Wrong command, u need some** `/`"
        elif seed == 5:
            msg = "**打咩！！** `/` **！！**"
        elif seed == 6:
            msg = "**Yo... use** `/` **la**"
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
            msg = "**乜你唔覺得怪怪的?**"
        if seed == 3:
            msg = "**「行返屋企」，你只係打咗「行返」，我點知行返去邊？**"
        if seed == 4:
            msg = "**你食飯未呀？Sor完全無興趣知，我只知你打漏咗野呀。**"
        if seed == 5:
            msg = "**你係想我fill in the blanks? 填充題？？**"

        await ctx.send(msg)
    if isinstance(error, commands.MissingPermissions):
        seed = randrange(2)
        if seed == 0:
            msg = "**Sor弱小的你冇權限用呢個指令:angry:**"
        elif seed == 1:
            msg = "**你確定你有能力用呢個指令？**"

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
async def on_application_command_error(ctx, error):
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
async def on_reaction_add(reaction, user):
    pass
    '''if reaction.message.guild.id == 351742829254410250 and (('pok' in reaction.message.content.lower() and 'pok' in reaction.message.content.lower()) or ('pok' == reaction.message.content.lower())):
        if len(reaction.message.reactions) == 3 and "🇵" in str(reaction.message.reactions) and "🇴" in str(reaction.message.reactions) and "🇰" in str(reaction.message.reactions):
            await reaction.message.add_reaction("🇵")
            await reaction.message.add_reaction("🇴")
            await reaction.message.add_reaction("🇰")'''

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.guild is None:
        if not str(message.content).startswith("$") and message.author.id not in temp_blocked_list:
            user = await getUserById(message.author.id)
            await user.send("DM commands is not available yet, please execute commands within a server.\n私訊指令尚未開放，請使用伺服器頻道。")
            await log(f"{user.display_name} sent a message to bot DM:\n\n{message.content}")
            '''req_ver_author = message.author
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
                await req_ver_channel.send(embed=req_ver_embed_to_staff)'''

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

    '''if str(message.content).startswith("$") and len(str(message.content)) > 1:
        if str(message.content).split("$", 1)[1].isnumeric():
            return'''

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

        seedCategory = randrange(3)
        seed = randrange(6)

        img = None
        img = mentions_List[seedCategory][seed][0]
        msg = mentions_List[seedCategory][seed][1]

        if img is None:
            await log(f'img is None when\nseedCategory: {seedCategory}\nseed: {seed}')
        else:
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

@bot.event
async def on_guild_join(guild):
    # Log
    try:
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
        try:
            await BDS_Log_Channel.send('<@254517813417476097>\nJoined a new server {}\n{}'.format(guild.name,timestamp))
        except Exception as e:
            await BDS_Log_Channel.send('<@254517813417476097>\nError when attempt to send notification for joining a new server\n{}'.format(e))
    except:
        pass
    
    # DB
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
    bot.run(os.getenv('TOKEN'))
except:
    try:
        DBConnection.DBCursor.close()
    except:
        pass
    try:
        DBConnection.botDB.close()
    except:
        pass
'''
finally:
    try:
        DBConnection.DBCursor.close()
        DBConnection.botDB.close()
    except:
        pass
'''