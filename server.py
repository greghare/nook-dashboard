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

config = configparser.ConfigParser()  
config.read("/opt/nook-dashboard/app.conf");

HA_URL = config["home_assistant"]["url"]
HA_ACCESS_TOKEN = config["home_assistant"]["access_token"]
HA_API = HA_URL + "/api"

# Configure headers for Home Assistant API
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + HA_ACCESS_TOKEN
}

CALENDAR = config["home_assistant"]["calendar"]

define("port", default=8888, help="run on the given port", type=int)
        
con = sqlite3.connect("/opt/nook-dashboard/todolist.db")
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

    # Return the high, and low temperatures from a list of temps
    def get_high_low(self, temps):
        return [max(temps), min(temps)]

    def get_weather_icon(self, condition):

        # The path is relative to the static_url
        icon_path = {
            "clear-night": "img/icons/weather-night.png",
            "cloudy": "img/icons/weather-cloudy.png",
            "fog": "img/icons/weather-fog.png",
            "hail": "img/icons/weather-hail.png",
            "lightning": "img/icons/weather-lightning.png",
            "lightning-rainy": "img/icons/weather-lightning-rainy.png",
            "partlycloudy": "img/icons/weather-partly-cloudy.png",
            "pouring": "img/icons/weather-pouring.png",
            "rainy": "img/icons/weather-rainy.png",
            "snowy": "img/icons/weather-snowy.pngclear",
            "snowy-rainy": "img/icons/weather-snowy-rainy.png",
            "sunny": "img/icons/weather-sunny.png",
            "windy": "img/icons/weather-windy.png",
            "windy-variant": "img/icons/weather-windy-variant.png",
            "exceptional": "img/icons/weather-sunny-alert.png"
        }

        return icon_path[condition]

    def get(self):

        ##############################
        #  TO DO LIST
        ##############################

        # Get to do list items
        res = cur.execute("SELECT ID, title, state FROM todo")
        items = res.fetchall()        

        ##############################
        #  TODAYS EVENTS (FROM CALENDAR)
        ##############################

        # Get calendar
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.date.today() - timedelta(days = 1)).strftime("%Y-%m-%d")
        start = today + "T00:00:00.000Z"
        end = today + "T23:59:59.999Z"

        response = requests.get(HA_API + "/calendars/" + CALENDAR + "?start="+start+"&end="+end, headers=headers, verify=False)
        calendar = response.json()  

        ##############################
        #  WEATHER
        ##############################

        # Get weather                
        response = requests.get(HA_API + "/states/weather.openweathermap", headers=headers, verify=False)
        weather = response.json()["attributes"]    
        weather_state = response.json()["state"]
        weather_icon = self.get_weather_icon(weather_state)

        # Build 5 day forecast of high/lows
        forecast = weather["forecast"]

        five_day = {}
        prev_date = datetime.datetime.now().strftime("%Y-%m-%d")
        prev_day = datetime.datetime.now().strftime("%a")
        temps = []
        index = 0

        for f in forecast:

            # Get current date
            today = datetime.datetime.now().strftime("%Y-%m-%d")

            # Get forecast datetime
            dt = datetime.datetime.strptime(f["datetime"], '%Y-%m-%dT%H:%M:%S%z').astimezone(timezone("America/New_York"))
            forecast_date = dt.strftime("%Y-%m-%d")
            forecast_day = dt.strftime("%a")

            # If new day, reset temps
            if forecast_date != prev_date:
                if len(temps) > 0:
                    high_low = self.get_high_low(temps)
                    five_day.update({index: {"dow": prev_day, "high": high_low[0], "low": high_low[1]}})
                    index += 1
                temps = []            

            # If not today, add temperature to temps list
            # if forecast_date != today:
            temps.append(f["temperature"])

            prev_date = forecast_date
            prev_day = forecast_day

        # Handle last date
        high_low = self.get_high_low(temps)
        five_day.update({index: {"dow": prev_day, "high": high_low[0], "low": high_low[1]}})
        index += 1

        ##############################
        #  TIDE CONDITIONS
        ##############################

        # Get tides                
        response = requests.get(HA_API + "/states/sensor.tide", headers=headers, verify=False)
        tide = response.json()["attributes"]
        format = "%Y-%m-%dT%H:%M"
        low_tide_time = datetime.datetime.strptime(tide["low_tide_time"], format)
        high_tide_time = datetime.datetime.strptime(tide["high_tide_time"], format)
        low_tide_height = round(tide["low_tide_height"], 1)
        high_tide_height = round(tide["high_tide_height"], 1)

        ltt = low_tide_time.strftime("%A @ %-I:%M %p")
        htt = high_tide_time.strftime("%A @ %-I:%M %p")

        ##############################
        #  SENSORS/DEVICE STATES
        ##############################

        # Sensor state dictionary
        sensors = []

        # Get motion status                
        response = requests.get(HA_API + "/states/input_boolean.kitchen_motion", headers=headers, verify=False)
        kitchen_motion = response.json()["state"]
        sensors.append({ "name": "Kitchen Motion Sensor", "state": kitchen_motion, "icon": "motion-sensor"})

        # Get patio light status                
        response = requests.get(HA_API + "/states/switch.patio_lights", headers=headers, verify=False)
        patio_light = response.json()["state"]    
        sensors.append({ "name": "Patio Light", "state": patio_light, "icon": "string-lights"})

        # Get door lock status                
        response = requests.get(HA_API + "/states/binary_sensor.front_door_lock", headers=headers, verify=False)
        front_door = response.json()["state"]         
        sensors.append({ "name": "Front Door Lock", "state": front_door, "icon": "lock" })

        response = requests.get(HA_API + "/states/binary_sensor.back_door_lock", headers=headers, verify=False)
        back_door = response.json()["state"]               
        sensors.append({ "name": "Back Door Lock", "state": back_door, "icon": "lock" })

        response = requests.get(HA_API + "/states/climate.living_room", headers=headers, verify=False)
        thermostat = str(response.json()["attributes"]["current_temperature"])
        sensors.append({ "name": "Living Room Thermostat", "state": thermostat, "icon": "thermostat" })

        ##############################
        #  RENDER DASHBOARD
        ##############################

        self.render(
            "dashboard.html", 
            title="Nook Dashboard", 
            items=items, 
            calendar=calendar, 
            weather_state=weather_state, 
            weather=weather, 
            weather_icon=weather_icon, 
            five_day=five_day, 
            htt=htt, 
            ltt=ltt, 
            hth=high_tide_height, 
            lth=low_tide_height, 
            sensors=sensors
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
