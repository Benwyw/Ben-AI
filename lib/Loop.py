from lib.GlobalImport import *
from lib.RiotApi import RiotApi

import sys


@loop(minutes=10)
async def twLolLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    # try:
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    summonerNames = DBConnection.getLolSummonerNames(getRegion('tw'))
    print(summonerNames)
    if summonerNames is None or int(len(summonerNames)) == 0:
        print(str(summonerNames) + ' is None or len = 0')
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
            uuid = str(title).split(',', 1)[1].split(', \'', 1)[1].split('\'', 1)[0]
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
                thumbnail = str(section).split('\"', 1)[1].split('\\"', 1)[0]
                break

            for section in soup_section.findAll("b"):
                title = str(section).split('>', 1)[1].split('<', 1)[0].encode('utf-8').decode('unicode_escape')
                break

            for section in soup_section.findAll("div"):
                if section is not None and str(section) != '' and str(section) != ' ' and '<' in str(
                        section) and '>' in str(section):
                    tempSection = str(section).split('>', 1)[1].split('<', 1)[0]

                if '/' in tempSection and dt == '':
                    dt = tempSection
                elif 'min' in tempSection and 's' in tempSection and gameDuration == '':
                    gameDuration = tempSection
                elif '\\' not in tempSection and gameMode == '':
                    gameMode = tempSection

            count = 0
            for section in soup_section.findAll("span"):
                if section is not None and str(section) != '' and str(section) != ' ' and '<' in str(
                        section) and '>' in str(section):
                    tempSection = str(section).split('>', 1)[1].split('<', 1)[0]

                if tempSection != '/':
                    if count == 0:
                        kills = tempSection
                    elif count == 1:
                        deaths = tempSection
                    elif count == 2:
                        assists = tempSection

                    count += 1

            break

        # DB operations
        if ' ' in gameDuration:
            dt_gD = gameDuration.replace(' ', '')
        if 'min' in gameDuration:
            dt_gD = gameDuration.replace('min', '')
        if 's' in gameDuration:
            dt_gD = gameDuration.replace('s', '')
        dt_duration = '{}{}{}{}{}{}'.format(gameMode, dt, dt_gD, kills, deaths, assists)  # format for unique id
        dt_duration_30 = dt_duration[:min(len(dt_duration), 30)]  # limit length to 30 char
        dt_db = DBConnection.getLolPublishedAt(getRegion('tw'), summonerName)[0][0]
        if str(dt_duration_30) != str(dt_db):
            DBConnection.updateLolPublishedAt(getRegion('tw'), dt_duration_30, summonerName)
            print('else with {}'.format(summonerName))

            color = 0x000000
            print('title: ' + str(title))
            print('title sumName: ' + str(summonerName))
            if '勝利' in str(title):
                color = 0x00ff00
            else:
                color = 0xff0000

            title = title.format('{} {}'.format(summonerName, title))
            url = url_construct
            championName = thumbnail.split('champion/')[1].split('.')[0]

            # embed construct
            embed = discord.Embed()
            embed.title = title
            embed.color = color
            embed.url = url
            # embed.description = desc
            embed.set_author(name='League of Legends (TW)', icon_url='https://i.imgur.com/tkjOxrX.png')
            embed.set_thumbnail(url=thumbnail)

            embed.add_field(name="召喚師等級", value='{}'.format(summonerLevel), inline=True)
            embed.add_field(name="英雄名字", value='{}'.format(championName), inline=True)
            # embed.add_field(name="獲得金幣", value='{}'.format(goldEarned), inline=True)

            embed.add_field(name="遊戲時長", value='{} 分鐘'.format(gameDuration), inline=True)
            embed.add_field(name="遊戲模式", value='{}'.format(gameMode), inline=True)
            # embed.add_field(name="遊戲類型", value='{}'.format(gameType), inline=True)

            embed.add_field(name="擊殺", value='{}'.format(kills), inline=True)
            embed.add_field(name="死亡", value='{}'.format(deaths), inline=True)
            embed.add_field(name="助攻", value='{}'.format(assists), inline=True)

            # embed.add_field(name="雙殺", value='{}'.format(doubleKills), inline=True)
            # embed.add_field(name="三連殺", value='{}'.format(tripleKills), inline=True)
            # embed.add_field(name="四連殺", value='{}'.format(quadraKills), inline=True)
            # embed.add_field(name="五連殺", value='{}'.format(pentaKills), inline=True)

            embed.set_footer(text=dt)

            # BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
            BLG_ST_Channel = bot.get_channel(815568098001813555)  # BrianLee Server - satellie
            # BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

            # await BDS_PD_Channel.send(embed=embed)
            # await BLG_ST_Channel.send(embed=embed)
            print('end with {}'.format(summonerName))
            # await BMS_OT_Channel.send(embed=embed)

    # except Exception as e:
    # BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
    # await BDS_Log_Channel.send('{}\n\nError occured in twLolLoop\n{}'.format(e,timestamp))


