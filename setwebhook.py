import requests

TOKEN = '1059696616:AAGcWDOvkpG2OFabcnFv9VZklF1Lj5ximxc'
API_URL = 'https://api.telegram.org/bot1059696616:AAGcWDOvkpG2OFabcnFv9VZklF1Lj5ximxc'
#WEBHOOKURL='https://Kethinor.pythonanywhere.com/incoming'
WEBHOOKURL='https://Kethinor.pythonanywhere.com/incoming'
url=API_URL
params={'url':WEBHOOKURL}
requests.post(url=url+'/setWebhook',data=params)