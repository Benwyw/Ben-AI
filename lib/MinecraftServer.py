from lib.GlobalImport import *


class MinecraftServer():
    def status(self):
        addr = 'mc'
        data = requests.get(f"https://api.mcsrvstat.us/2/{addr}.benwyw.com").json()
        if data['debug']['ping'] is True:
            status = 'online'
        return status

    def status_seasonal(self):
        addr = 'play'
        status = 'offline'
        data = requests.get(f"https://api.mcsrvstat.us/2/{addr}.benwyw.com").json()
        if data['debug']['ping'] is True:
            status = 'online'
        return status
