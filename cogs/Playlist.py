from globalImport import *
import urllib.request

class Playlist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_embed(self, ctx, title, desc):
        '''
        return default embed with default values
        '''
        await log('inside create_embed')
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

        return embed

    '''    
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
    '''
    
    @slash_command(guild_ids=guild_ids, name='createplaylist', description='Create playlist', description_localizations={"zh-TW": "建立播放清單"})
    async def _createplaylist(self, ctx:commands.Context, playlist_name:str):
        #url:Option(str, "Test param", name_localizations={"zh-TW": "測試參數"})
        await ctx.defer()
        try:
            await log(f'start createplaylist {playlist_name}')

            # TODO db operations

            await ctx.send_followup(embed=await self.create_embed(ctx, f'已建立播放清單 {playlist_name}', ''))
            await log(f'end createplaylist {playlist_name}')
        except Exception as e:
            await ctx.send_followup('Error occured.')
            await log(f'error ocured during createplaylist {playlist_name}:\n\n{e}')

    @slash_command(guild_ids=guild_ids, name='insertplaylist', description='Insert music into existing playlist', description_localizations={"zh-TW": "將音樂加入播放清單"})
    async def _insertplaylist(self, ctx:commands.Context, playlist_name:str, music_url:str):
        #url:Option(str, "Test param", name_localizations={"zh-TW": "測試參數"})
        await ctx.defer()
        try:
            await log(f'start insertplaylist {playlist_name}')

            desc = f'{playlist_name} | {music_url}'

            regex_code = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

            pattern = re.compile(regex_code)
            if not pattern.match(music_url):
                await ctx.send_followup('Youtube URL only')
            else:
                VideoID = pattern.search(music_url)
                for i in range(30):
                    try:
                        await log(VideoID.group(i))
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
                    await log(data)
                    await log(f"{data['title']}")
                    desc = str(data['title'])

                # TODO db operations

                embed = await self.create_embed(ctx, f'已加入播放清單 __{playlist_name}__', f'{desc}')
                await ctx.send_followup(embed=embed)
                await log(f'end insertplaylist {playlist_name}')
        except Exception as e:
            await ctx.send_followup('Error occured.')
            await log(f'error occured during insertplaylist {playlist_name}:\n\n{e}')

    @slash_command(guild_ids=guild_ids, name='setplaylistthumbnail', description='Update playlist thumbnail', description_localizations={"zh-TW": "更新播放清單圖象"})
    async def _setplaylistthumbnail(self, ctx:commands.Context, playlist_name:str, thumbnail_url:str):
        await ctx.defer()
        try:
            await log(f'begin setplaylistthumbnail {playlist_name}')
            if thumbnail_url.startswith('http') and (thumbnail_url.endswith('.png') or thumbnail_url.endswith('jpg') or thumbnail_url.endswith('gif') or thumbnail_url.endswith('jpeg')):
                # TODO db operations
                await ctx.send_followup(embed=await self.create_embed(ctx, f'已更新播放清單 __{playlist_name}__ 圖象'))
            else:
                await ctx.send_followup('只容許圖象連結。')
            await log(f'end setplaylistthumbnail {playlist_name}')
        except Exception as e:
            await ctx.send_followup('Error occured.')
            await log(f'error ocured during setplaylistthumbnail {playlist_name}:\n\n{e}')

    @slash_command(guild_ids=guild_ids, name='myplaylist', description='Retrieve all my playlist', description_localizations={"zh-TW": "查閱所有我的播放清單"})
    async def _myplaylist(self, ctx:commands.Context):
        await ctx.defer()
        await ctx.send_followup('Completed myplaylist')

    @slash_command(guild_ids=guild_ids, name='getplaylist', description='Retrieve details of a specific playlist', description_localizations={"zh-TW": "查閱特定播放清單的曲目"})
    async def _getplaylist(self, ctx:commands.Context):
        await ctx.defer()
        await ctx.send_followup('Completed getplaylist')

    @slash_command(guild_ids=guild_ids, name='listallplaylist', description='List all playlist', description_localizations={"zh-TW": "查閱全域播放清單"})
    async def _listallplaylist(self, ctx:commands.Context):
        await ctx.defer()
        await ctx.send_followup('Completed listallplaylist')

    @slash_command(guild_ids=guild_ids, name='copytomyplaylist', description='Copy specific playlist to my playlist', description_localizations={"zh-TW": "複製特定播放清單至我的播放清單"})
    async def _copytomyplaylist(self, ctx:commands.Context):
        await ctx.defer()
        await ctx.send_followup('Completed copytomyplaylist')

    @slash_command(guild_ids=guild_ids, name='deleteplaylist', description='Delete specific playlist from my list', description_localizations={"zh-TW": "從我的播放清單刪除特定播放清單"})
    async def _deleteplaylist(self, ctx:commands.Context, playlist_name):
        await ctx.defer()
        try:
            await log(f'start deleteplaylist {playlist_name}')

            # TODO db operations

            await ctx.send_followup(embed=await self.create_embed(ctx, f'已刪除播放清單 {playlist_name}', ''))
            await log(f'end deleteplaylist {playlist_name}')
        except Exception as e:
            await ctx.send_followup('Error occured.')
            await log(f'error ocured during deleteplaylist {playlist_name}:\n\n{e}')


def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Playlist(bot))