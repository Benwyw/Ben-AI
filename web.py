import os, pytz

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from DBConnection import DBConnection

from sanic import Sanic
from sanic.response import text

global data, hk_now
data = 'null'
hk_now = 'null'

async def fetch():
    global data, hk_now
    data = ''
    rankData = DBConnection.fetchAllRankData()

    count = 1
    for user in rankData:
        tempID = str(user[0])
        tempWIN = str(user[1])

        if count <= 10:
            tempStar = ''
            for i in range(1,len(tempID)):
                tempStar += '*'

            userID = tempID[:4]+tempStar

            data += "{}. {} (勝場: {})\n".format(count, userID, tempWIN)

        count += 1

    tz = pytz.timezone('Asia/Hong_Kong')
    hk_now = datetime.now(tz)

app = Sanic("app")

@app.listener('before_server_start')
async def initialize_scheduler(app, loop):
    await fetch()
    scheduler = AsyncIOScheduler({'event_loop': loop})
    scheduler.add_job(fetch, 'interval', hours=1)
    scheduler.start()

@app.route('/')
async def test(request):
    global data, hk_now
    return text('{}\nUpdated: {}'.format(data, hk_now))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=False, access_log=False)