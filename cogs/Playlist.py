from globalImport import *
import urllib.request

class Playlist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @classmethod
    def create_embed(self, ctx, title, desc):
        '''
        return default embed with default values
        '''
        # initial attributes
        #title          = title
        #description    = 'Playlist description' # editable
        #url            = 'https://i.imgur.com/i5OEMRD.png'
        color          = 0xFF0000
        author         = ctx.author
        thumbnail_icon_url        = 'https://i.imgur.com/i5OEMRD.png'

        # footer
        footer_text = '播放清單 (Beta)'
        footer_icon_url = 'https://i.imgur.com/i5OEMRD.png'

        embed = discord.Embed(title=title, description=desc, color=color) #url=url,
        embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        embed.set_thumbnail(url=thumbnail_icon_url)
        embed.set_footer(text=footer_text, icon_url=footer_icon_url)
        
    @slash_command(guild_ids=guild_ids, name='testplaylist', description='Testing playlist', description_localizations={"zh-TW": "測試播放清單"})
    #@commands.cooldown(1, 600, commands.BucketType.user)
    #cooldown=commands.CooldownMapping.from_cooldown(2, 60, commands.BucketType.default),
    async def _testplaylist(self, ctx:commands.Context, desc:str):
        #url:Option(str, "Test param", name_localizations={"zh-TW": "測試參數"})
        await ctx.defer()

        # log channel in FBenI
        log_channel = bot.get_channel(809527650955296848)
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))

        await log_channel.send('initialized template')
        

        template = discord.Embed(title=title, description=desc, url=url, color=color)
        template.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        template.set_thumbnail(url=url)
        template.set_footer(text=footer_text, icon_url=footer_icon_url)
        
        await log_channel.send(f'testtplaylist\nbefore send_followup\n\n{timestamp}')
        await ctx.send_followup(embed=template)

    @slash_command(guild_ids=guild_ids, name='createplaylist', description='Create playlist', description_localizations={"zh-TW": "建立播放清單"})
    async def _createplaylist(self, ctx:commands.Context, desc:str):
        #url:Option(str, "Test param", name_localizations={"zh-TW": "測試參數"})
        await ctx.defer()
        log('initialized template')
        # initial attributes
        title          = 'Playlist title'
        #description    = 'Playlist description' # editable
        url            = 'https://i.imgur.com/i5OEMRD.png'
        color          = 0xFF0000
        author         = ctx.author

        # footer
        footer_text = 'Playlist footer'
        footer_icon_url = 'https://i.imgur.com/i5OEMRD.png'

        template = discord.Embed(title=title, description=desc, url=url, color=color)
        template.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        template.set_thumbnail(url=url)
        template.set_footer(text=footer_text, icon_url=footer_icon_url)

        await ctx.send_followup(embed=template)

    @slash_command(guild_ids=guild_ids, name='insertplaylist', description='Insert music into existing playlist', description_localizations={"zh-TW": "將音樂加入播放清單"})
    async def _createplaylist(self, ctx:commands.Context, playlist_name:str, music_url:str):
        #url:Option(str, "Test param", name_localizations={"zh-TW": "測試參數"})
        await ctx.defer()
        await log('initialized template')

        desc = f'{playlist_name} | {music_url}'

        regex_code = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

        pattern = re.compile(regex_code)
        if not pattern.match(music_url):
            await ctx.send_followup('Youtube URL only')
        else:
            VideoID = pattern.search(music_url)
            for i in range(30):
                try:
                    print(VideoID.group(i))
                    if 'watch?v=' in VideoID.group(i) and 'https' not in VideoID.group(i):
                        VideoID = VideoID.group(i+1)
                        break
                except Exception as e:
                    pass
                    
            await log(f'Result: {VideoID}')

            params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % VideoID}
            url = "https://www.youtube.com/oembed"
            query_string = urllib.parse.urlencode(params)
            url = url + "?" + query_string

            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                await log(print(f"{data}"))
                await log(f"{data['title']}")
                desc = str(data['title'])
            await log(f'before final sending follow up line')
            await ctx.send_followup(embed=self.create_embed(ctx, f'已加入播放清單 {playlist_name}', f'{desc}'))
            await log(f'Successful insertplaylist validation')

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Playlist(bot))