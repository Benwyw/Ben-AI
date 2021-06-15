import urllib.request, json

def status():
    with urllib.request.urlopen("https://api.mcsrvstat.us/2/mc.benwyw.com") as url:
        data = json.loads(url.read().decode())

        pairs = data.items()

        for key, value in pairs:
            if key == 'debug':
                if value['ping'] == True:
                    return 'online'
                else:
                    return 'offline'