#!/bin/python3

import asyncio

import tornado.web
from tornado.options import define, options
import datetime
import time
import sqlite3
import requests
import json
import pprint as pprint
import os

# Home Assistant Configuration
# HA_URL should be the URL of your Home Assistant instance, including the port. If you are using 
#        Nabu Casa or another custom domain, you may need to set this to your local IP address, including the port
# HA_ACCESS_TOKEN should be your long-lived access token (create one by clicking your username in the 
#                 bottom left and selecting "create token" at the bottom)
HA_URL = "<YOUR_HOME_ASSISTANT_URL>"
HA_ACCESS_TOKEN = "<YOUR_ACCESS_TOKEN>"
HA_API = HA_URL + "/api"

define("port", default=8888, help="run on the given port", type=int)
        
con = sqlite3.connect("todolist.db")
cur = con.cursor()

requests.packages.urllib3.disable_warnings()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('> <a href="/dashboard" style="font-size: 25px">Dashboard</a><br>\
                    > <a href="/todo" style="font-size: 25px">To Do Manager</a>')

class DeleteToDo(tornado.web.RequestHandler):

    def post(self):

        # Delete todo item
        id = self.get_argument("id")
        cur.execute("DELETE FROM todo WHERE ID = ?", (id,))
        con.commit()        
        
        print("Item " + id + " was deleted")
        
class ToDo(tornado.web.RequestHandler):
    def get(self):
        
        # Get to do list
        res = cur.execute("SELECT ID, title, state FROM todo")
        items = res.fetchall()                

        self.render("todo.html", title="To Do", items=items)

    def post(self):
        
        # Insert todo item        
        title = self.get_argument("title")
        cur.execute("INSERT INTO todo VALUES (NULL, ?, false)", (title,))
        con.commit()        
        
        print("New todo item posted")
        self.redirect('/todo')

class Dashboard(tornado.web.RequestHandler):
    def get(self):

        # Get to do list items
        res = cur.execute("SELECT ID, title, state FROM todo")
        items = res.fetchall()        

        # Configure headers for Home Assistant API
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + HA_ACCESS_TOKEN
        }

        # Get weather                
        response = requests.get(HA_API + "/states/weather.home", headers=headers, verify=False)
        weather = response.json()["attributes"]    
        weather_state = response.json()["state"]
        
        # Get front door image
        # # response = requests.get(HA_API + "/states/camera.front_door", headers=headers, verify=False)
        # front_door = HA_URL + response.json()["attributes"]["entity_picture"]

        # response = requests.get(front_door, headers=headers, verify=False)
        # if response.status_code:
        #     fp = open('static/img/front_door.png', 'wb')
        #     fp.write(response.content)
        #     fp.close()

        self.render("index.html", title="Nook Dashboard", items=items, weather_state=weather_state, weather=weather)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/dashboard", Dashboard),
            (r"/todo", ToDo),
            (r"/deletetodo", DeleteToDo),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

async def main():

    # Create the todo list database
    try:
        cur.execute("CREATE TABLE IF NOT EXISTS todo(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, title, state)")
    except Exception as ex:
        print("Exception occured: " + ex)

    # Start the web server
    app = tornado.httpserver.HTTPServer(Application())
    app.listen(options.port)
    await asyncio.Event().wait()    

if __name__ == "__main__":
    asyncio.run(main())
