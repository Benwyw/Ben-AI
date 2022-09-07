import urllib.request, json

class MinecraftServer():
    def checkStatus(seasonal:bool=False):
        print('yo')
        addr = 'mc'
        status = 'offline'
        if seasonal is True:
            print('s')
            addr = 'play'
        print(addr)
        with urllib.request.urlopen(f"https://api.mcsrvstat.us/2/{addr}.benwyw.com") as url:
            data = json.loads(url.read().decode())

            pairs = data.items()

            for key, value in pairs:
                if key == 'debug':
                    if value['ping'] == True:
                        status = 'online'

        return status

    def status():
        return MinecraftServer.checkStatus()

    def status_seasonal():
        print('s')
        return MinecraftServer.checkStatus(True)