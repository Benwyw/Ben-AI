from lib.globalImport import *

class CyberSecurity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    security = SlashCommandGroup(guild_ids=guild_ids, name="security", description='CyberSecurity', description_localizations={"zh-TW": "電腦安全"})
        
    @security.command(guild_ids=guild_ids, name='scan', description='Retrieve virus scan report of the url', cooldown=commands.CooldownMapping.from_cooldown(2, 60, commands.BucketType.default), description_localizations={"zh-TW": "提取網址的病毒掃描報告"})
    #@commands.cooldown(1, 600, commands.BucketType.user)
    async def _scan(self, ctx:commands.Context, url:Option(str, "Paste the url", name_localizations={"zh-TW": "貼上網址"})):
        await ctx.defer()
        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
        try:
            url_param = url
            if not (url_param.startswith("http://") or url_param.startswith("https://")):
                url_param = f"http://{url_param}"
                
            if uri_validator(url_param):
                if '200' in str(post_scan(url_param, VIRUS_TOTAL_API_KEY)):
                    url_id = base64.urlsafe_b64encode(f"{url_param}".encode()).decode().strip("=")
                    
                    # GET Get URL analysis report
                    url = f"https://www.virustotal.com/api/v3/urls/{url_id}"

                    headers = {
                        "Accept": "application/json",
                        "x-apikey": f"{VIRUS_TOTAL_API_KEY}"
                    }

                    response = requests.get(url, headers=headers)

                    id = response.json()['data']['id']
                    attr = response.json()['data']['attributes']
                    
                    times_submitted = attr['times_submitted']
                    
                    harmless_count = attr['last_analysis_stats']['harmless']
                    malicious_count = attr['last_analysis_stats']['malicious']
                    suspicious_count = attr['last_analysis_stats']['suspicious']
                    undetected_count = attr['last_analysis_stats']['undetected']
                    timeout_count = attr['last_analysis_stats']['timeout']
                    
                    total_vendor_count = harmless_count+malicious_count+suspicious_count+undetected_count+timeout_count
                    
                    # if any one of the vendor raise an concern, flag it
                    suspicious_image_url = "https://i.imgur.com/Cin3myh.png"
                    virus_image_url = "https://i.imgur.com/jNe8oI9.png"
                    no_virus_image_url = "https://i.imgur.com/tEwIaQL.png"
                    if malicious_count + suspicious_count > 0:
                        if malicious_count > 0 and suspicious_count > 0:
                            if malicious_count > suspicious_count:
                                thumbnail_image_url = virus_image_url
                            elif malicious_count < suspicious_count:
                                thumbnail_image_url = suspicious_image_url
                        else:
                            if malicious_count > 0:
                                thumbnail_image_url = virus_image_url
                            elif suspicious_count > 0:
                                thumbnail_image_url = suspicious_image_url
                    else:
                        thumbnail_image_url = no_virus_image_url
                        
                    if thumbnail_image_url == no_virus_image_url:
                        color = 0x00ff00
                    if thumbnail_image_url == virus_image_url:
                        color = 0xff0000
                    if thumbnail_image_url == suspicious_image_url:
                        color = 0xffff00
                        
                    if ctx.guild.id in (guild_BenKaChu, guild_BrianLeeGaming, guild_BrianLeeGaming): #chi
                        chi_embed = discord.Embed(title = "防毒Ben件", color=color, description = f"使用與{total_vendor_count}位防毒供應商合作的VirusTotal。")
                        chi_embed.set_author(name='VirusTotal', url=f"https://www.virustotal.com/gui/url/{id}?nocache=1", icon_url="https://i.imgur.com/E7cIWC1.png")
                        chi_embed.set_thumbnail(url=f"{thumbnail_image_url}")
                        chi_embed.add_field(name="無害", value=f"{harmless_count}", inline=True)
                        chi_embed.add_field(name="惡意", value=f"{malicious_count}", inline=True)
                        chi_embed.add_field(name="可疑", value=f"{suspicious_count}", inline=True)
                        chi_embed.add_field(name="未測", value=f"{undetected_count}", inline=True)
                        chi_embed.add_field(name="逾時", value=f"{timeout_count}", inline=True)
                        chi_embed.add_field(name="提交次數", value=f"{times_submitted}", inline=True)
                        
                        if malicious_count != 0:
                            malicious_msg = ""
                            for vendor in attr['last_analysis_results']:
                                if attr['last_analysis_results'][vendor]['category'] == 'malicious':
                                    if malicious_msg == "":
                                        malicious_msg = f"{attr['last_analysis_results'][vendor]['engine_name']}: {attr['last_analysis_results'][vendor]['result']}"
                                    else:
                                        malicious_msg += f"\n{attr['last_analysis_results'][vendor]['engine_name']}: {attr['last_analysis_results'][vendor]['result']}"
                            chi_embed.add_field(name="惡意資訊", value=f"{malicious_msg}")
                        
                        if suspicious_count != 0:
                            suspicious_msg = ""
                            for vendor in attr['last_analysis_results']:
                                if attr['last_analysis_results'][vendor]['category'] == 'suspicious':
                                    if suspicious_msg == "":
                                        suspicious_msg = f"{attr['last_analysis_results'][vendor]['engine_name']}: {attr['last_analysis_results'][vendor]['result']}"
                                    else:
                                        suspicious_msg += f"\n{attr['last_analysis_results'][vendor]['engine_name']}: {attr['last_analysis_results'][vendor]['result']}"
                            chi_embed.add_field(name="可疑資訊", value=f"{suspicious_msg}")
                            
                        chi_embed.set_footer(text=timestamp)
                        result = chi_embed
                        
                    else: #eng
                        eng_embed = discord.Embed(title = "AntiBenrus", color=color, description = f"An API call to VirusTotal with {total_vendor_count} Security Vendors.")
                        eng_embed.set_author(name='VirusTotal', url=f"https://www.virustotal.com/gui/url/{id}?nocache=1", icon_url="https://i.imgur.com/E7cIWC1.png")
                        eng_embed.set_thumbnail(url=f"{thumbnail_image_url}")
                        eng_embed.add_field(name="Harmless", value=f"{harmless_count}", inline=True)
                        eng_embed.add_field(name="Malicious", value=f"{malicious_count}", inline=True)
                        eng_embed.add_field(name="Suspicious", value=f"{suspicious_count}", inline=True)
                        eng_embed.add_field(name="Undetected", value=f"{undetected_count}", inline=True)
                        eng_embed.add_field(name="Timeout", value=f"{timeout_count}", inline=True)
                        eng_embed.add_field(name="Times submitted", value=f"{times_submitted}", inline=True)
                        
                        if malicious_count != 0:
                            malicious_msg = ""
                            for vendor in attr['last_analysis_results']:
                                if attr['last_analysis_results'][vendor]['category'] == 'malicious':
                                    if malicious_msg == "":
                                        malicious_msg = f"{attr['last_analysis_results'][vendor]['engine_name']}: {attr['last_analysis_results'][vendor]['result']}"
                                    else:
                                        malicious_msg += f"\n{attr['last_analysis_results'][vendor]['engine_name']}: {attr['last_analysis_results'][vendor]['result']}"
                            eng_embed.add_field(name="Malicious info", value=f"{malicious_msg}")
                        
                        if suspicious_count != 0:
                            suspicious_msg = ""
                            for vendor in attr['last_analysis_results']:
                                if attr['last_analysis_results'][vendor]['category'] == 'suspicious':
                                    if suspicious_msg == "":
                                        suspicious_msg = f"{attr['last_analysis_results'][vendor]['engine_name']}: {attr['last_analysis_results'][vendor]['result']}"
                                    else:
                                        suspicious_msg += f"\n{attr['last_analysis_results'][vendor]['engine_name']}: {attr['last_analysis_results'][vendor]['result']}"
                            eng_embed.add_field(name="Suspicious info", value=f"{suspicious_msg}")
                            
                        eng_embed.set_footer(text=timestamp)
                        result = eng_embed
                else:
                    result = "Scan failure."
            else:
                result = "This is not a valid url."
        except Exception as e:
            result = f'An error occured:\n{e}'
            await ctx.send_followup(f'{result}\n{timestamp}')
        else:
            if isinstance(result, str):
                await ctx.send_followup(f'{result}')
            else:
                await ctx.send_followup(embed=result)
    
def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(CyberSecurity(bot))