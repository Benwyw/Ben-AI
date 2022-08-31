import discord
from globalImport import bot
class Playlist:
    '''
    https://docs.pycord.dev/en/stable/api.html?highlight=embed#discord.Embed
    '''

    def __init__(self):
        # initial attributes
        self.title          = 'Playlist title'
        self.description    = 'Playlist description' # editable
        self.url            = 'https://i.imgur.com/i5OEMRD.png'
        self.color          = 0xFF0000
        self.author         = bot.user

        # footer
        self.footer_text = 'Playlist footer'
        self.footer_icon_url = 'https://i.imgur.com/i5OEMRD.png'

    def create_embed(self, description:str):
        print('execute create embed')
        template = discord.Embed(title=self.title, description=description, url=self.url, color=self.color, author=self.author)
        print('initialized template')
        template.set_footer(text=self.footer_text, icon_url=self.footer_icon_url)
        print('before return template')
        return template