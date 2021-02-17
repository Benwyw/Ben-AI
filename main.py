# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Valentin B.
A simple music bot written in discord.py using youtube-dl.
Though it's a simple example, music bots are complex and require much time and knowledge until they work perfectly.
Use this as an example or a base for your own bot and extend it as you want. If there are any bugs, please let me know.
Requirements:
Python 3.5+
pip install -U discord.py pynacl youtube-dl
You also need FFmpeg in your PATH environment variable or the FFmpeg.exe binary in your bot's directory on Windows.
"""

import asyncio
import functools
import itertools
import math
import random
import os

import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
from dotenv import load_dotenv
from random import randrange

#========================Music========================
# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} 日'.format(days))
        if hours > 0:
            duration.append('{} 小時'.format(hours))
        if minutes > 0:
            duration.append('{} 分'.format(minutes))
        if seconds > 0:
            duration.append('{} 秒'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='正在播放',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='時間', value=self.source.duration)
                 .add_field(name='要求者', value=self.requester.mention)
                 .add_field(name='上載者', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='網址', value='[點擊]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.tempSource = None

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)

            elif self.loop == True:
                try:
                    async with timeout(60):
                        await self.songs.put(self.current)
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

                self.tempSource = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS))

                self.tempSource.volume = self._volume
                self.voice.play(self.tempSource, after=self.play_next_song)

            await self.current.source.channel.send(embed=self.current.create_embed())
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

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

    @commands.command(name='join', aliases=['j'], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """我要進來了。"""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
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
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """清除曲列、解除循環播放，離開語音頻道。"""

        if not ctx.voice_state.voice:
            return await ctx.send('未連接到任何語音通道。')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume', aliases=['v'])
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """較大細聲。"""

        if not ctx.voice_state.is_playing:
            return await ctx.send('目前沒有任何播放。')

        if 0 > volume > 100:
            return await ctx.send('音量必須在0到100之間')

        ctx.voice_state.volume = volume / 100
        await ctx.send('播放器音量設置為 {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """顯示目前播緊嘅歌。"""

        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """暫停目前播緊嘅歌。"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume', aliases=['r'])
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """恢復目前播緊嘅歌。"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop', aliases=['st'])
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """停止播放並清除曲列。"""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip', aliases=['s'])
    async def _skip(self, ctx: commands.Context):
        """跳過一首歌。 請求者可以自動跳過。
        要跳過該歌曲，需要3個跳過票。
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('依家冇嘢播緊...')

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

    @commands.command(name='queue', aliases=['q'])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """顯示曲列。
        您可以選擇指定要顯示的頁面。 每頁包含10個曲目。
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('曲列有堆空氣。')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} 首曲目:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='頁數 {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """洗牌曲列。"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('曲列有堆空氣。')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove', aliases=['rm'])
    async def _remove(self, ctx: commands.Context, index: int):
        """從曲列中刪除指定索引嘅歌曲。"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('曲列有堆空氣。')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop', aliases=['l'])
    async def _loop(self, ctx: commands.Context):
        """循環播放目前播放的歌曲。
        再次使用此指令以解除循環播放。
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('空白一片。')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop:
            await ctx.message.add_reaction('✅')
        elif not ctx.voice_state.loop:
            await ctx.message.add_reaction('❎')

    @commands.command(name='play', aliases=['p'])
    async def _play(self, ctx: commands.Context, *, search: str):
        """播放歌曲。
        如果隊列中有歌曲，它將一直排隊，直到其他歌曲播放完畢。
        如果未提供URL，此指令將自動從各個站點搜索。
        個站點的列表可以喺呢到揾到：https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('處理此請求時發生錯誤: {}'.format(str(e)))
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send('加咗首 {}'.format(str(source)))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot is already in a voice channel.')

#========================General========================
dmList = [254517813417476097,525298794653548751,562972196880777226,199877205071888384,407481608560574464,346518519015407626,349924747686969344,270781455678832641,363347146080256001,272977239014899713,262267347379683329,394354007650336769,372395366986940416,269394999890673664]

class Special(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='announce')
    @commands.is_owner()
    async def _announce(self, ctx: commands.Context, message):
        '''特別指令。公告。'''

        #client.get_channel("182583972662")
        for guild in bot.guilds:
            await guild.text_channels[0].send(message)

    @commands.command(name='dm')
    @commands.is_owner()
    async def _dm(self, ctx: commands.Context, target, content):
        """特別指令。同Bot DM，會由Bot DM Ben。"""

        target = target.lower()

        if 'ben' in target:
            memberID = 254517813417476097
        elif 'ronald' in target:
            memberID = 525298794653548751
        elif 'chris' in target:
            memberID = 562972196880777226
        elif 'anson' in target:
            memberID = 199877205071888384
        elif 'andy' in target:
            memberID = 407481608560574464

        elif 'pok' in target:
            memberID = 346518519015407626
        elif 'chester' in target:
            memberID = 349924747686969344
        elif 'daniel' in target:
            memberID = 270781455678832641
        elif 'kei' in target:
            memberID = 363347146080256001
        elif 'olaf' in target:
            memberID = 272977239014899713
        elif 'brian' in target:
            memberID = 262267347379683329
        elif 'blue' in target:
            memberID = 394354007650336769
        elif 'nelson' in target:
            memberID = 372395366986940416
        elif 'ivan' in target:
            memberID = 269394999890673664
        else:
            memberID = int(target)

        person = bot.get_user(memberID)
        try:
            await person.send(content)
        except Exception as e:
            channel = bot.get_channel(809527650955296848)
            await ctx.send("Unable to send message to: "+str(person))
            await channel.send(str(e))
        else:
            await ctx.send("Sent a message to: "+str(person))

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='hello')
    async def _hello(self, ctx: commands.Context):
        '''Say Hello to the AI'''

        await ctx.send("你好呀 "+str(ctx.author.display_name))

    @commands.command(name='call')
    async def _call(self, ctx: commands.Context):
        '''Ping爆佢!!!'''

        if len(ctx.message.mentions) == 0:
            await ctx.send("我唔會Ping: 空氣 / 其他Bot")
        else:
            embed = discord.Embed()
            embed.set_author(name="{} 揾你".format(ctx.author.display_name))
            for count in range(10):
                await ctx.send("<@{}>".format(ctx.message.mentions[0].id))
                await ctx.send(embed=embed)


bot = commands.Bot('$', description='使用Python的Ben AI，比由Java而成的Ben Kaneki更有效率。', intents=discord.Intents.all())
bot.add_cog(Music(bot))
bot.add_cog(Special(bot))
bot.add_cog(General(bot))


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="$help | 冇野幫到你"))
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))

'''
@bot.event
async def on_voice_state_update(member, before, after):
    # pylint: disable=unused-argument
    # If we're the only one left in a voice chat, leave the channel
    if member == bot.user and after.channel is None:
        print(member.guild)

    if member.bot:
        return
'''

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        seed = randrange(8)
        if seed == 0:
            msg = "**無效的令咒。 請使用** `$help` **來找出強制命令！**"
        elif seed == 1:
            msg = "**NANI！？** `$help`"
        elif seed == 2:
            msg = "**What 7 command is this ah, use** `$help` **la 7 head**"
        elif seed == 3:
            msg = "**JM9? 試下睇下個** `$help`"
        elif seed == 4:
            msg = "**Kys, u need some** `$help`"
        elif seed == 5:
            msg = "**打咩！！** `$help` **！！**"
        elif seed == 6:
            msg = "**Trash... use** `$help` **la**"
        elif seed == 7:
            msg = "**都冇呢個指令！！！！！！！ 用** `$help` **啦！！！！！！！**"

        await ctx.send(msg)
    if isinstance(error, commands.MissingRequiredArgument):
        seed = randrange(6)
        if seed == 0:
            msg = "**打漏野呀Ching**"
        if seed == 1:
            msg = "**你漏咗...個腦**"
        if seed == 2:
            msg = "**乜你唔覺得怪怪dick?**"
        if seed == 3:
            msg = "**「行返屋企」，你只係打咗「行返」，我點lung知行返去邊？**"
        if seed == 4:
            msg = "**你食飯未呀？Sor9完全無興趣知，我只知你打漏咗野呀。**"
        if seed == 5:
            msg = "**你係想我fill in the blanks? 填充題？？**"

        await ctx.send(msg)
    if isinstance(error, commands.MissingPermissions):
        seed = randrange(2)
        if seed == 0:
            msg = "**Sor9弱小的你冇權限用呢個指令:angry:**"
        elif seed == 1:
            msg = "**你確定你有lung力用呢個指令？**"

        await ctx.send(msg)

@bot.event
async def on_message(message):
    if message.guild is None and message.author != bot.user and message.author != bot.get_user(254517813417476097):
        #await channel.send("{}: {}".format(message.author,message.content))
        if message.author.id not in dmList:
            await bot.get_user(254517813417476097).send("{}({}): {}".format(message.author,message.author.id,message.content))
        else:
            await bot.get_user(254517813417476097).send("{}: {}".format(message.author,message.content))
    await bot.process_commands(message)

    if message.author == bot.user:
        return

    #Mentions Ben AI
    if bot.user.mentioned_in(message):
        seed = randrange(6)
        if seed == 0:
            msg = "你就是我的Master嗎"
        elif seed == 1:
            msg = "此後吾之劍與Ben同在，Ben之命運與吾共存。"
        elif seed == 2:
            msg = "Ben心之所向，即為我劍之所指。"
        elif seed == 3:
            msg = "I am the bone of my sword.\n" \
                  "Steel is my body, and fire is my blood.\n" \
                  "I have created over a thousand blades.\n" \
                  "Unknown to death,Nor known to life.\n" \
                  "Have withstood pain to create many weapons.\n" \
                  "Yet, those hands will never hold anything.\n" \
                  "So as I pray, unlimited blade works."
        elif seed == 4:
            msg = "Ben來承認，Ben來允許，Ben來背負整個世界。"
        elif seed == 5:
            msg = "輸給誰都可以，但是，決不能輸給自己。"

        await message.channel.send(msg)
        
    #Troll
    if '888' in message.content and message.content.startswith('8'):
        seed = randrange(7)
        if seed == 0:
            msg = "8888"
        elif seed == 1:
            msg = "7777"
        elif seed == 2:
            msg = "6666"
        elif seed == 3:
            msg = "9999"
        elif seed == 4:
            msg = "爸爸爸爸"
        elif seed == 5:
            msg = "伯伯伯伯"
        elif seed == 6:
            msg = "八八八八"

        await message.channel.send(msg, tts=True)

    #Shield
    if 'ben' in message.content.lower() and 'gay' in message.content.lower():
        await message.delete()
        if 'ben' not in message.author.display_name.lower():
            await message.channel.send(str(message.author.display_name)+" is gay")
        else:
            seed = randrange(5)
            if seed == 0:
                msg = "Pok is gay"
            elif seed == 1:
                msg = "Pok is fucking gay"
            elif seed == 2:
                msg = "Pok guy jai"
            elif seed == 3:
                msg = "Wow! Jennifer Pok-pez?"
            elif seed == 4:
                msg = "POKemon鳩"

            await message.channel.send(msg)

load_dotenv()
bot.run(os.getenv('TOKEN'))