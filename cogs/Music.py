from locale import strcoll
from pickletools import string1
from lib.GlobalImport import *
from lib.music.VoiceState import VoiceState
from lib.music.YTDLSource import YTDLSource
from lib.music.Song import *
from lib.music.SongQueue import *

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}
        self.prevmsg = None

    music = SlashCommandGroup(guild_ids=guild_ids, name="music", description='Music', description_localizations={"zh-TW": "音樂"})

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('該命令不能在私訊中使用.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('發生錯誤: {}'.format(str(error)))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_state = member.guild.voice_client

        if voice_state is not None and len(voice_state.channel.members) == 1 or member == bot.user and after.channel is None:
            # You should also check if the song is still playing
            try:
                voice_state.stop()
            except:
                pass
            try:
                await voice_state.disconnect()
                '''for task in asyncio.Task.all_tasks(bot.loop):
                    await task.cancel()'''
                #self.voice_states.get(member.guild.id).audio_player.cancel()
                
            except:
                pass
            try:
                del self.voice_states[member.guild.id]
            except:
                pass
        else:
            return
        
    @music.command(guild_ids=guild_ids, name='forcejoin', aliases=['fj'], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """我要進來了。(強制)"""
        
        await ctx.defer()
        
        destination = ctx.author.voice.channel
        
        try:
            ctx.guild.voice_client.stop() #await ctx.voice_state.stop()
        except Exception as e:
            await log(f'`/music leave`\nctx.guild.voice_client.stop()\n{e}')
        try:
            await ctx.guild.voice_client.disconnect()
        except Exception as e:
            await log(f'`/music leave`\nawait ctx.guild.voice_client.disconnect()\n{e}')
        try:
            del self.voice_states[ctx.guild.id]
        except Exception as e:
            await log(f'`/music leave`\ndel self.voice_states[ctx.guild.id]\n{e}')
        
        try:
            if ctx.voice_state.voice:
                await ctx.voice_state.voice.move_to(destination)
                await ctx.respond(':thumbsup:')
                return

            ctx.voice_state.voice = await destination.connect()
        except Exception as e:
            pass
        
        await ctx.send_followup(':thumbsup:')

    @music.command(guild_ids=guild_ids, name='join', aliases=['j'], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """我要進來了。"""
        
        await ctx.defer()

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.respond(':thumbsup:')
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.send_followup(':thumbsup:')

    @music.command(guild_ids=guild_ids, name='join2', aliases=['j2'], invoke_without_subcommand=True)
    @commands.has_any_role('Ben AI')
    async def _join2(self, ctx: commands.Context):
        """我要進來了。"""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @music.command(guild_ids=guild_ids, name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """召喚我去某個語音頻道。
        如果無講明邊個語音頻道，我要進來了。
        """

        if not channel and not ctx.author.voice:
            raise VoiceError('您既未連接到語音通道，也未指定要加入的通道。')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            await ctx.respond(':thumbsup:')
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.respond(':thumbsup:')

    @music.command(guild_ids=guild_ids, name='leave', aliases=['disconnect'])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """清除曲列、解除循環播放，離開語音頻道。"""

        if not ctx.guild.voice_client: #if not ctx.voice_state.voice:
            return await ctx.respond('未連接到任何語音通道。')

        try:
            ctx.guild.voice_client.stop() #await ctx.voice_state.stop()
        except Exception as e:
            await log(f'`/music leave`\nctx.guild.voice_client.stop()\n{e}')
        try:
            await ctx.guild.voice_client.disconnect()
        except Exception as e:
            await log(f'`/music leave`\nawait ctx.guild.voice_client.disconnect()\n{e}')
        try:
            del self.voice_states[ctx.guild.id]
        except Exception as e:
            await log(f'`/music leave`\ndel self.voice_states[ctx.guild.id]\n{e}')
            
        await ctx.respond(':middle_finger:')

    @music.command(guild_ids=guild_ids, name='volume', aliases=['v'])
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """較大細聲。"""

        if not ctx.voice_state.is_playing:
            return await ctx.respond('目前沒有任何播放。')

        if 0 > volume > 100:
            return await ctx.respond('音量必須在0到100之間')

        ctx.voice_state.volume = volume / 100
        await ctx.respond('播放器音量設置為 {}%'.format(volume))

    @music.command(guild_ids=guild_ids, name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """顯示目前播緊嘅歌。"""

        await ctx.respond(embed=ctx.voice_state.current.create_embed())

    @music.command(guild_ids=guild_ids, name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """暫停目前播緊嘅歌。"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.respond('⏯')

    @music.command(guild_ids=guild_ids, name='resume', aliases=['r'])
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """恢復目前播緊嘅歌。"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.respond('⏯')

    @music.command(guild_ids=guild_ids, name='stop', aliases=['st'])
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """停止播放並清除曲列。"""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.respond('⏹')

    @music.command(guild_ids=guild_ids, name='skip', aliases=['s'])
    async def _skip(self, ctx: commands.Context):
        """跳過一首歌。 請求者可以自動跳過。
        要跳過該歌曲，需要3個跳過票。
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('依家冇嘢播緊...')
        '''
        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)
        
            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('已增加跳過投票，目前位於 **{}/3**'.format(total_votes))
        
        else:
            await ctx.send('您已經投票跳過這首歌。')
        '''
        await ctx.respond('⏭')
        ctx.voice_state.skip()
    @music.command(guild_ids=guild_ids, name='queue', aliases=['q'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """顯示曲列。
        您可以選擇指定要顯示的頁面。 每頁包含10個曲目。
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('曲列有堆空氣。')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} 首曲目:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='頁數 {}/{}'.format(page, pages)))
        await ctx.respond(embed=embed)

    @music.command(guild_ids=guild_ids, name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """洗牌曲列。"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('曲列有堆空氣。')

        ctx.voice_state.songs.shuffle()
        await ctx.respond('✅')

    @music.command(guild_ids=guild_ids, name='remove', aliases=['rm'])
    async def _remove(self, ctx: commands.Context, index: int):
        """從曲列中刪除指定索引嘅歌曲。"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.respond('曲列有堆空氣。')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.respond('✅')

    @music.command(guild_ids=guild_ids, name='loop', aliases=['l'])
    async def _loop(self, ctx: commands.Context):
        """循環播放目前播放的歌曲。
        再次使用此指令以解除循環播放。
        """

        if not ctx.voice_state.is_playing:
            return await ctx.respond('空白一片。')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop:
            await ctx.respond('✅')
        elif not ctx.voice_state.loop:
            await ctx.respond('❎')

    @music.command(guild_ids=guild_ids, name='play', aliases=['p'], description='Play music', description_localizations={"zh-TW": "播放音樂"})
    async def _play(self, ctx: commands.Context, *, search: str):
        """播放歌曲。
        如果隊列中有歌曲，它將一直排隊，直到其他歌曲播放完畢。
        如果未提供URL，此指令將自動從各個站點搜索。
        個站點的列表可以喺呢到揾到：https://rg3.github.io/youtube-dl/supportedsites.html
        """

        #ctx.voice_stats.voice --> ctx.voice_client
        #ctx.invoke --> commands.Context.invoke, 'cmd name' | (original) | ctx
        await ctx.defer()

        if not ctx.voice_client:
            #await commands.Context.invoke('join2', self._join2, ctx)
            destination = ctx.author.voice.channel
            if ctx.voice_state.voice:
                await ctx.voice_state.voice.move_to(destination)
                return

            ctx.voice_state.voice = await destination.connect()

        async with ctx.typing():
            try:
                sourceList = await asyncio.wait_for(YTDLSource.create_source(ctx, search, loop=self.bot.loop), 180)
            #except YTDLError as e:
            except asyncio.TimeoutError:
                timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
                BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                await BDS_Log_Channel.send('{}\n\n__TimeoutError__ occured in YTDLSource.create_source\n{}'.format(e,timestamp))
                await ctx.send_followup('處理此請求時發生錯誤: 處理時間過長 (3分鐘以上)')
            except Exception as e:
                timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
                BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                await BDS_Log_Channel.send('{}\n\nError occured in YTDLSource.create_source\n{}'.format(e,timestamp))
                await ctx.send_followup('處理此請求時發生錯誤: {}'.format(str(e)))
            else:
                for source in sourceList:
                    try:
                        song = Song(source)
                        await ctx.voice_state.songs.put(song)
                        await ctx.send_followup('加咗首 {}'.format(str(source)))
                    except Exception as e:
                        timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
                        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                        await BDS_Log_Channel.send('{}\n\nError occured in for source in sourceList\n{}'.format(e,timestamp))

    @music.command(guild_ids=guild_ids, name='playplaylist', aliases=['pp'], description='Play playlist', description_localizations={"zh-TW": "播放播放清單"})
    async def _playplaylist(self, ctx: commands.Context, *, playlist_id: int, random_shuffle: bool=False, start_id: int=None):
        """播放歌曲。
        如果隊列中有歌曲，它將一直排隊，直到其他歌曲播放完畢。
        如果未提供URL，此指令將自動從各個站點搜索。
        個站點的列表可以喺呢到揾到：https://rg3.github.io/youtube-dl/supportedsites.html
        """

        #ctx.voice_stats.voice --> ctx.voice_client
        #ctx.invoke --> commands.Context.invoke, 'cmd name' | (original) | ctx
        await ctx.defer()
        
        playlist = DBConnection.getPlaylist(None, playlist_id)
        if not playlist or playlist is None:
            await ctx.send_followup('指定之播放清單不存在 或 沒有曲目。')
        else:
            if not ctx.voice_client:
                #await commands.Context.invoke('join2', self._join2, ctx)
                destination = ctx.author.voice.channel
                if ctx.voice_state.voice:
                    await ctx.voice_state.voice.move_to(destination)
                    return

                ctx.voice_state.voice = await destination.connect()

            async with ctx.typing():
                try:
                    if random_shuffle:
                        random.shuffle(playlist)
                    for pl in playlist:
                        try:
                            if start_id is not None:
                                if int(pl[0]) >= start_id:
                                    sourceList = await asyncio.wait_for(YTDLSource.create_source(ctx, f'https://www.youtube.com/watch?v={pl[4]}', loop=self.bot.loop), 180)
                                else:
                                    continue
                            else:
                                sourceList = await asyncio.wait_for(YTDLSource.create_source(ctx, f'https://www.youtube.com/watch?v={pl[4]}', loop=self.bot.loop), 180)
                        #except YTDLError as e:
                        except asyncio.TimeoutError:
                            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
                            BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                            await BDS_Log_Channel.send('{}\n\n__TimeoutError__ occured in YTDLSource.create_source\n{}'.format(e,timestamp))
                            await ctx.send_followup('處理此請求時發生錯誤: 處理時間過長 (3分鐘以上)')
                        except Exception as e:
                            timestamp = str(datetime.now(pytz.timezone('Asia/Hong_Kong')))
                            BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                            await BDS_Log_Channel.send('{}\n\nError occured in YTDLSource.create_source\n{}'.format(e,timestamp))
                            await ctx.send_followup('處理此請求時發生錯誤: {}'.format(str(e)))
                        else:
                            if sourceList:
                                for source in sourceList:
                                    try:
                                        song = Song(source)
                                        await ctx.voice_state.songs.put(song)
                                        await ctx.send_followup('加咗首 {}'.format(str(source)))
                                    except Exception as e:
                                        BDS_Log_Channel = bot.get_channel(809527650955296848) #Ben Discord Bot - logs
                                        await BDS_Log_Channel.send('{}\n\nError occured in for source in sourceList\n{}'.format(e,timestamp))
                except Exception as e:
                        await log(f'{e}')

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

def setup(
    bot: commands.Bot
) -> None:
    bot.add_cog(Music(bot))