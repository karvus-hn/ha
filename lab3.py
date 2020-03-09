from flask import Flask,request,Response,json
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
from sqlalchemy.orm import scoped_session, sessionmaker

TOKEN = '1059696616:AAGcWDOvkpG2OFabcnFv9VZklF1Lj5ximxc'
API_URL = 'https://api.telegram.org/bot1059696616:AAGcWDOvkpG2OFabcnFv9VZklF1Lj5ximxc'
url=API_URL

engine = create_engine("postgres://zueltcpozckyiz:dcc13eeb6e9969ebb6842885ffc4d5d51b10da9c60801e26d939b77e91577b5f@ec2-46-137-156-205.eu-west-1.compute.amazonaws.com:5432/d67s20vrum3nv0", echo = True)

app = Flask(__name__)
app.config.from_pyfile('config.py')
#db = scoped_session(sessionmaker(bind=engine))
ccount=5

with open('english_words.json') as f:
    eng_words = json.load(f)

random.seed(2)

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

def GRound(chat_id,params):
    global end_words
    global dct
    global ccount
    queryA=db.session.query(user)
    queryB=db.session.query(learning)
    x = random.randint(0,len(eng_words))
    r = random.choices(range(0,len(eng_words)),k=3)
    rt=99
    try:
        while rt>=ccount:
            x = random.randint(0,len(eng_words))
            rezC=queryB.filter(learning.user_id==chat_id,learning.word==eng_words[x]['word'], ).first()  # узнаем количество
            if rezC==None:
                tempL = learning(user_id=chat_id, word=eng_words[x]['word'],lastans=datetime.utcnow(),cnt=0)
                db.session.add(tempL)
                #db.session.flush()
                rezC=tempL
			db.session.commit()
            rt=rezC.cnt
            if (rt<=ccount):
                break
    except:
        pass
    while x in r:
        r = random.choices(range(0, len(eng_words)), k=3)
    r.append(x)
    r.sort()
    b=[dict(text=eng_words[a]['translation']) for a in r]
    b.append({'text':'привести пример'})
    reply={'keyboard':[[b[0],b[1]],[b[2],b[3]],[b[4]]],'resize_keyboard':True}
    params['text']='Как переводится с английского слово "{word}"?'.format(word=eng_words[x]['word'])
    reply=json.dumps(reply)
    params['reply_markup']=reply
    requests.post(url=url+'/sendMessage',data=params)
    dct[chat_id].Cword=eng_words[x]['translation']
    dct[chat_id].pos=x
    data={"id":chat_id,"word":dct[chat_id].Cword,"dt":datetime.utcnow()}
    #rezC=queryB.filter(learning.user_id==chat_id,learning.word==dct[chat_id].Cword ).first()  # вставляем слово
    #if rezC.cnt==None:
    #    tempL = learning(user_id=chat_id, word=dct[chat_id].Cword,lastans=datetime.utcnow(),cnt=0)
    #    db.session.add(tempL)
    #    db.session.commit()
    return Response(status=200)


@app.route('/incoming', methods=['POST'])
def webhook():
    if request.method == 'POST':
        queryA=db.session.query(user)
        queryB=db.session.query(learning)
        update = request.get_json()
        if "message" in update:
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
                GRound(chat_id,params)
            elif params['text']=='привести пример':
                x=dct[chat_id].pos
                y=random.randint(0,100)
                params['text']=eng_words[x]['examples'][y%len(eng_words[x]['examples'])]
                requests.post(url=url+'/sendMessage',data=params)
            else :
                if params['text']==dct[chat_id].Cword:
                    dct[chat_id].cor+=1
                    dt=datetime.utcnow()
                    data={"id":chat_id,"word":dct[chat_id].Cword,"dt":datetime.utcnow()}
                    rezL=queryB.filter(learning.user_id==chat_id,learning.word==dct[chat_id].Cword ).first()   # находим слово ++
                    rezL.cnt+=1
                    db.session.commit()
                    params['text']='Правильно {cor} раз(а)'.format(cor=rezL.cnt)

                else:
                    params['text']='Неправильно.Правильный ответ {word}.'.format(word=dct[chat_id].Cword)
                rez =queryA.filter(user.tg_id==chat_id).first()
                rez.lastans=datetime.utcnow()
                db.session.commit()
                requests.post(url=url+'/sendMessage',data=params)
                dct[chat_id].rnd+=1
                if dct[chat_id].rnd==10:
                    params['text']='Результат : правильно - {cor}, неправильно - {unc}.'.format(cor=dct[chat_id].cor,unc=10-dct[chat_id].cor)
                    dct[chat_id].rnd=0
                    dct[chat_id].cor=0
                    reply={'keyboard':[[{'text':'Давай начнем!'}],[{'text':'Нет!'}]],'resize_keyboard':True}
                    reply=json.dumps(reply)
                    params['reply_markup']=reply
                    requests.post(url=url+'/sendMessage',data=params)
                else:
                    GRound(chat_id,params)
        return Response(status=200)
    else:
        return Response(status=400)

@app.route('/init')
def ind():

    return ''

@app.route('/')
def index():
    return Response(status=200)




