from globalImport import *

class Special(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
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

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Special(bot))