'''
https://developer.riotgames.com/docs/lol#data-dragon_regions
'''


@loop(minutes=10)
async def riotLolLoop():
    regionList = ['na', 'tw', 'eu']
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    embedList = []

    try:
        for region in regionList:
            count = 0
            summonerNames = DBConnection.getLolSummonerNames(getRegion(region))

            load_dotenv()
            riotApi = None
            if not str(sys.platform).startswith('win'):
                riotApi = RiotApi(os.getenv('RIOT_API_KEY'), region)
            else:
                riotApi = RiotApi(os.getenv('RIOT_DEV_API_KEY'), region)

            for summonerName in summonerNames:
                if count == 20:
                    asyncio.sleep(1)
                    count = 0

                count += 1
                summonerName = str(summonerName[0])
                match = riotApi.get_latest_matches_by_name(summonerName)

                if match is None:
                    await log(
                        '{}\n\nError occured in riotLolLoop summoner: {} possibly not found in region {}\n'.format(
                            timestamp, summonerName, region))
                    continue

                matchId = match['metadata']['matchId']

                # DB operations
                dt_db = DBConnection.getLolPublishedAt(getRegion(region), summonerName)[0][0]
                if str(matchId) == str(dt_db):
                    continue
                else:
                    DBConnection.updateLolPublishedAt(getRegion(region), matchId, summonerName)

                    gameDuration = match['info']['gameDuration']
                    gameMode = match['info']['gameMode']
                    gameType = match['info']['gameType']
                    gameStartTimestamp = match['info']['gameStartTimestamp']

                    for participant in match['info']['participants']:

                        # if a list of participant names...
                        if participant['summonerName'] == summonerName:
                            # general
                            summonerLevel = participant['summonerLevel']
                            championName = participant['championName']
                            win = participant['win']

                            # economy
                            goldEarned = participant['goldEarned']
                            goldSpent = participant['goldSpent']

                            # KDA
                            kills = participant['kills']
                            deaths = participant['deaths']
                            assists = participant['assists']

                            # double triple quadra penta kill
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
                    url = 'https://{}.op.gg/summoner/userName={}'.format(region, summonerNameFormat)
                    thumbnail = 'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{}_0.jpg'.format(
                        championName)
                    # dt = str(datetime.utcfromtimestamp(int(gameStartTimestamp)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                    dt = "{} {}".format(str(datetime.fromtimestamp(int(gameStartTimestamp) / 1000,
                                                                   pytz.timezone('Asia/Hong_Kong')).strftime(
                        '%Y-%m-%d %H:%M:%S')), 'HKT')

                    # embed construct
                    embed = discord.Embed()
                    embed.title = title
                    embed.color = color
                    embed.url = url
                    # embed.description = desc
                    embed.set_author(name='League of Legends ({})'.format(region.upper()),
                                     icon_url='https://i.imgur.com/tkjOxrX.png')
                    embed.set_thumbnail(url=thumbnail)

                    embed.add_field(name="召喚師等級", value='{}'.format(summonerLevel), inline=True)
                    embed.add_field(name="英雄名字", value='{}'.format(championName), inline=True)
                    embed.add_field(name="獲得金幣", value='{}'.format(goldEarned), inline=True)

                    embed.add_field(name="遊戲時長", value='{} 分鐘'.format(int(gameDuration) / 60), inline=True)
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

                    embedList.append(embed)

                    '''print('\n\n')
                    print('matchId: {}\ngameDuration: {}\ngameMode: {}\ngameType: {}\n \
                        summonerLevel: {}\nchampionName: {}\nwin: {}\n \
                        goldEarned: {}\ngoldSpent: {}\n \
                        kills: {}\ndeaths: {}\nassists: {}\n \
                        doubleKills: {}\ntripleKills: {}\nquardraKills: {}\npentaKills: {}'.format(matchId, gameDuration, gameMode, gameType, summonerLevel, championName, win, goldEarned, goldSpent, kills, deaths, assists, doubleKills, tripleKills, quadraKills, pentaKills))'''

        embedList.sort(
            key=lambda embed: datetime.strptime(str(embed.footer).split('\'')[1].split('\'')[0].split(' HKT')[0],
                                                '%Y-%m-%d %H:%M:%S'))
        for embed in embedList:
            if str(sys.platform).startswith('win'):
                await bot.get_channel(channel_BenDiscordBot_PublicDemo).send(
                    embed=embed)  # Ben Discord Bot - public demo
            else:
                await bot.get_channel(channel_BrianLee_Satellite).send(embed=embed)  # BrianLee Server - satellie
                # await bot.get_channel(channel_BenKaChu_OffTopic).send(embed=embed) #Ben's Minecraft Server - off topic
    except Exception as e:
        await log('{}\n\nError occured in riotLolLoop\n{}'.format(e, timestamp))


