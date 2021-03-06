from apscheduler.schedulers.blocking import BlockingScheduler

from lab3 import db,user,datetime,json,requests,url,settingsClass
sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=60)
def timed_job():
    queryA = db.session.query(user)
    queryC=db.session.query(settingsClass)
    rez =queryC.first()
    for u in queryA.all():
        dif= datetime.now()-u.lastans
        params={'chat_id':u.tg_id,'text':'t'}
        if dif.seconds>rez.intr*60:
            params['text']='Повторяй'
            reply = {'keyboard': [[{'text': 'Повторить'}], [{'text': 'Отложить'}]], 'resize_keyboard': True}
            reply = json.dumps(reply)
            params['reply_markup'] = reply
            requests.post(url=url + '/sendMessage', data=params)

@sched.scheduled_job('interval', seconds=60)
def wake_up():
    r = requests.get('https://lab6py.herokuapp.com')
    print ('https://lab6py.herokuapp.com')
    print (r.status_code)

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=10)
def scheduled_job():
    print('This job is run every weekday at 10am.')

sched.start()