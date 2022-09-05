# -*- coding: utf-8 -*-

"""
pip install -U discord.py pynacl youtube-dl
Requires FFmpeg in PATH environment variable or bot's directory
"""
from globalImport import *
from cogs.Game import gameLoop

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
            iurl = str(DBConnection.getRemarks(source, 'Y')[0][0])

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
                #await BMS_OT_Channel.send(embed=embed)

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

                BDS_PD_Channel = bot.get_channel(channel_BenDiscordBot_PublicDemo) #Ben Discord Bot - public demo
                BLG_ST_Channel = bot.get_channel(channel_BrianLee_Satellite) #BrianLee Server - satellie
                BMS_OT_Channel = bot.get_channel(channel_BenKaChu_OffTopic) #Ben's Minecraft Server - off topic

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
            BDS_PD_Channel = bot.get_channel(channel_BenDiscordBot_PublicDemo) #Ben Discord Bot - public demo
            BLG_ST_Channel = bot.get_channel(channel_BrianLee_Satellite) #BrianLee Server - satellie
            BMS_OT_Channel = bot.get_channel(channel_BenKaChu_OffTopic) #Ben's Minecraft Server - off topic

            await BDS_PD_Channel.send(embed=embed)
            #await BMS_OT_Channel.send(embed=embed)
            
            if newsId in ['Bloomberg', 'IGN']:
                Cave_Channel = bot.get_channel(965809908970819614) #Cave - ben-ai
                await Cave_Channel.send(embed=embed)
            else:
                await BLG_ST_Channel.send(embed=embed)

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
            #await BMS_OT_Channel.send(embed=embed)

    except Exception as e:
        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
        await BDS_Log_Channel.send('{}\n\nError occured in covLoop\n{}'.format(e,timestamp))





bot.load_extension('Poker')
bot.load_extension('Economy')
bot.load_extension('Betting')
bot.load_extension('Pres')
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
        '''gameLoop.start()
        covLoop.start()
        newsLoop.start()
        gamesLoop.start()
        hypebeastLoop.start()
        naLolLoop.start()'''
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
    if reaction.message.guild.id == 351742829254410250 and (('ben' in reaction.message.content.lower() and 'gay' in reaction.message.content.lower()) or ('ben' == reaction.message.content.lower())):
        if len(reaction.message.reactions) == 3 and "🇬" in str(reaction.message.reactions) and "🇦" in str(reaction.message.reactions) and "🇾" in str(reaction.message.reactions):
            await reaction.message.add_reaction("🇵")
            await reaction.message.add_reaction("🇴")
            await reaction.message.add_reaction("🇰")

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

        seedCategory = randrange(3)
        seed = randrange(6)

        img = None
        if seedCategory == 0:
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

        elif seedCategory == 1:
            #demon slayer
            if seed == 0:
                img = "https://i.imgur.com/VWvwDQp.gif"
                msg = "不要讓其他人掌握你的生殺大權，\n" \
                    "不要悲慘的跪下來求任何人，\n" \
                    "如果這麼做有用的話，\n" \
                    "你的{}就不會被鬼殺了。".format('BOT')
            elif seed == 1:
                img = "https://i.imgur.com/IkLDag7.gif"
                msg = "情緒支配下的攻擊，兩個字，愚Pok。\n" \
                    "你就不能用自己的頭腦思考一下嗎？\n" \
                    "如果光憑「憤怒」就能勝利，那世界上就不會有鬼了。"
            elif seed == 2:
                img = "https://i.imgur.com/3UJZUUl.gif"
                msg = "禰豆子禰豆子禰豆子\n" \
                    "禰豆子禰豆子禰豆子\n" \
                    "禰豆子禰豆子禰豆子"
            elif seed == 3:
                img = "https://i.imgur.com/TtMVkGI.gif"
                msg = "???!!!"
            elif seed == 4:
                img == "https://i.imgur.com/xsQJglf.jpg"
                msg = "無論如何，\n" \
                    "都請為自己感到自豪並且努力活下去。"
            elif seed == 5:
                img == "https://i.imgur.com/MfaJOtc.gif"
                msg = "你就是雷柱個friend，\n" \
                    "__好撚雷__嗎？"

        elif seedCategory == 2:
            if seed == 0:
                img = "https://i.imgur.com/yY9Lwjz.gif"
                msg = "OT on99！"
            elif seed == 1:
                img = "https://i.imgur.com/pDCgoaR.png"
                msg = "就算你說些聽起來像一回事的大道理，\n" \
                    "你也只不過想要認為自己是正確的罷了。"
            elif seed == 2:
                img = "https://i.imgur.com/gCZK0SQ.jpg"
                msg = "不幸的人做什麼都會被原諒嗎？"
            elif seed == 3:
                img = "https://i.imgur.com/l51cxNQ.png"
                msg = "以死獲勝跟拼死獲勝，這兩者完全不同喔，\n" \
                    "{}，使出全力吧，你要更貪心一點。".format(bot.get_user(346518519015407626).display_name)
            elif seed == 4:
                img == "https://i.imgur.com/Bfg91US.gif"
                msg = "在我生命中沒有一席之地的人，\n" \
                    "我不希望他們影響到我的內心。"
            elif seed == 5:
                img == "https://i.imgur.com/vElML0o.gif"
                msg = "Strong"

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

    #Anti Bot Pok
    if message.guild.id == 351742829254410250:
        if message.author.id == 941598922948870186 and (('ben' in message.content.lower() and 'gay' in message.content.lower()) or ('is' in message.content.lower() and 'gay' in message.content.lower())):
            await message.reply('Pok gay')
        if message.author.id != 941598922948870186 and 'ben' in message.content.lower() and 'gay' in message.content.lower():
            await message.reply('Pok is gay')
        if 'ben' == message.content.lower():
            await message.reply('is strong')


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
