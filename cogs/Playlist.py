from globalImport import *

class Playlist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_embed(self, description:str):
        await log_channel.send('execute create embed')
        template = discord.Embed(title=self.title, description=description, url=self.url, color=self.color, author=self.author)
        await log_channel.send('initialized template')
        template.set_footer(text=self.footer_text, icon_url=self.footer_icon_url)
        await log_channel.send('before return template')
        return template
        
    @slash_command(guild_ids=guild_ids, name='testplaylist', description='Testing playlist', description_localizations={"zh-TW": "測試播放清單"})
    #@commands.cooldown(1, 600, commands.BucketType.user)
    #cooldown=commands.CooldownMapping.from_cooldown(2, 60, commands.BucketType.default),
    async def _testplaylist(self, ctx:commands.Context, desc:str):
        #url:Option(str, "Test param", name_localizations={"zh-TW": "測試參數"})
        await ctx.defer()
        print('1')
        await log_channel.send(f'testtplaylist\nbefore send_followup\n\n{timestamp}')
        print('2')
        await ctx.send_followup(embed=self.create_embed(desc))

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Playlist(bot))