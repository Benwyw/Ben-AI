from globalImport import *
from lib.music.SongQueue import *
from lib.music.YTDLSource import *

class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.prevmsg = None
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
                #async with timeout(1800):  # 3 minutes
                    self.current = await self.songs.get()
                except Exception as e:#asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    print(e)
                    return

                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)

            elif self.loop == True:
                #try:
                #async with timeout(60):
                await self.songs.put(self.current)
                self.current = await self.songs.get()
                #except asyncio.TimeoutError:
                #self.bot.loop.create_task(self.stop())
                #return

                self.tempSource = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS))

                self.tempSource.volume = self._volume
                self.voice.play(self.tempSource, after=self.play_next_song)

            try:
                if self.prevmsg is not None:
                    await self.prevmsg.delete()
            except Exception as e:
                log_channel = bot.get_channel(809527650955296848)
                await log_channel.send(e)

            self.prevmsg = await self.current.source.channel.send(embed=self.current.create_embed())

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
