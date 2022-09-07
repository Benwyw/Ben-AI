import urllib.request, json

class MinecraftServer():
    def checkStatus(self, seasonal:bool=False):
        addr = 'mc'
        if seasonal is True:
            addr = 'play'
        with urllib.request.urlopen(f"https://api.mcsrvstat.us/2/{addr}.benwyw.com") as url:
            data = json.loads(url.read().decode())

            pairs = data.items()

            for key, value in pairs:
                if key == 'debug':
                    if value['ping'] == True:
                        return 'online'
                    else:
                        return 'offline'

    def status(self):
        return self.checkStatus()

    def status_seasonal(self):
        return self.checkStatus(True)