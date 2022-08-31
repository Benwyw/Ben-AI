from globalImport import *

class Playlist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @slash_command(guild_ids=guild_ids, name='testplaylist', description='Testing playlist', description_localizations={"zh-TW": "測試播放清單"})
    #@commands.cooldown(1, 600, commands.BucketType.user)
    #cooldown=commands.CooldownMapping.from_cooldown(2, 60, commands.BucketType.default),
    async def _testplaylist(self, ctx:commands.Context, desc:str):
        #url:Option(str, "Test param", name_localizations={"zh-TW": "測試參數"})
        await ctx.defer()
        print('1')

        # log channel in FBenI
        log_channel = bot.get_channel(809527650955296848)
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))

        await log_channel.send('initialized template')
        # initial attributes
        title          = 'Playlist title'
        #description    = 'Playlist description' # editable
        url            = 'https://i.imgur.com/i5OEMRD.png'
        color          = 0xFF0000
        author         = bot.user

        # footer
        footer_text = 'Playlist footer'
        footer_icon_url = 'https://i.imgur.com/i5OEMRD.png'
        print('2')
        template = discord.Embed(title=title, description=desc, url=url, color=color)
        print('3')
        template.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        print('4')
        template.set_thumbnail(url=url)
        print('5')
        template.set_footer(text=footer_text, icon_url=footer_icon_url)
        print('6')
        await log_channel.send(f'testtplaylist\nbefore send_followup\n\n{timestamp}')
        print('7')
        await ctx.send_followup(embed=self.create_embed(desc))

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Playlist(bot))