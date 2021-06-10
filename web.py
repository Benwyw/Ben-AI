import os
from main import bot

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from DBConnection import DBConnection

from sanic import Sanic
from sanic.response import text

global data
data = 'null'

async def fetch():
    global data
    data = ''
    rankData = DBConnection.fetchAllRankData()

    count = 1
    for user in rankData:
        tempID = user[0]
        tempWIN = user[1]

        if count <= 5:
            user = await bot.fetch_user(tempID)

            data += "{}. {} (勝場: {})\n".format(count, user.display_name, tempWIN)

        count += 1

app = Sanic("app")

@app.listener('before_server_start')
async def initialize_scheduler(app, loop):
    await fetch()
    scheduler = AsyncIOScheduler({'event_loop': loop})
    scheduler.add_job(fetch, 'interval', hours=1)
    scheduler.start()

@app.route('/')
async def test(request):
    global data
    return text('{}\nUpdated every hour.'.format(data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=False, access_log=False)