@loop(minutes=10)
async def newTWLolLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:

        count = 0
        summonerNames = DBConnection.getLolSummonerNames(getRegion('tw'))

        load_dotenv()
        riotApi = None
        if not str(sys.platform).startswith('win'):
            riotApi = RiotApi(os.getenv('RIOT_API_KEY'), "tw2")
        else:
            riotApi = RiotApi(os.getenv('RIOT_DEV_API_KEY'), "tw2")

        for summonerName in summonerNames:
            if count == 20:
                asyncio.sleep(1)
                count = 0

            count += 1
            summonerName = str(summonerName[0])
            match = riotApi.get_latest_matches_by_name(summonerName)

            if match is None:
                await log(
                    '{}\n\nError occured in lolloop summoner: {} possibly not found\n'.format(timestamp, summonerName))
                continue

            matchId = match['metadata']['matchId']

            # DB operations
            dt_db = DBConnection.getLolPublishedAt(getRegion('tw'), summonerName)[0][0]
            if str(matchId) == str(dt_db):
                continue
            else:
                DBConnection.updateLolPublishedAt(getRegion('tw'), matchId, summonerName)

                gameDuration = match['info']['gameDuration']
                gameMode = match['info']['gameMode']
                gameType = match['info']['gameType']
                gameStartTimestamp = match['info']['gameStartTimestamp']

                for participant in match['info']['participants']:

                    # if a list of participant names...
                    if participant['summonerName'] == summonerName:
                        # general
                        summonerLevel = participant['summonerLevel']
                        championName = participant['championName']
                        win = participant['win']

                        # economy
                        goldEarned = participant['goldEarned']
                        goldSpent = participant['goldSpent']

                        # KDA
                        kills = participant['kills']
                        deaths = participant['deaths']
                        assists = participant['assists']

                        # double triple quadra penta kill
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
                url = 'https://tw.op.gg/summoner/userName={}'.format(summonerNameFormat)
                thumbnail = 'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{}_0.jpg'.format(championName)
                dt = str(datetime.utcfromtimestamp(int(gameStartTimestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S'))

                # embed construct
                embed = discord.Embed()
                embed.title = title
                embed.color = color
                embed.url = url
                # embed.description = desc
                embed.set_author(name='League of Legends (TW)', icon_url='https://i.imgur.com/tkjOxrX.png')
                embed.set_thumbnail(url=thumbnail)

                embed.add_field(name="召喚師等級", value='{}'.format(summonerLevel), inline=True)
                embed.add_field(name="英雄名字", value='{}'.format(championName), inline=True)
                embed.add_field(name="獲得金幣", value='{}'.format(goldEarned), inline=True)

                embed.add_field(name="遊戲時長", value='{} 分鐘'.format(int(gameDuration) / 60), inline=True)
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

                await bot.get_channel(channel_BenDiscordBot_PublicDemo).send(
                    embed=embed)  # Ben Discord Bot - public demo
                # await bot.get_channel(channel_BrianLee_Satellite).send(embed=embed) #BrianLee Server - satellie
                # await bot.get_channel(772038210057535488).send(embed=embed) #Ben's Minecraft Server - off topic

                '''print('\n\n')
                print('matchId: {}\ngameDuration: {}\ngameMode: {}\ngameType: {}\n \
                    summonerLevel: {}\nchampionName: {}\nwin: {}\n \
                    goldEarned: {}\ngoldSpent: {}\n \
                    kills: {}\ndeaths: {}\nassists: {}\n \
                    doubleKills: {}\ntripleKills: {}\nquardraKills: {}\npentaKills: {}'.format(matchId, gameDuration, gameMode, gameType, summonerLevel, championName, win, goldEarned, goldSpent, kills, deaths, assists, doubleKills, tripleKills, quadraKills, pentaKills))'''
    except Exception as e:
        await log('{}\n\nError occured in newTWLolLoop\n{}'.format(e, timestamp))


@loop(minutes=10)
async def naLolLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:

        count = 0
        # totalcount = 0
        summonerNames = DBConnection.getLolSummonerNames(getRegion('na'))

        load_dotenv()
        riotApi = None
        if not str(sys.platform).startswith('win'):
            riotApi = RiotApi(os.getenv('RIOT_API_KEY'), "na1")
        else:
            riotApi = RiotApi(os.getenv('RIOT_DEV_API_KEY'), "na1")

        for summonerName in summonerNames:
            if count == 20:
                asyncio.sleep(1)
                count = 0
                # totalcount += count

            count += 1
            summonerName = str(summonerName[0])
            match = riotApi.get_latest_matches_by_name(summonerName)

            if match is None:
                await log(
                    '{}\n\nError occured in lolloop summoner: {} possibly not found\n'.format(timestamp, summonerName))
                continue

            matchId = match['metadata']['matchId']

            # DB operations
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

                    # if a list of participant names...
                    if participant['summonerName'] == summonerName:
                        # general
                        summonerLevel = participant['summonerLevel']
                        championName = participant['championName']
                        win = participant['win']

                        # economy
                        goldEarned = participant['goldEarned']
                        goldSpent = participant['goldSpent']

                        # KDA
                        kills = participant['kills']
                        deaths = participant['deaths']
                        assists = participant['assists']

                        # double triple quadra penta kill
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
                dt = str(datetime.utcfromtimestamp(int(gameStartTimestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S'))

                # embed construct
                embed = discord.Embed()
                embed.title = title
                embed.color = color
                embed.url = url
                # embed.description = desc
                embed.set_author(name='League of Legends (NA)', icon_url='https://i.imgur.com/tkjOxrX.png')
                embed.set_thumbnail(url=thumbnail)

                embed.add_field(name="召喚師等級", value='{}'.format(summonerLevel), inline=True)
                embed.add_field(name="英雄名字", value='{}'.format(championName), inline=True)
                embed.add_field(name="獲得金幣", value='{}'.format(goldEarned), inline=True)

                embed.add_field(name="遊戲時長", value='{} 分鐘'.format(int(gameDuration) / 60), inline=True)
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

                # BDS_PD_Channel = bot.get_channel(927850362776461333) #Ben Discord Bot - public demo
                BLG_ST_Channel = bot.get_channel(channel_BrianLee_Satellite)  # BrianLee Server - satellie
                # BMS_OT_Channel = bot.get_channel(772038210057535488) #Ben's Minecraft Server - off topic

                # await BDS_PD_Channel.send(embed=embed)
                await BLG_ST_Channel.send(embed=embed)
                # await BMS_OT_Channel.send(embed=embed)

                '''print('\n\n')
                print('matchId: {}\ngameDuration: {}\ngameMode: {}\ngameType: {}\n \
                    summonerLevel: {}\nchampionName: {}\nwin: {}\n \
                    goldEarned: {}\ngoldSpent: {}\n \
                    kills: {}\ndeaths: {}\nassists: {}\n \
                    doubleKills: {}\ntripleKills: {}\nquardraKills: {}\npentaKills: {}'.format(matchId, gameDuration, gameMode, gameType, summonerLevel, championName, win, goldEarned, goldSpent, kills, deaths, assists, doubleKills, tripleKills, quadraKills, pentaKills))'''
    except Exception as e:
        await log('{}\n\nError occured in naLolLoop\n{}'.format(e, timestamp))


@loop(minutes=30)
async def hypebeastLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

        url = Request("https://hypebeast.com/zh/latest", headers=hdr)
        html_page = urlopen(url)
        soup = BeautifulSoup(html_page, "lxml")

        text = ''  # game title
        link = ''  # game url
        img = ''  # image url
        desc = ''  # game desc
        dt = ''  # posted dt
        for title in soup.findAll("div", class_="post-box"):
            if "post-box sticky-post" in str(title):
                continue

            soup_section = BeautifulSoup(str(title), "lxml")

            for section in soup_section.findAll("time", class_="timeago"):
                dt = str(section).split('datetime=\"')[1].split('\">', 1)[0]
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
                    desc = str(section).split('\">', 1)[1].split('</', 1)[0].strip()
                    break

                for section in soup_section.findAll("img", class_="img-fluid lazy-load"):
                    img_text = str(section).split('alt=\"', 1)[1].split('\"')[0].strip()
                    if text == img_text:
                        img = str(section).split('data-srcset=\"', 1)[1].split(' 1x', 1)[0]
                        break

                # embed construct
                embed = discord.Embed()
                embed.title = text
                embed.description = desc
                embed.set_author(name='Hypebeast', icon_url='https://i.imgur.com/9IvVe1D.png')
                embed.set_thumbnail(url=img)
                embed.set_footer(text=dt)

                # url handlings
                url = link
                if url is not None and 'http' in url and '://' in url:
                    url2 = url.rsplit('/', 1)[1]
                    url1 = url.rsplit('/', 1)[0]
                    if url2 is not None and url2 != '' and not url2.isalnum():
                        url2 = quote(url2)
                        url = url1 + '/' + url2
                    embed.url = url

                BDS_PD_Channel = bot.get_channel(channel_BenDiscordBot_PublicDemo)  # Ben Discord Bot - public demo
                BLG_ST_Channel = bot.get_channel(channel_BrianLee_Satellite)  # BrianLee Server - satellie
                BMS_OT_Channel = bot.get_channel(772038210057535488)  # Ben's Minecraft Server - off topic

                await BDS_PD_Channel.send(embed=embed)
                await BLG_ST_Channel.send(embed=embed)
                # await BMS_OT_Channel.send(embed=embed)

            break
    except Exception as e:
        await log('{}\n\nError occured in hypebeastLoop\n{}'.format(e, timestamp))


@loop(hours=1)
async def gamesLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

        url = Request("https://www.indiegamebundles.com/category/free/", headers=hdr)
        html_page = urlopen(url)
        soup = BeautifulSoup(html_page, "lxml")

        text = ''  # game title
        link = ''  # game url
        desc = ''  # game desc
        dt = ''  # posted dt
        img = ''  # image url

        for title in soup.findAll("div", class_="td-module-container"):
            soup_section = BeautifulSoup(str(title), "lxml")

            for section in soup_section.findAll("div", class_="td-module-thumb"):
                soup_section = BeautifulSoup(str(section), "lxml")

                for section in soup_section.findAll("span", class_="entry-thumb td-thumb-css rocket-lazyload"):
                    img = str(section).split('data-bg=\"')[1].split('\"', 1)[0]
                    break

                break
            break

        for title in soup.findAll("div", class_="td-module-meta-info"):
            soup_section = BeautifulSoup(str(title), "lxml")

            for section in soup_section.findAll("time", class_="entry-date updated td-module-date"):
                dt = str(section).split('datetime=\"')[1].split('\">', 1)[0]
                # print(dt+'\n') #text_30 = text[:min(len(text), 30)]
                break
            dt_db = DBConnection.getPublishedAt('indiegamebundles')[0][0]
            if str(dt) == str(dt_db):
                return
            else:
                DBConnection.updatePublishedAt(dt, 'indiegamebundles')
                # continue else

                for section in soup_section.findAll("h3", class_="entry-title td-module-title"):
                    title = str(section)
                    link = title.split('<a href=\"')[1].split('\" rel=\"bookmark\" title=\"')[0]
                    text = \
                    title.split('<a href=\"')[1].split('\" rel=\"bookmark\" title=\"')[1].split('</a></h3>')[0].split(
                        '\">')[0]
                    break

                for section in soup_section.findAll("div", class_="td-excerpt"):
                    desc = str(section).split('\">', 1)[1].split('</', 1)[0]
                    break

                # embed construct
                embed = discord.Embed()
                embed.title = text
                embed.color = 0xb50024
                embed.description = desc
                embed.set_author(name='Indie Game Bundles', icon_url='https://i.imgur.com/RWIVDRN.png')
                embed.set_thumbnail(url=img)
                embed.set_footer(text=dt)

                # url handlings
                url = link
                if url is not None and 'http' in url and '://' in url:
                    url2 = url.rsplit('/', 1)[1]
                    url1 = url.rsplit('/', 1)[0]
                    if url2 is not None and url2 != '' and not url2.isalnum():
                        url2 = quote(url2)
                        url = url1 + '/' + url2
                    embed.url = url

                BDS_PD_Channel = bot.get_channel(channel_BenDiscordBot_PublicDemo)  # Ben Discord Bot - public demo
                BLG_ST_Channel = bot.get_channel(channel_BrianLee_Satellite)  # BrianLee Server - satellie
                BMS_OT_Channel = bot.get_channel(channel_BenKaChu_OffTopic)  # Ben's Minecraft Server - off topic

                await BDS_PD_Channel.send(embed=embed)
                await BLG_ST_Channel.send(embed=embed)
                await BMS_OT_Channel.send(embed=embed)

            break
    except Exception as e:
        await log('{}\n\nError occured in gamesLoop\n{}'.format(e, timestamp))


@loop(hours=1)
async def newsLoop():
    newsList = ['Rthk.hk']  # , 'Bloomberg', 'IGN']
    for newsId in newsList:
        embed = await getNewsEmbed(newsId)
        if embed is not None:
            BDS_PD_Channel = bot.get_channel(channel_BenDiscordBot_PublicDemo)  # Ben Discord Bot - public demo
            BLG_ST_Channel = bot.get_channel(channel_BrianLee_Satellite)  # BrianLee Server - satellie
            BMS_OT_Channel = bot.get_channel(channel_BenKaChu_OffTopic)  # Ben's Minecraft Server - off topic

            await BDS_PD_Channel.send(embed=embed)
            # await BMS_OT_Channel.send(embed=embed)

            '''if newsId in ['Bloomberg', 'IGN']:
                Cave_Channel = bot.get_channel(channel_Cave_BenAI) #Cave - ben-ai
                await Cave_Channel.send(embed=embed)
            else:'''
            await BLG_ST_Channel.send(embed=embed)


@loop(minutes=15)
async def covLoop():
    timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
    try:
        # api / json
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        # api = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fbuilding_list_chi.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%2C%22sorts%22%3A%5B%5B4%2C%22desc%22%5D%5D%7D"
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
        # print('{} {} {} {} {} {} {} {} {} {}'.format(caseNo, reportedDate, onsetDate, sex, age, hospital, humanStatus, local, category, caseStatus))

        # db
        db_case_no = DBConnection.getCaseNo()[0][0]

        if int(caseNo) == int(db_case_no):
            return
        else:
            DBConnection.updateCaseNo(caseNo)

            embed = discord.Embed(title='2019冠狀病毒病的本地最新情況',
                                  url='https://data.gov.hk/tc-data/dataset/hk-dh-chpsebcddr-novel-infectious-agent/resource/f350a865-03a0-4b82-b3ce-2b7d3a817688')
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

            BDS_PD_Channel = bot.get_channel(channel_BenDiscordBot_PublicDemo)  # Ben Discord Bot - public demo
            BLG_ST_Channel = bot.get_channel(channel_BrianLee_Satellite)  # BrianLee Server - satellie
            BMS_OT_Channel = bot.get_channel(772038210057535488)  # Ben's Minecraft Server - off topic

            # Google Map
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
            # await BMS_OT_Channel.send(embed=embed)

    except Exception as e:
        await log('{}\n\nError occured in covLoop\n{}'.format(e, timestamp))
