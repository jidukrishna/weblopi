import hashlib
import time
from datetime import datetime

import requests
import uvicorn
from fastapi import FastAPI
import sqlite3



db = sqlite3.connect("website.db")
db.execute("create table if not exists website (id integer primary key,name text,"
           "hash text,status text,mssg text,change int null,inserted text)")
db.commit()
db.close()
app = FastAPI()

def get_change():
    k=datetime.now()
    return k.strftime("inserted %d/%m/%Y %H:%M:%S")

@app.get("/")
def root():
    return "poyi valla panikum poda"


@app.get("/add_website", summary="use f to check the webiste forever otherwise use no")
def add_website(url: str, type: str = "no"):
    type = type.lower()
    if type not in ("no", "f"):
        return "not valid"

    def add_website(url):
        c = 0
        while True:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
                r = requests.get(url, headers=headers)
                break
            except:
                c += 1
                if c == 4:
                    return "invalid url ig"
                time.sleep(1)
        global data
        data = r.content
        k = hashlib.sha256(str(r.content).encode('utf-8')).hexdigest()
        val= 0 if type=="f" else "NULL"
        with sqlite3.connect("website.db") as db:
            c = db.cursor()
            c.execute("delete from website where name=?", (url,))
            c.execute("insert into website values (NULL,?,?,?,?,?,?)", (url, k, type,"no change",val,get_change()))

    add_website(url)
    return "added  " + str(data)


@app.get("/status")
def status(type: str = "all"):
    with sqlite3.connect("website.db") as db:
        if type.lower() == "all":
            q = "select id,name,status,inserted,mssg,change from website"
        elif type.lower() == "yes":
            q = "select id,name,status,mssg,change from website where status='yes'"
        elif type.lower() == "no":
            q = "select id,name,status,mssg,change from website where status='no'"
        elif type.lower() == "f":
            q = "select id,name,status,mssg,change from website where status='f'"
        else:
            return "invalid type"

        data = db.execute(q).fetchall()
        data.insert(0, ("id", "name"))
    return data


@app.get("/clear", summary="use (yes,no,f,all_clear,id,use the url if needed)")
def clear(type: str):
    type=type.strip()
    with sqlite3.connect("website.db") as db:
        if type.lower() == "all_clear":
            q = "delete from website"
        elif type.lower() == "yes":
            q = "delete from website where status='yes'"
        elif type.lower() == "no":
            q = "delete from website where status='no'"
        elif type.lower() == "f":
            q = "delete from website where status='f'"
        elif type.isdigit():
            q = "delete from website where id ="+type
        else:
            k = db.execute("select count(*) from website where name = ?", (type,))
            k = list(k)[0][0]
            print(k)
            if k == 0:
                return "invalid type"
            else:
                q = f"delete from website where name='{type}'"

        cur = db.cursor()
        cur.execute(q)
        data = cur.rowcount
    return f"deleted {data} no of data"


uvicorn.run(app, port=6969, host="0.0.0.0")
