from globalImport import *

class CyberSecurity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @slash_command(guild_ids=guild_ids, name='scan', description='Retrieve virus scan report of the url', cooldown=commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.default), description_localizations={"zh-TW": "提取網址的病毒掃描報告"})
    #@commands.cooldown(1, 600, commands.BucketType.user)
    async def _scan(self, ctx:commands.Context, url:Option(str, "Paste the url", name_localizations={"zh-TW": "貼上網址"})):
        await ctx.defer()
        try:
            result = url
            
            print('processing API')
            
            embed_r = 'embed'
        except Exception as e:
            result = f'An error occured:\n{e}'
        else:
            result = embed_r
        finally:
            await ctx.send_followup(f'{result}')
    
def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(CyberSecurity(bot))