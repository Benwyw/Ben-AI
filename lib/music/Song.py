from globalImport import *
from lib.music.YTDLSource import YTDLSource

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