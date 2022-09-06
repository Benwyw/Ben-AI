from lib.globalImport import *

@loop(seconds=1)
async def gameLoop():
    for GAME in gameList:
        await GAME.gameLoop()

# Card constants
offset = 10
cardWidth = 138
cardHeight = 210

gameList = []

uncategorized = ['game', 'hand',  'in', 'rc', 'setcolor', 'setsort', 'start']

# Card generator
cardChoices = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
suits = ['C', 'D', 'H', 'S']



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

# Get a Game object by its 6-digit id
def getGameByid(id):
    for GAME in gameList:
        if GAME.ID == id:
            return GAME

# Check if a Game object exists given a 6-digit id
def hasGame(id):
    for GAME in gameList:
        if GAME.ID == id:
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
    sorttype = DBConnection.fetchUserData("sortPref", str(user.id))
    if sorttype== 'p':
        ORDER = presOrder
    elif sorttype == 's':
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

class Game(commands.Cog):
    games = SlashCommandGroup(guild_ids=guild_ids, name="games", description='Games', description_localizations={"zh-TW": "遊戲"})
    
    @games.command(guild_ids=guild_ids, description="遊戲幫助指令。",
                      name="cmd",
                      help="顯示遊戲指令表",
                      pass_context=True)
    async def _cmd(self, ctx: commands.Context, param: str = None):
        if param is None:
            embed = discord.Embed(title="新世界 指令表",
                                  description="要查看幫助頁面，只需在/cmd命令後添加頁面編號。 例如：/cmd 3",
                                  color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
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
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            if int(param) == 1:
                commands = bot.get_cog('Betting').get_commands()
                embed.title = "賭注 指令"
                embed.description = "要查看特定指令，請在/cmd命令之後輸入指令名稱。 例如：/cmd raise。"

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 2:
                commands = bot.get_cog('Economy').get_commands()
                embed.title = "經濟 指令"
                embed.description = "要查看特定指令，請在/cmd命令之後輸入指令名稱。 例如：/cmd bal。"

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 3:
                embed.title = "遊戲 指令"
                embed.description = "要查看幫助頁面，只需在/cmd命令後添加頁面編號。 例如：/cmd 3"
                embed.add_field(name="第5頁：德州撲克", value="德州撲克的指令。", inline=False)
                embed.add_field(name="Page 6: 大統領", value="大統領的指令。", inline=False)
                await ctx.send(embed=embed)
            elif int(param) == 4:
                embed.title = "未分類的指令"
                embed.description = "要查看特定指令，請在/cmd命令之後輸入指令名稱。 例如：/cmd raise。"

                for name in uncategorized:
                    command = hasCommandByName(name)
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 5:
                embed.title = "德州撲克指令"
                embed.description = "要查看特定指令，請在 /cmd 命令之後輸入命令名稱。 例如：/cmd rc。"
                commands = bot.get_cog('Poker').get_commands()

                for command in commands:
                    embed.add_field(name=BOT_PREFIX + command.name, value=command.description, inline=False)

                await ctx.send(embed=embed)
            elif int(param) == 6:
                embed.title = "大統領指令"
                embed.description = "要查看特定指令，請在 /cmd 命令之後輸入命令名稱。 例如：/cmd rc。"
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
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            await ctx.send(embed=embed)

    @games.command(guild_ids=guild_ids, description="生成隨機卡。 可能會出現重複項。",
                      name="rc",
                    brief="生成隨機卡",
                    help="該命令從52張卡組中生成一張隨機卡。 格式為 /rc。 不需要任何參數。",
                    pass_context=True)
    async def rc(self, ctx: commands.Context):
        embed = discord.Embed(title="隨機卡", description="", color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
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


    '''@games.command(guild_ids=guild_ids, description="從卡組中拉出許多隨機卡。",
                      name="draw",
                    brief="從牌組中抽出若干張牌",
                    help="從卡組中拉出一些指定的隨機卡。\n"
                         "該指令的格式為 $draw <卡數>.\n 卡數應在1到52之間（含1和52）。",
                    pass_context=True)
    async def draw(self, ctx: commands.Context, cards: int = 1):
        embed = discord.Embed(title="抽卡", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
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


    @games.command(guild_ids=guild_ids, description="查看您的手。",
                      name="hand",
                    brief="查看你的手",
                    help="查看您手中的卡。 該機器人將為您PM包含您的手的圖像。 格式為 /hand，不帶任何參數。",
                    pass_context=True)
    async def hand(self, ctx: commands.Context):
        embed = discord.Embed(title=ctx.author.name + "'s Hand", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)

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


    @games.command(guild_ids=guild_ids, description="Set sorting type. 'p' for (3 low, 2 high), 'd' for (A low, K high), 's' for (diamonds - spades).",
                      name="setsort",
                    brief="Set sorting type",
                    aliases=['ss'],
                    help="/setsort <sorttype>. 'p' for 3 lowest, 2 highest, 'd' for default, 's' for by suit.",
                    pass_context=True)
    async def setsort(self, ctx: commands.Context, sorttype: str = None):
        embed = discord.Embed(title="排序方式", description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
        embed.add_field(name="大統領-樣式 (p)", value="3 - K, A, 2", inline=False)
        embed.add_field(name="默認 (d)", value="A - K", inline=False)
        embed.add_field(name="Suits (s)", value="Ace of Diamonds - King of Spades", inline=False)

        global order, presOrder, ORDER

        if sorttype is None:
            embed.description = "沒有提供排序類型。"
            await ctx.send(embed=embed)
            return

        if sorttype == "d":
            embed.description = "排序類型設置為默認(d)。"
            ORDER = order
            DBConnection.updateUserSortPref(str(ctx.author.id), sorttype)
        elif sorttype == "p":
            embed.description = "排序類型設置為“大統領-樣式(p)”。"
            ORDER = presOrder
            DBConnection.updateUserSortPref(str(ctx.author.id), sorttype)
        elif sorttype == "s":
            embed.description = "排序類型設置為 Suits-Style."
            ORDER = suitOrder
            DBConnection.updateUserSortPref(str(ctx.author.id), sorttype)
        else:
            embed.description = "Try 'd', 'p', or 's'."

        await ctx.send(embed=embed)


    @games.command(guild_ids=guild_ids, description="開始遊戲。",
                      name="game",
                    brief="開始遊戲",
                    aliases=['5card'],
                    help="使用此命令開始新遊戲。 您只能在遊戲之外使用此命令。 格式為 /game，不帶參數。",
                    pass_context=True)
    async def game(self, ctx: commands.Context):
        global gameList

        channelGame = getGameByChannel(ctx.channel)
        if channelGame is not None:
            embed = discord.Embed(title='德州撲克', description="該頻道已經有一個活躍的遊戲。", color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name="遊戲編號", value=str(channelGame.id))
            embed.set_footer(text="使用 /in <遊戲編號> 加入遊戲。")
            await ctx.respond(embed=embed)
            return

        if checkInGame(ctx.author):
            embed = discord.Embed(title='德州撲克', description="您已經在玩遊戲。", color=0x00ff00)
            embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            await ctx.respond(embed=embed)
            return

        await ctx.defer()

        emoji1 = '1️⃣'
        #emoji2 = '2️⃣'
        embed = discord.Embed(title="遊戲選擇", description="通過使用給定的表情符號對此消息做出反應來選擇遊戲類型。", color=0x00ff00)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
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
            await ctx.respond(embed=discord.Embed(title="遊戲選擇", description="沒有人及時選擇...", color=0x00ff00))
            return
        else:
            if str(rxn[0].emoji) == emoji1:
                id = randrange(100000, 1000000)
                while hasGame(id):
                    id = randrange(100000, 1000000)
                GAME = TexasHoldEm(ctx.channel, id)
                gameList.append(GAME)
                embed = discord.Embed(title="創建遊戲", description="創建了德州撲克遊戲。", color=0x00ff00)
                embed.add_field(name="遊戲編號", value=str(id))
                embed.add_field(name="加入", value="/in " + str(id))
                embed.set_thumbnail(url=GAME.imageUrl)
                await msg.delete()
                await ctx.send_followup(embed=embed)
            '''elif str(rxn[0].emoji) == emoji2:
                id = randrange(100000, 1000000)
                while hasGame(id):
                    id = randrange(100000, 1000000)
                GAME = President(ctx.channel, id)
                gameList.append(GAME)
                embed = discord.Embed(title="創建遊戲", description="創建了大統領遊戲。", color=0x00ff00)
                embed.add_field(name="遊戲編號", value=str(id))
                embed.add_field(name="加入", value="/in " + str(id))
                embed.set_thumbnail(url=GAME.imageUrl)
                await ctx.send(embed=embed)'''


    @games.command(guild_ids=guild_ids, description="使用6位數字id參加遊戲。",
                      name="in",
                    brief="加入遊戲。",
                    help="使用其6位數字id加入現有遊戲。 此命令的格式為 /in <6位數id>。",
                    pass_context=True)
    async def _in(self, ctx: commands.Context, id: int = None):
        embed = discord.Embed(title='德州撲克', description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)

        if checkInGame(ctx.author):
            embed.description = "您已經在玩遊戲。"
            await ctx.respond(embed=embed)
            return

        if id is None:
            embed.description = "您未提供6位數字的遊戲id。"
            await ctx.respond(embed=embed)
            return

        if not hasGame(id):
            embed.description = "無效的遊戲id。"
            await ctx.respond(embed=embed)
            return

        if not channelCheck(getGameByid(id), ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.respond(embed=embed)
            return

        GAME = getGameByid(id)

        if GAME.gameUnderway:
            embed.description = "這場比賽已經在進行中。 您現在不能加入。"
            embed.add_field(name="遊戲編號", value=GAME.ID)
            await ctx.respond(embed=embed)
            return

        GAME.players.append(str(ctx.author.id))
        embed.description = "您加入了遊戲。"

        playerList = ""
        for playerid in GAME.players:
            user = bot.get_user(int(playerid))
            playerList += user.name + "\n"

        embed.add_field(name="玩家們", value=playerList)
        embed.add_field(name="遊戲編號", value=GAME.ID)
        embed.set_thumbnail(url=GAME.imageUrl)
        await ctx.respond(embed=embed)


    @games.command(guild_ids=guild_ids, description="離開遊戲，如果遊戲已經在進行中，則放棄任何下注。",
                      name="out",
                    brief="離開您加入的遊戲，如果該遊戲已經在進行中，則放棄任何下注",
                    help="留下您與眾不同的遊戲，從而放棄您已經進行的任何下注。 格式為 /out，不帶任何參數。",
                    pass_context=True)
    async def out(self, ctx: commands.Context):
        embed = discord.Embed(title='德州撲克', description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
        if not checkInGame(ctx.author):
            embed.description = "您不在遊戲中。"
            await ctx.respond(embed=embed)
            return

        GAME = getGame(ctx.author)
        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.respond(embed=embed)
            return

        GAME.playerStatus[str(ctx.author.id)] = "Fold"
        GAME.players.remove(str(ctx.author.id))

        embed.description = "您離開了遊戲。"
        embed.add_field(name="遊戲編號", value=str(GAME.ID))
        embed.set_thumbnail(url=GAME.imageUrl)
        await ctx.respond(embed=embed)


    @games.command(guild_ids=guild_ids, description="開始遊戲。",
                      name="start",
                    brief="開始遊戲",
                    help="如果您還沒有開始遊戲，請先開始。 格式為 /start，不帶任何參數。",
                    pass_context=True)
    async def start(self, ctx: commands.Context):
        embed = discord.Embed(title='德州撲克', description=None, color=0x00ff00)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=bot.get_user(814558209859518555).display_avatar.url)
        if not checkInGame(ctx.author):
            embed.description = "您不在遊戲中。"
            await ctx.respond(embed=embed)
            return

        GAME = getGame(ctx.author)
        if not channelCheck(GAME, ctx.channel):
            embed.description = "您不在指定遊戲的頻道中。 請去那裡。"
            await ctx.respond(embed=embed)
            return

        if GAME.gameUnderway:
            embed.description = "您的遊戲已經開始。"
            embed.add_field(name="遊戲編號", value=str(GAME.ID))
            embed.set_thumbnail(url=GAME.imageUrl)
            await ctx.respond(embed=embed)
            return

        if len(GAME.players) == 1:
            embed.description = "你不能一個人玩！"
            await ctx.respond(embed=embed)
            return
        await ctx.respond('開始中...')
        await GAME.startGame()


    @games.command(guild_ids=guild_ids, description="使用十六進制代碼為您的手設置自定義顏色。",
                      name="setcolor",
                    brief="為您的手設置自定義顏色",
                    aliases=['sc', 'setColour'],
                    help="為顯示您的手的圖像設置自定義顏色。 需要格式為＃123ABC的有效顏色十六進制代碼。 格式為 /setcolor <十六進制代碼>。",
                    pass_context=True)
    async def setcolor(self, ctx: commands.Context, colour: str):
        embed = discord.Embed(title="自定義顏色", description=None, color=0x00ff00)
        embed.set_thumbnail(url="https://i.imgur.com/FCCMHHi.png")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
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

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Game(bot))