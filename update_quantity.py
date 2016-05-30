#!/usr/bin/env python
# coding=utf-8
import requests, json
import hashlib 
import time
import datetime
tid=[]
tid2=[]
num=0
def gettime():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
def change_to_one(app_id,app_secret):
    m2 = hashlib.md5()      
    method='kdt.trades.sold.get'
    t=gettime()
    secret=app_secret+"app_id"+app_id+"format"+"json"+"method"+method+"sign_method"+"md5"+"status"+"TRADE_BUYER_SIGNED"+"timestamp"+t+"v1.0"+app_secret
    m2.update(secret)
    sign=m2.hexdigest()
    url = "https://open.koudaitong.com/api/entry?sign="+sign+"&timestamp="+t+"&v=1.0&app_id="+app_id+"&method="+method+"&sign_method=md5"+"&format=json"+"&status=TRADE_BUYER_SIGNED"
    r = requests.post(url)
    r.encoding='utf-8'
    #print r.json()
    #for x in r.json()['response']['trades']:
    #    print x['orders']
    for trade in r.json()['response']['trades']:
        if trade['tid'] in tid:
            break
        tid.append(trade['tid'])
        for order in trade['orders']:
            num_iid=order['num_iid']
            sku_id=order['sku_id'] 
            method='kdt.item.sku.update'
            t=gettime()
            secret=app_secret+"app_id"+app_id+"format"+"json"+"method"+method+"num_iid"+num_iid+"quantity"+"1"+"sign_method"+"md5"+"sku_id"+sku_id+"timestamp"+t+"v1.0"+app_secret
            m2=hashlib.md5()
            m2.update(secret)
            sign=m2.hexdigest()
            url = "https://open.koudaitong.com/api/entry?sign="+sign+"&timestamp="+t+"&v=1.0&app_id="+app_id+"&method="+method+"&sign_method=md5"+"&format=json"+"&num_iid="+num_iid+"&quantity="+"1"+"&sku_id="+sku_id
            r=requests.post(url)
            r.encoding='utf-8'
            #print r.json()
def check(app_id,app_secret):       
    global num
    s=''
    m2=hashlib.md5()      
    method='kdt.trades.sold.get'
    t=gettime()
    secret=app_secret+"app_id"+app_id+"format"+"json"+"method"+method+"sign_method"+"md5"+"status"+"TRADE_BUYER_SIGNED"+"timestamp"+t+"v1.0"+app_secret
    m2.update(secret)
    sign=m2.hexdigest()
    url="https://open.koudaitong.com/api/entry?sign="+sign+"&timestamp="+t+"&v=1.0&app_id="+app_id+"&method="+method+"&sign_method=md5"+"&format=json"+"&status=TRADE_BUYER_SIGNED"
    r=requests.post(url)
    r.encoding='utf-8'
    diary=open('diary.txt','a')
    for trade in r.json()['response']['trades']:
        t=time.strptime(trade['sign_time'],'%Y-%m-%d %H:%M:%S')
        d=datetime.datetime(*t[:6])
        interval=(datetime.datetime.now()-d).seconds
        if (trade['tid'] in tid2) & (interval>60):
            break
        tid2.append(trade['tid'])
        num+=1
        s+=u'序号:'+str(num)+u'\t交易号tid:'+trade['tid']+u'\t买家签收时间sign_time:'+trade['sign_time']+'\n'
        for order in trade['orders']:
            m2=hashlib.md5()      
            method='kdt.item.get'
            t=gettime()
            num_iid=order['num_iid']
            secret=app_secret+"app_id"+app_id+"format"+"json"+"method"+method+"num_iid"+num_iid+"sign_method"+"md5"+"timestamp"+t+"v1.0"+app_secret
            m2.update(secret)
            sign=m2.hexdigest()
            url="https://open.koudaitong.com/api/entry?sign="+sign+"&timestamp="+t+"&v=1.0&app_id="+app_id+"&method="+method+"&sign_method=md5"+"&format=json"+"&num_iid="+num_iid
            r2=requests.post(url)
            r2.encoding='utf-8'
            quantity=r2.json()['response']['item']['skus'][0]['quantity']
            s+=u'\t订单号oid:'+str(order['oid'])+u'\t商品编号num_iid:'+order['num_iid']+u'\t商品名称:'+order['title']+u'\t库存quantity:'+r2.json()['response']['item']['skus'][0]['quantity']
            if quantity=='1':
                s+=u'\t更新库存结果:成功!\n'
            elif interval<=60:
                s+=u'\t买家刚签收,还没来得及更新库存哦~\n'
            else:
                s+=u'\t更新库存结果:失败!\n'
        s+='\n\n\n'
    #print s
    try:
        diary.write(s.encode('utf-8'))
    finally:
        diary.close()



if __name__=='__main__':
    while True:
        app_id='28d0381f755d973346'
        app_secret='dc33fbab8ef36c8a4d4b602ac64fff3e'    
        change_to_one(app_id,app_secret)
        check(app_id,app_secret)
        time.sleep(40)
