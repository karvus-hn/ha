from flask import Flask,request,Response,json
from flask import render_template
import json
import requests
import time
import random
import sqlite3
from datetime import datetime, date, time

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import MetaData, String, Integer,DateTime, ForeignKey

TOKEN = '1059696616:AAGcWDOvkpG2OFabcnFv9VZklF1Lj5ximxc'
API_URL = 'https://api.telegram.org/bot1059696616:AAGcWDOvkpG2OFabcnFv9VZklF1Lj5ximxc'
url=API_URL

engine = create_engine("postgres://zueltcpozckyiz:dcc13eeb6e9969ebb6842885ffc4d5d51b10da9c60801e26d939b77e91577b5f@ec2-46-137-156-205.eu-west-1.compute.amazonaws.com:5432/d67s20vrum3nv0", echo = False)

app = Flask(__name__)
app.config.from_pyfile('config.py')
#db = scoped_session(sessionmaker(bind=engine))
ccount=5

with open('english_words.json') as f:
    eng_words = json.load(f)

random.seed(2)

class TokenHolder:
    def __init__(self):
        self.cont=[]
    
    def check(self):
        for c in self.cont:
            timestamp = datetime.fromtimestamp(c['time'])
            dif= datetime.now()-timestamp
            if dif.days>=1:
                self.cont.remove(c)


    def ins(self,it):
        self.check()
        self.cont.append(it)

    def alr(self, it):
        try:
            a = next(e for e in self.cont if e['id'] == it['id'])
        except:
            self.ins(it)
            return False
        return True
        

tHolder=TokenHolder()

class UInfo:
    def __init__(self):
        self.SWord=''
        self.Cword=''
        self.pos=0
        self.cor=0
        self.rnd=0
dct={}

db = SQLAlchemy(app)
db.session.autocommit=True
class user(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    tg_id = db.Column(db.Integer(),unique=True)
    lastans=db.Column(db.DateTime())

    def __str__(self):
        return "<User ('%s','%s', '%s')>" % (self.id, self.tg_id, self.lastans)

class learning(db.Model):
    __tablename__='learning'
    word=db.Column(db.String(),primary_key=True)
    cnt=db.Column(db.Integer())
    lastans = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), ForeignKey('users.tg_id'),primary_key=True)
    user = db.relationship("user")

    def __str__(self):
        return "<Learning ('%s','%s', '%s','%s')>" % (self.user_id, self.word, self.lastans,self.cnt)

class settingsClass(db.Model):
    __tablename__='settings'
    id=db.Column(db.Integer(),primary_key=True)
    right = db.Column(db.Integer())
    intr = db.Column(db.Integer())
    rc = db.Column(db.Integer())

    def __str__(self):
        return "<Settings ('%s',' %s','%s','%s')>" % (self.id,self.right,self.intr,self.rc)

def GRound(chat_id,params):
    global end_words
    global dct
    global ccount
    queryA=db.session.query(user)
    queryB=db.session.query(learning)
    queryC=db.session.query(settingsClass)
    rez =queryC.first()
    count=rez.right
    x = random.randint(0,len(eng_words))
    r = random.choices(range(0,len(eng_words)),k=3)
    rt=99
    try:
        f = queryB.filter(learning.user_id==chat_id,learning.cnt<count ).all()
        if(len(f)==0):
            tempL = learning(user_id=chat_id, word=eng_words[x]['translation'],lastans=datetime.utcnow(),cnt=0)
            db.session.add(tempL)
            db.session.flush()
            f.append(tempL)
        db.session.commit()
        x = random.randint(0,len(f)-1)
        a=next(e for e in eng_words if e['translation'] == f[x].word)
        x=eng_words.index(a)

    except:
        pass
    while x in r:
        r = random.choices(range(0, len(eng_words)), k=3)
    r.append(x)
    r.sort()
    b=[dict(text=eng_words[a]['translation']) for a in r]
    b.append({'text':'привести пример'})
    dct[chat_id].Cword=eng_words[x]['translation']
    dct[chat_id].pos=x
    reply={'keyboard':[[b[0],b[1]],[b[2],b[3]],[b[4]]],'resize_keyboard':True}
    params['text']='Как переводится с английского слово "{word}"?'.format(word=eng_words[x]['word'])
    reply=json.dumps(reply)
    params['reply_markup']=reply
    requests.post(url=url+'/sendMessage',data=params)
    print('Ждем {word}.'.format(word=dct[chat_id].Cword))
    data={"id":chat_id,"word":dct[chat_id].Cword,"dt":datetime.utcnow()}
    #rezC=queryB.filter(learning.user_id==chat_id,learning.word==dct[chat_id].Cword ).first()  # вставляем слово
    #if rezC.cnt==None:
    #    tempL = learning(user_id=chat_id, word=dct[chat_id].Cword,lastans=datetime.utcnow(),cnt=0)
    #    db.session.add(tempL)
    #    db.session.commit()

