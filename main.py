import hashlib
import sqlite3
import time
import schedule
from datetime import datetime
import requests

from dotenv import dotenv_values

config=dotenv_values("weblopi.env")
user_key=config["user_key"]
token_group=config["token_key"]
time_refresh=int(config["time_refresh"])



db = sqlite3.connect("website.db")
db.execute("create table if not exists website (id integer primary key,name text,"
           "hash text,status text,mssg text,change int null,inserted text)")

def get_change():
    k=datetime.now()
    return k.strftime("updated %d/%m/%Y %H:%M:%S")

def check_webs():

    data=list(db.execute("select * from website where status in ('no','f')"))
    for i in data:
        while True:
            try:
                headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
                r = requests.get(i[1], headers=headers)
                break
            except:
                time.sleep(3)

        data = r.content
        k = hashlib.sha256(str(data).encode('utf-8')).hexdigest()
        if k!=i[2]:

            while True:
                try:
                    message= i[1] + f" updated"
                    if i[3]=="f":
                        message= i[1] + f" updated no : {int(i[-2])+1} times since {i[-1].rstrip('inserted ')}"
                    r = requests.post("https://api.pushover.net/1/messages.json", data={
                        "token": token_group,
                        "user": user_key,
                        "message": message,
                        "url": i[1]
                    }, )
                    break
                except:
                    time.sleep(3)
            ko=list(db.execute("select status from website where name = ?",(i[1],)))[0][0]
            if ko=="f":
                reinserted=list(db.execute("select change,inserted from website where name=?",(i[1],)))[0]
                change_no=reinserted[0]+1
                date_inserted=reinserted[1]
                db.execute("delete from website where name=?", (i[1],))
                db.execute("insert into website values (NULL,?,?,?,?,?,?)", (i[1], k, "f",get_change(),change_no,date_inserted))

            else:
                db.execute("update website set status='yes' where id=?",(i[0],))
            db.commit()


schedule.every(time_refresh).seconds.do(check_webs)
while True:
    schedule.run_pending()
    time.sleep(1)
