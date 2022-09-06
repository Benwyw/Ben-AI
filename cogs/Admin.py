from globalImport import *

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    guild_ids = guild_ids_FBenI
        
    admin = SlashCommandGroup(guild_ids=guild_ids, name="admin", description='Admin', description_localizations={"zh-TW": "管理員"})
    db = admin.create_subgroup(guild_ids=guild_ids, name="db", description='Database', description_localizations={"zh-TW": "數據庫"})
    test = admin.create_subgroup(guild_ids=guild_ids, name="test", description='Testing', description_localizations={"zh-TW": "測試"})


    # --- Action ---
    
    @admin.command(guild_ids=guild_ids, name='announce')
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
            cave_channel = bot.get_channel(490302069425700866) #Cave ben-ai
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
                
            #send main
            try:
                await cave_channel.send(embed=embed_botupdates)
            except Exception as e:
                await ctx.send_followup("Unable to send message to Cave")
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

    @admin.command(guild_ids=guild_ids, name='status')
    @commands.is_owner()
    async def _status(self, ctx: commands.Context, status):
        '''特別指令。更改狀態。'''

        if status != "reset":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/ | {}".format(status)))
        else:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/ | 冇野幫到你"))
        
        await ctx.respond('Request processed.')
        

    # --- Economy ---
    
    @db.command(guild_ids=guild_ids, description="Set money for user. Requires administrator permissions.",
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
        embed.set_thumbnail(url=Economy_imgUrl)

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
            embed.set_thumbnail(url=Economy_imgUrl)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="權限錯誤",
                                    description="您無權使用此指令。",
                                    color=0x00ff00)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=Economy_imgUrl)
            await ctx.send(embed=embed)
            
            
    # --- Database ---
    
    @db.command(guild_ids=guild_ids, name='scanusers')
    @commands.is_owner()
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

    memeChoice = [
        OptionChoice(name="Up", value="up", name_localizations={"zh-TW": "上"}),
        OptionChoice(name="Center", value="center", name_localizations={"zh-TW": "中"}),
        OptionChoice(name="Down", value="down", name_localizations={"zh-TW": "下"})
    ]
    meme_size_choice = [
        OptionChoice(name="Small", value=10, name_localizations={"zh-TW": "小"}),
        OptionChoice(name="Medium", value=50, name_localizations={"zh-TW": "中"}),
        OptionChoice(name="Large", value=100, name_localizations={"zh-TW": "大"})
    ]
    meme_color_choice = [
        OptionChoice(name="Red", value="red", name_localizations={"zh-TW": "紅"}),
        OptionChoice(name="Green", value="green", name_localizations={"zh-TW": "綠"}),
        OptionChoice(name="Blue", value="blue", name_localizations={"zh-TW": "藍"}),
        OptionChoice(name="Yellow", value="yellow", name_localizations={"zh-TW": "黃"}),
        OptionChoice(name="Cyan", value="cyan", name_localizations={"zh-TW": "藍綠"}),
        OptionChoice(name="Magenta", value="magenta", name_localizations={"zh-TW": "洋紅"}),
        OptionChoice(name="White", value="white", name_localizations={"zh-TW": "白"}),
        OptionChoice(name="Black", value="black", name_localizations={"zh-TW": "黑"})
    ]
    @slash_command(guild_ids=guild_ids,
                   name='meme',
                   description='Meme generator',
                   description_localizations={"zh-TW": "梗圖生成器"})
    async def _meme(self, ctx: commands.Context,
                    text:Option(str, "Input text of your choice", name_localizations={"zh-TW": "文字"}), 
                    txtsize:Option(int, description = "Font size", required = True, choices = meme_size_choice, name_localizations={"zh-TW": "文字大小"}),
                    pos:Option(str, "Position", required = True, choices=memeChoice, name_localizations={"zh-TW": "位置"}),
                    color:Option(str, "Color", required = True, choices = meme_color_choice, name_localizations={"zh-TW": "顏色"}),
                    attachment:Option(discord.Attachment, "Image", required=True, name_localizations={"zh-TW": "圖片"})):
                    #url:Option(str, "Image url, either one", required=False)
        
        await ctx.defer()
        try:
            #processed_url = attachment if attachment is not None else url
            image = Image.open(BytesIO(requests.get(attachment).content))
            image = image.convert('RGBA')
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
        else:
            with BytesIO() as img:
                image.save(img, 'PNG')
                img.seek(0)
                file = discord.File(fp=img, filename='memeup.png')
            await ctx.send_followup(file=file)

    @db.command(guild_ids=guild_ids, name='deletelol')
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

    @db.command(guild_ids=guild_ids, name='insertlol')
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
            
    @db.command(guild_ids=guild_ids, name='updateserverpw')
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

    @db.command(guild_ids=guild_ids, name='deleteserver')
    @commands.is_owner()
    async def deleteserver(self, ctx: commands.Context, id):
        '''Delete server by (id)'''

        await ctx.defer()
        result = "No operations."

        DBConnection.deleteServer(str(id))
        result = "Successfully deleted `{}` in serverlist".format(id)
        
        await ctx.send_followup(result)

    @db.command(guild_ids=guild_ids, name='updateserver')
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

    @db.command(guild_ids=guild_ids, name='createserver')
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
        
    
    # --- Test ---
    
    @test.command(guild_ids=guild_ids, name='gamesloop')
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
    
    @test.command(guild_ids=guild_ids, name='newsloop')
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
    
    @test.command(guild_ids=guild_ids, name='welcome')
    @commands.is_owner()
    async def testwelcome(self, ctx: commands.Context):
        '''Test welcome message'''
        
        await ctx.defer()
        
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
        #bot_channel = bot.get_channel(692466531447210105)
        
        try:
            await ctx.author.send(embed=bot_channel_embed_to_member)
            bot_channel_embed_to_staff.description = "歡迎信息發送成功"
            bot_channel_embed_to_staff.color = 0x00ff00
        except Exception as e:
            bot_channel_embed_to_staff.description = "無法發送歡迎信息"
            bot_channel_embed_to_staff.color = 0xff0000
            await log(str(e))
        #await bot_channel.send(embed=bot_channel_embed_to_staff)
        await ctx.send_followup(embed=bot_channel_embed_to_staff)
    
            
def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Admin(bot))     