@app.route('/settings')
def settings_1():
    queryC=db.session.query(settingsClass)
    rez =queryC.first()
    if rez==None:
        tempS=settingsClass(right=5,intr=30,rc=10)
        db.session.add(tempS)
        db.session.flush()
    return render_template('settings.html',count=rez.rc,rcount=rez.right,intr=rez.intr)

@app.route('/debug')
def debug():
    global dct
    global tHolder
    return render_template('debug.html',lst=dct,th=tHolder.cont)
@app.route('/settings/set',methods=['POST'])
def settings_set():
    if request.method == 'POST':
        queryC=db.session.query(settingsClass)
        rez =queryC.first()
        if rez==None:
            tempS=settingsClass(right=request.form.get('rcount'),intr=request.form.get('intr'),rc=request.form.get('count'))
            db.session.add(tempS)
            db.session.flush()
        else:
            rez.intr=request.form.get('intr')
            rez.right=request.form.get('rcount')
            rez.rc=request.form.get('count')
            db.session.flush()
        db.session.commit()
        return render_template('settings.html',count=rez.rc,rcount=rez.right,intr=rez.intr)
		
@app.route('/incoming', methods=['POST'])
def webhook():
    global dct
    global tHolder
    if request.method == 'POST':
        queryA=db.session.query(user)
        queryB=db.session.query(learning)
        queryC=db.session.query(settingsClass)
        rez =queryC.first()
        rc=rez.rc
        update = request.get_json()
        if "message" in update:
            if tHolder.alr({'id':update["message"]["message_id"],'time':update["message"]["date"]})==True:
                return Response(status=200)
            text = update["message"]["text"]
            chat_id = update["message"]["chat"]["id"]
            if chat_id in dct:
                pass
            else:
                dct[chat_id]=UInfo()
                rez =queryA.filter(user.tg_id==chat_id).first()                 # находим пользователя или вставляем
                if rez == None:
                    tempU=user(tg_id=chat_id,lastans=datetime.utcnow())
                    db.session.add(tempU)
                    #db.session.flush()
                db.session.commit()
            params={'chat_id':chat_id,'text':text}
            st=params['text'].split(' ')

            if params['text']=='Давай начнем!':
                dct[chat_id].rnd = 0
                dct[chat_id].cor = 0
                dct[chat_id].Cword=''
                GRound(chat_id,params)
            elif params['text']=='Повторить':
                dct[chat_id].rnd = 0
                dct[chat_id].cor = 0
                dct[chat_id].Cword=''
                GRound(chat_id,params)
            elif params['text']=='Отложить':
                rez = queryA.filter(user.tg_id == chat_id).first()
                rez.lastans = datetime.utcnow()
                db.session.commit()
            elif params['text']=='привести пример':
                x=dct[chat_id].pos
                y=random.randint(0,100)
                params['text']=eng_words[x]['examples'][y%len(eng_words[x]['examples'])]
                requests.post(url=url+'/sendMessage',data=params)
            else :
                print('Пришло {word}.'.format(word=params['text']))
                rez =queryA.filter(user.tg_id==chat_id).first()
                rez.lastans=datetime.utcnow()
                db.session.commit()
                if params['text']==dct[chat_id].Cword:
                    dct[chat_id].cor+=1
                    dt=datetime.utcnow()
                    data={"id":chat_id,"word":dct[chat_id].Cword,"dt":datetime.utcnow()}
                    rezL=queryB.filter(learning.user_id==chat_id,learning.word==dct[chat_id].Cword ).first()   # находим слово ++
                    rezL.cnt+=1
                    rw=queryB.filter(learning.user_id==chat_id,learning.word==dct[chat_id].Cword ).update({'cnt':rezL.cnt})
                    params['text']='Правильно {cor} раз(а)'.format(cor=rezL.cnt)

                else:
                    params['text']='Неправильно.Правильный ответ {word}.'.format(word=dct[chat_id].Cword)
                requests.post(url=url+'/sendMessage',data=params)
                dct[chat_id].rnd+=1
                if dct[chat_id].rnd==rc:
                    params['text']='Результат : правильно - {cor}, неправильно - {unc}.'.format(cor=dct[chat_id].cor,unc=rc-dct[chat_id].cor)
                    dct[chat_id].rnd=0
                    dct[chat_id].cor=0
                    reply={'keyboard':[[{'text':'Давай начнем!'}],[{'text':'Нет!'}]],'resize_keyboard':True}
                    reply=json.dumps(reply)
                    params['reply_markup']=reply
                    requests.post(url=url+'/sendMessage',data=params)
                else:
                    GRound(chat_id,params)
        try:
            db.session.commit()
        except:
            pass
        return Response(status=200)
    else:
        return Response(status=400)

@app.route('/init')
def ind():

    return ''

@app.route('/')
def index():
    return 'ИВТ-41-16 Петров Д.С. <br> Бот для заучивания'





