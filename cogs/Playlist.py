from globalImport import *
import lib.template.Playlist as ltp

class Playlist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @slash_command(guild_ids=guild_ids, name='testplaylist', description='Testing playlist', description_localizations={"zh-TW": "測試播放清單"})
    #@commands.cooldown(1, 600, commands.BucketType.user)
    #cooldown=commands.CooldownMapping.from_cooldown(2, 60, commands.BucketType.default),
    async def _testplaylist(self, ctx:commands.Context, desc:str):
        #url:Option(str, "Test param", name_localizations={"zh-TW": "測試參數"})
        await ctx.defer()
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
        print('before send_followup')
        await ctx.send_followup(embed=ltp.Playlist.create_embed(desc))

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Playlist(bot))