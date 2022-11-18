from lib.GlobalImport import *

class Special(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.thumbnail_dict = {
            "ARAM": "https://i.imgur.com/tsJ59Fg.png",
            "Apex": "https://i.imgur.com/0fF6EkT.png",
            "Minecraft": "https://i.imgur.com/Rc6f19X.png"
        }
    
    mc = SlashCommandGroup(guild_ids=guild_ids, name="mc", description='Minecraft', description_localizations={"zh-TW": "當個創世神"})
    ask = SlashCommandGroup(guild_ids=guild_ids, name="ask", description='Ask', description_localizations={"zh-TW": "問"})
    report = SlashCommandGroup(guild_ids=guild_ids, name="report", description='Report', description_localizations={"zh-TW": "報告"})
        
    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

    '''
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner'))
    @slash_command(guild_ids=[guild_BenKaChu], name='kickallfromben', description='Kick all from Minecraft server')
    async def _kickallfromben(self, ctx: commands.Context):
        await ctx.defer()
        print('Executing kickallfromben...')

        counter = 0
        protect_ids = [254517813417476097, 232833713648435200, 809526579389792338]
        protected_names = '保護名單:'
        ben_home_text_channel = bot.get_channel(918890234459090984)
        kicked_members = '已踢除名單:'

        ben_guild = bot.get_guild(671654280985313282)
        for member in ben_guild.members:
            if protect_ids is not None and member.id in protect_ids:
                protected_names += '\n{}'.format(member)
            else:
    '''
    '''
    roleList = None
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))

    for role in member.roles:
        if ('everyone' not in role.name):
            if roleList is None:
                roleList = role.name
            else:
                roleList += ' | {}'.format(role.name)

    embed = discord.Embed()
    embed.url = "https://www.benwyw.com/"
    embed.title = "End of service"
    embed.description = "28Feb2022 (Discord) | 17Dec2021 (Minecraft)"
    embed.set_author(name='Ben\'s Minecraft Server', icon_url='https://i.imgur.com/NssQKDi.png')
    embed.set_thumbnail(url="https://i.imgur.com/a4aDhEm.png")
    embed.add_field(name="Your user roles", value=roleList, inline=False)
    embed.add_field(name="Instagram", value='@mcbenwywcom', inline=True)
    embed.set_footer(text=timestamp)

    person = member
    try:
        await person.send(content='End of service, thank you for your support.\n服務結束，感謝您的支持。', embed=embed)
    except Exception as e:
        await ctx.send_followup("無法傳訊至: "+str(person))
        await ben_home_text_channel.send(str(e))
    else:
        await ctx.send_followup("成功傳訊至: "+str(person))
    '''
    '''
                try:
                    await member.kick(reason='End of service, 28Feb2022 (Discord) | 17Dec2021 (Minecraft)')
                except Exception as e:
                    await ctx.send_followup("無法踢除: "+str(member))
                    await ben_home_text_channel.send(str(e))
                else:
                    await ctx.send_followup("成功踢除: "+str(member))
                kicked_members += '\n{}'.format(member)
                counter += 1
        
        await ctx.send_followup('{}'.format(protected_names))
        await ctx.send_followup('{}'.format(kicked_members))
        await ctx.send_followup('在 {} 已踢除 {} 位非受保護成員'.format(ben_guild, counter))

        print('Completed execution of kickallfromben.')
    '''

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

    '''@mc.command(guild_ids=guild_ids, name='log', description='Change log release')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    async def log(self, ctx: commands.Context, message):
        
        if ctx.channel.id == 692466531447210105:

            #timezone
            tz = pytz.timezone('Asia/Hong_Kong')
            hk_now = datetime.now(tz)
            timestamp = str(hk_now)

            #channels
            changelog_channel = bot.get_channel(903541645411237889)

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
                await log(str(e))
                return

            #response embed
            embed = discord.Embed()
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.title = "已發布變更日誌"
            embed.description = str(message)
            embed.set_footer(text=timestamp)

            #send reponse
            await ctx.respond(embed=embed)
            await log("Changelog: {} --> {}".format(ctx.author,message))
        else:
            await ctx.respond("請去 <#692466531447210105>")'''

    @slash_command(guild_ids=guild_ids, name='getserver')
    async def _getserver(self, ctx: commands.Context, code):
        '''在__私訊__收到 play.benwyw.com 既 Private Server 資訊'''
        
        await ctx.defer()

        game = ""
        port = ""
        remarks = ""
        password = ""
        status = ""

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

    @mc.command(guild_ids=guild_ids, name='bind')
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

    @mc.command(guild_ids=guild_ids, name='unbind')
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

    @mc.command(guild_ids=guild_ids, name='bound')
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

        '''print(draw_List[seed])
        print(draw_List[seed][0])
        print(draw_List[seed][1])
        print(draw_List[seed][2])
        img = draw_List[seed][0]
        end= draw_List[seed][1]
        money = draw_List[seed][2]'''
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
            '''if mc.status() == 'online':
                await log('inside mc status')
                await console_channel.send("eco give {} {}".format(mc_Username, money))
                await serverchat_channel.send("{} received ${} from per-10 mins lucky draw '/draw'!".format(mc_Username, money))
                mc_content_1 = "\n{}得到了 ${}".format(mc_Username,money)
                await log(mc_content_1)
                if mc.status_seasonal() == 'online':
                    await log('inside seasonal')
                    await console_seasonal_channel.send("!cmd say {} received ${} from per-10 mins lucky draw '/draw'!".format(mc_Username, money))
            else:'''
            mc_content_1 = "\nServer is offline"
        else:
            mc_content_1 = "\n尚未綁定伺服器 /bind"

        mc_content_2 = "\nmc.benwyw.com | play.benwyw.com"
        mc_content = mc_content_1 + mc_content_2

        final_content = default_content + mc_content

        e.set_footer(text=final_content)

        await ctx.send_followup(embed=e)

    '''@slash_command(guild_ids=guild_ids, name='block', description='特別指令。Temp block verification request。')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _tempblk(self, ctx: commands.Context, message):
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

            await req_ver_channel.send(embed=req_ver_embed_to_staff)'''

    '''@slash_command(guild_ids=guild_ids, name='unblock', description='特別指令。Unblock verification request。')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _unblk(self, ctx: commands.Context, message):
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

            await req_ver_channel.send(embed=req_ver_embed_to_staff)'''

    '''@mc.command(guild_ids=guild_ids, name='blocklist', description='特別指令。Unblock verification request。')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _blklist(self, ctx: commands.Context):
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
            await ctx.send_followup('請去 <#878538264762527744> 或 <#692466531447210105>')'''

    '''@mc.command(guild_ids=guild_ids, name='dm', description='特別指令。Bot DM for Minecraft Staff usage。')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _dm(self, ctx: commands.Context, target, content):
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
            await ctx.send_followup('請去 <#878538264762527744> 或 <#692466531447210105>')'''

    '''@mc.command(guild_ids=guild_ids, name='ver', description='特別指令。驗證玩家Minecraft。')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _ver(self, ctx: commands.Context, message):
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
            await ctx.respond('請去 <#878538264762527744> 或 <#692466531447210105>')'''

    '''@mc.command(guild_ids=guild_ids, name='discver', description='特別指令。驗證玩家Discord。')
    @commands.check_any(commands.is_owner(), commands.has_any_role('Owner', 'Co-Owner', 'Manager', 'Public Relations Team', 'Discord Staff'))
    @is_in_guild(671654280985313282)
    async def _discver(self, ctx: commands.Context, message):
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

            await req_ver_channel.send(embed=req_ver_embed_to_staff)'''

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

    # Disabled, require JVM environment
    '''@slash_command(guild_ids=guild_ids, name='chest')
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
            await ctx.send_followup('Response.status_code != 200. <@{}>'.format(bot.owner_id))'''

    @ask.command(guild_ids=guild_ids, name='ping')
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

    async def create_ask_embed(self, ctx, target_user, purpose:str, thumbnail:str=None, ask_type:str=None):
        title = f"玩唔玩{purpose}呀?"
        if ask_type is not None:
            title = f"{ask_type}唔{ask_type}{purpose}呀?"

        thumbnail_url = thumbnail
        if purpose in self.thumbnail_dict and thumbnail is None:
            thumbnail_url = self.thumbnail_dict[purpose]

        embed = discord.Embed(title=title)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.description = f'<@{ctx.author.id}> <:arrow_right:1016253447638618183> <@{target_user.id}>'
        if thumbnail_url is not None:
            embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text=get_timestamp())

        return embed

    async def create_desc_embed(self, target_user, desc:str):
        embed = discord.Embed(description=f"<@{target_user.id}> {desc}")
        return embed

    async def process_ask_embed(self, ctx, target_user, purpose, thumbnail=None, ask_type=None):
        await ctx.defer()
        embed_to_target_user = await self.create_ask_embed(ctx, target_user, purpose, thumbnail, ask_type)

        try:
            target_user_msg = await target_user.send(embed=embed_to_target_user)
        except Exception as e:
            embed_except = discord.Embed(description=f"無法傳信息至 <@{target_user.id}>")
            await ctx.send_followup(embed=embed_except)
            return
        channel_msg = await ctx.send_followup(embed=embed_to_target_user)
        await ctx.send_followup('正等待回覆...(1分鐘)')

        confirmEmoji = '👍'
        quitEmoji = '👎'
        await target_user_msg.add_reaction(confirmEmoji)
        await target_user_msg.add_reaction(quitEmoji)

        def check(reaction, user):
                global rxn
                rxn = reaction
                return user.id == target_user.id and not user.bot

        try:
            rxn = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await target_user_msg.remove_reaction(confirmEmoji, bot.user)
            await target_user_msg.remove_reaction(quitEmoji, bot.user)
            desc_embed = discord.Embed(description=f"由 <@{ctx.author.id}> 發出的__{purpose}__邀請已過期")
            await target_user.send(embed=desc_embed)
            await ctx.send_followup(embed=desc_embed)
            return
        else:
            if str(rxn[0].emoji) == confirmEmoji:
                desc_embed = await self.create_desc_embed(target_user, f"已接受__{purpose}__邀請")

                await target_user.send(embed=desc_embed)
                await channel_msg.add_reaction(confirmEmoji)
                await ctx.send_followup(embed=desc_embed)
            elif str(rxn[0].emoji) == quitEmoji:
                desc_embed = await self.create_desc_embed(target_user, f"已拒絕__{purpose}__邀請")

                await target_user.send(embed=desc_embed)
                await channel_msg.add_reaction(quitEmoji)
                await ctx.send_followup(embed=desc_embed)

    askGameOption = [
        OptionChoice(name="ARAM", value="ARAM", name_localizations={"zh-TW": "單中"}),
        OptionChoice(name="Apex", value="Apex", name_localizations={"zh-TW": "Apex 英雄"}),
        OptionChoice(name="Minecraft", value="Minecraft", name_localizations={"zh-TW": "當個創世神"})
    ]
    @ask.command(guild_ids=guild_ids, name='game', description="玩唔玩...呀?", description_locationlizations={"zh-TW": "玩唔玩...呀?"})
    async def _game(self, ctx: commands.Context, target_user: Option(discord.Member, "User", required=True, name_localizations={"zh-TW": "收件人"}), purpose: Option(str, "Purpose", required=True, choices=askGameOption, name_localizations={"zh-TW": "目的"})):
        await self.process_ask_embed(ctx,target_user, purpose)

    askCustomOption = [
        OptionChoice(name="玩", value="玩", name_localizations={"zh-TW": "玩"}),
        OptionChoice(name="去", value="去", name_localizations={"zh-TW": "去"}),
        OptionChoice(name="搞", value="搞", name_localizations={"zh-TW": "搞"}),
        OptionChoice(name="試", value="試", name_localizations={"zh-TW": "試"}),
        OptionChoice(name="打", value="打", name_localizations={"zh-TW": "打"}),
        OptionChoice(name="問", value="問", name_localizations={"zh-TW": "問"}),
        OptionChoice(name="知", value="知", name_localizations={"zh-TW": "知"}),
        OptionChoice(name="食", value="食", name_localizations={"zh-TW": "食"}),
        OptionChoice(name="飲", value="飲", name_localizations={"zh-TW": "飲"}),
        OptionChoice(name="睇", value="睇", name_localizations={"zh-TW": "睇"})
    ]
    @ask.command(guild_ids=guild_ids, name='custom', description="_唔_...呀?", description_locationlizations={"zh-TW": "_唔_...呀?"})
    async def _custom(self, ctx: commands.Context, target_user: Option(discord.Member, "User", required=True, name_localizations={"zh-TW": "收件人"}), ask_type: Option(str, "Ask type", required=True, choices=askCustomOption, name_localizations={"zh-TW": "類別"}), purpose: Option(str, "Purpose", required=True, name_localizations={"zh-TW": "目的"}), thumbnail: Option(discord.Attachment, "Image", required=True, name_localizations={"zh-TW": "圖片"})):
        await self.process_ask_embed(ctx,target_user, purpose, thumbnail, ask_type)
        
    async def create_report_embed(self, ctx, content=str, thumbnail:str=None, report_type=str):
        title = "Bug report" if report_type == 'Bug' else "Suggestion report"
        thumbnail_url = thumbnail

        embed = discord.Embed(title=title)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.description = f'<@{ctx.author.id}> <:e_mail:1018530503344787477> __FBenI Headquarter__\n\n{content}'
        if thumbnail_url is not None:
            embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text=get_timestamp())

        return embed
        
    async def process_report_embed(self, ctx, content=str, thumbnail=None, report_type=str):
        await ctx.defer()
        embed_report = await self.create_report_embed(ctx, content, thumbnail, report_type)
        
        channel_target = channel_BenDiscordBot_BugReport if report_type == 'Bug' else channel_BenDiscordBot_SuggestionReport

        try:
            await bot.get_channel(channel_target).send(embed=embed_report)
            await ctx.send_followup(embed=embed_report)
        except Exception as e:
            embed_except = discord.Embed(description=f"無法傳信息至 <@{ctx.channel}>")
            await ctx.send_followup(embed=embed_except)
            return
        
    @report.command(guild_ids=guild_ids, name='bug', description="Bug report", cooldown=commands.CooldownMapping.from_cooldown(3, 60, commands.BucketType.default), description_locationlizations={"zh-TW": "漏洞回饋"})
    async def _bug(self, ctx: commands.Context, content: Option(str, "Content", required=True, name_localizations={"zh-TW": "內容"}), thumbnail: Option(discord.Attachment, "Image", required=False, name_localizations={"zh-TW": "圖片"})):
        await self.process_report_embed(ctx, content, thumbnail, "Bug")
        
    @report.command(guild_ids=guild_ids, name='suggest', description="Suggestion report", cooldown=commands.CooldownMapping.from_cooldown(3, 60, commands.BucketType.default), description_locationlizations={"zh-TW": "建議回饋"})
    async def _suggest(self, ctx: commands.Context, content: Option(str, "Content", required=True, name_localizations={"zh-TW": "內容"}), thumbnail: Option(discord.Attachment, "Image", required=False, name_localizations={"zh-TW": "圖片"})):
        await self.process_report_embed(ctx, content, thumbnail, "Suggest")

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Special(bot))