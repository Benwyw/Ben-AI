from globalImport import *

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @slash_command(guild_ids=guild_ids, name='hello')
    async def _hello(self, ctx: commands.Context):
        '''Say Hello to the AI'''

        await ctx.respond("你好呀 "+str(ctx.author.display_name))
        await ctx.send_followup("你好你好")

    @slash_command(guild_ids=guild_ids, name='ping')
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

    @slash_command(guild_ids=guild_ids, name='news')
    async def _news(self, ctx:commands.Context, search=None, language=None):
        """新聞 zh=中文 en=英文 默認中文"""

        if ctx.guild.id == 351742829254410250 and ctx.channel.id == 356782441777725440 or ctx.guild.id == 671654280985313282 and ctx.channel.id in [684024056944787489, 903247995682824242, 717424039387201536, 684024142135296059]:
            await ctx.respond('由於指令結果會洗版，已在主頻道禁用，請在其他頻道執行。')
            return
            
        await ctx.defer()
        results = None

        if language is None or language in ('cn', 'chi', 'chinese', 'tw', 'hk', 'hongkong', 'zh', 'taiwan'):
            language = 'zh'
        else:
            language = 'en'


        if search is None:
            # /v2/top-headlines
            results = newsapi.get_top_headlines(#q='bitcoin',
                                                #sources='bbc-news,the-verge',
                                                #category='business',
                                                language=language,
                                                country='hk')
        else:
            # /v2/everything
            results = newsapi.get_everything(q=search,
                                            #sources='bbc-news,the-verge',
                                            #domains='bbc.co.uk,techcrunch.com',
                                            language=language,
                                            sort_by='publishedAt',
                                            page=1)
        for result in results['articles']:

            title = result['title']
            url = result['url']
            urlToImage = result['urlToImage'] if result['urlToImage'] is not None and 'http' in result['urlToImage'] and '://' in result['urlToImage'] else 'https://i.imgur.com/UdkSDcb.png'
            authorName = result['source']['name']
            author = result['author']
            description = result['description']
            publishedAt = result['publishedAt']
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

            await ctx.send_followup(embed=embed)

    @slash_command(guild_ids=guild_ids, name='stock')
    async def _stock(self, ctx:commands.Context, stock_name):
        """股市圖表"""
        await ctx.defer()

        response = requests.get('https://www.marketwatch.com/tools/quotes/lookup.asp?siteid=mktw&Lookup={}&Country=us&Type=All'.format(stock_name))
        if response.status_code == 200:
            for line in response.content.decode('utf-8').splitlines():
                if '<td class="bottomborder">' in line:
                    stock_name = line.split('<',3)[2].split('>')[-1]
                    break
                if '<span class="company__ticker">' in line:
                    stock_name = line.split('>',1)[1].split('<',1)[0]
                    break

        else:
            await ctx.send_followup("marketwatch連線失敗！？")
            return

        response.close()
        e = discord.Embed()

        # Initialize IO
        data_stream = io.BytesIO()

        data, meta_data = ts.get_intraday(symbol=stock_name,interval='1min', outputsize='full')
        if str(data.head(2)) is not None:
            pass
        else:
            await ctx.send_followup("symbol搜尋失敗！？")
            return
        #ctx.send(str(data.head(2)))

        data = data.drop(columns='5. volume',axis=1)
        data.plot()
        plt.title('Intraday Times Series for the {} stock (1 min)'.format(stock_name))
        plt.grid()
        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()
        #plt.show()

        #create file
        data_stream.seek(0)
        chart = discord.File(data_stream,filename="stock_chart.png")
        data_stream.close()

        e.set_image(
            url="attachment://stock_chart.png"
        )

        await ctx.send_followup(embed=e, file=chart)

    @slash_command(guild_ids=guild_ids, name='cov', aliases=['covid','cov19','covid-19'])
    async def _cov(self, ctx:commands.Context):
        """本港冠狀病毒病的最新情況"""
        await ctx.defer()

        csv_url="http://www.chp.gov.hk/files/misc/latest_situation_of_reported_cases_covid_19_chi.csv"
        response = requests.get(csv_url)

        response.close()
        e = discord.Embed()

        # Initialize IO
        data_stream = io.BytesIO()

        file_object = io.StringIO(response.content.decode('utf-8'))
        pd.set_option('display.max_rows', 60)
        pd.set_option('display.max_columns', None)
        data = pd.read_csv(file_object)

        data = data.tail(60)

        try:
            #data['更新日期'] = data['更新日期'].map(lambda x: datetime.strptime(str(x), '%d/%m/%y'))
            #data['更新日期'] = pd.to_date(data['更新日期'])
            pass
            #df['date'] = pd.to_datetime(df['date'])  
            #print(data['更新日期'])
        except Exception as e:
            await ctx.send_followup('<@{}>\n{}\n{}'.format(bot.owner_id,e,data['更新日期']))
            return
        x = data['更新日期']
        y = data['確診個案']
        y2 = data['死亡']
        y3 = data['出院']
        y4 = data['疑似個案']
        y5 = data['住院危殆個案']
        y6 = data['嚴重急性呼吸綜合症冠狀病毒2的陽性檢測個案']

        plt.plot(x, y, label="confirmed")
        plt.plot(x, y2, label="death")
        plt.plot(x, y3, label="discharge")
        plt.plot(x, y4, label="probable")
        plt.plot(x, y5, label="hospitalised and critical")
        plt.plot(x, y6, label="positive for SARS-CoV-2")
        plt.title("Latest situation of reported cases of COVid-19 in Hong Kong")
        plt.xlabel('past 60 days')
        plt.ylabel('amount')
        plt.gcf().autofmt_xdate()

        #print(data.tail(1))
        plt.legend()
        plt.grid()
        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()

        #create file
        data_stream.seek(0)
        chart = discord.File(data_stream,filename="cov_latest.png")
        data_stream.close()

        e.set_image(
            url="attachment://cov_latest.png"
        )

        latest = data['確診個案'].iloc[-1]
        if latest is None or str(latest) == 'nan':
            latest = data['嚴重急性呼吸綜合症冠狀病毒2的陽性檢測個案'].iloc[-1]

        await ctx.send_followup(content='__確診個案__\n最高: {}\n最低: {}\n平均: {}\n中位: {}\n現時: {}'.format(data['確診個案'].max(), data['確診個案'].min(), data['確診個案'].mean(), data['確診個案'].median(), latest), embed=e, file=chart)

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(General(bot))