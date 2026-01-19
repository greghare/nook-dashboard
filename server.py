#!/bin/python3

# Author: Greg Hare
# https://github.com/greghare
# Created: 10/26/2022

import asyncio
import tornado.web
from tornado.options import define, options
from datetime import datetime
import datetime
from datetime import timedelta
from pytz import timezone
import time
import sqlite3
import requests
import json
import re
import pprint as pprint
import os
import configparser
from todo_client import TodoClient
from dashboard import Dashboard

# Load configuration from app.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "app.json")) as f:
    config = json.load(f)

HA_URL = config["ha_url"]
HA_ACCESS_TOKEN = config["ha_access_token"]

TIMEZONE = config["timezone"]
CALENDAR = config["calendar"]
WEATHER = config["weather"]
FEATURED_ENTITY = config["featured_entity"]
ENTITIES_CONFIG = config["entities"]

requests.packages.urllib3.disable_warnings()

todo_client = TodoClient()

dashboard = Dashboard(
    ha_url=HA_URL,
    ha_access_token=HA_ACCESS_TOKEN,
    timezone=TIMEZONE,
    calendar=CALENDAR,
    weather=WEATHER,
    featured_entity=FEATURED_ENTITY,
    entities=ENTITIES_CONFIG
)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('> <a href="/dashboard" style="font-size: 25px">Dashboard</a><br>\
                    > <a href="/todo" style="font-size: 25px">To Do Manager</a>')

class DeleteToDo(tornado.web.RequestHandler):

    def post(self):

        try:
            todo_id = self.get_argument("id")
            todo_client.delete(todo_id)
            print(f"Item {todo_id} was deleted")
        except Exception as ex:
            print(f"Error deleting todo: {ex}")
            self.set_status(500)
            self.write({"error": "Failed to delete todo item."})
            return
        self.redirect('/todo')
        
class ToDo(tornado.web.RequestHandler):
    def get(self):
        
        try:
            items = todo_client.get_all()
        except Exception as ex:
            print(f"Error fetching todo list: {ex}")
            items = []

        self.render("todo.html", title="To Do List", items=items)
        
    def post(self):
        
        try:
            title = self.get_argument("title")
            todo_client.add(title)
            print("New todo item posted")
        except Exception as ex:
            print(f"Error adding todo: {ex}")
            self.set_status(500)
            self.write({"error": "Failed to add todo item."})
            return
        
        self.redirect('/todo')


class Dashboard(tornado.web.RequestHandler):

    def panel_visibility(self, display: dict) -> tuple[bool, bool]:
        left_enabled = any((
            display.get("show_todo"),
            display.get("show_today_events"),
            display.get("show_tomorrow_events"),
        ))

        right_enabled = any((
            display.get("show_weather"),
            display.get("show_featured_entity"),
            display.get("show_entity_table"),
        ))

        return left_enabled, right_enabled

    def get(self):

        ##############################
        #  RENDER DASHBOARD
        ##############################
        
        todo_list = None
        today_events = None
        tomorrow_events = None
        weather_cur_temp = None
        weather_cur_icon = None
        five_day = None
        featured_entity = None
        entities = None
        
        print(self.panel_visibility(config["display"]))
        
        if config["display"]["show_todo"]:
            todo_list = todo_client.get_all()
            
        if config["display"]["show_today_events"]:
            today_events = dashboard.get_today_events()
            
        if config["display"]["show_tomorrow_events"]:
            tomorrow_events = dashboard.get_tomorrow_events()
            
        if config["display"]["show_weather"]:
            
            # Get current weather
            weather = dashboard.get_weather()
            weather_cur_temp = weather["temperature"]
            weather_cur_icon = weather["icon"]
            
            # Get 5 day forecast
            five_day = dashboard.get_weather_forecast()    
            
        if config["display"]["show_featured_entity"]:
            featured_entity = dashboard.get_featured_entity()       
            
        if config["display"]["show_entity_table"]:
            entities = dashboard.get_entities()
        
        self.render(
            "dashboard.html", 
            title="Nook Dashboard", 
            left_panel = self.panel_visibility(config["display"])[0],
            right_panel = self.panel_visibility(config["display"])[1],
            display=config["display"],
            todo_list=todo_list, 
            today_events=today_events, 
            tomorrow_events=tomorrow_events,
            weather_cur_temp=weather_cur_temp, 
            weather_cur_icon=weather_cur_icon, 
            five_day=five_day,
            featured_entity=featured_entity,
            entities=entities    
        )

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/dashboard", Dashboard),
            (r"/todo", ToDo),
            (r"/deletetodo", DeleteToDo)
       ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)

async def main():

    # Parse command-line options (e.g., --port)
    define("port", default=8888, help="Run on the specified port", type=int)    

    tornado.options.parse_command_line()    

    # Start the web server
    app = tornado.httpserver.HTTPServer(Application())
    app.listen(options.port)
    await asyncio.Event().wait()    

if __name__ == "__main__":
    asyncio.run(main())
