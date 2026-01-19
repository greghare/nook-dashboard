# nook-dashboard

This repository contains the files necessary for creating a simple web-based dashboard, optimized for a Nook Simple Touch E-Ink display. 

![IMG_20230414_151345255](https://user-images.githubusercontent.com/6226804/232252282-4e1c71d5-0b2c-4bdc-b487-c571b0f45cde.jpg)

## Requirements
- Nook Simple Touch E-Ink tablet (rooted to access Android, with Electric Sign app installed: https://play.google.com/store/apps/details?id=com.sugoi.electricsign)
  - Note: You can run this without a Nook. It has just been optimized for an 800x600 pixel E-Ink display. 
- Linux system such as a Raspberry Pi or Ubuntu system capable of running Python 3. I run this directly on my Ubuntu Home Assistant server. 
- Some basic knowledge of Python programming

## Installation and Setup
### 1. Clone the repository
Note: The application expects to be installed in /opt/nook-dashboard
``` 
$ cd /opt
$ git clone https://github.com/greghare/nook-dashboard.git
$ pip install requirements.txt
```
### 2. Install the service
``` 
$ cd /opt/nook-dashboard
$ sudo cp nook-dashboard.service /etc/systemd/system/nook-dashboard.service
$ sudo systemctl daemon-reload
```
### 3. Configure the application
``` 
$ cd /opt/nook-dashboard
$ cp app.json.example app.json
```
Open app.json in your favorite text editor, and configure the required items. At a minimum you must have
- ha_url: Complete path to your Home Assistant instance, including the port. Use your local Home Assistant IP address and port
- ha_access_token: To get an access token, follow the steps below
  1. Click your profile icon in the bottom left of the Home Assistant sidebar
  2. Click on "Security" at the top
  3. At the bottom of the page, under "Long-lived access tokens" click on "Create token"
  4. Name the token, and then click the copy button
  5. Replace <LONG_LIVED_ACCESS_TOKEN> with your new access token

Example configuration file
```
{
  "ha_url": "https://<HOME_ASSISTANT_IP>:8123",
  "ha_access_token": "<LONG_LIVED_ACCESS_TOKEN>",
  "timezone": "America/New_York",
  "calendar": "calendar.example_gmail_com",
  "weather": "weather.forecast_home",
  "featured_entity": {
    "id": "climate.downstairs",
    "attribute": "current_temperature",
    "icon": "information"
  },
  "entities": [
    { "id": "input_boolean.kitchen_motion", "property": "state", "icon": "motion-sensor" },
    { "id": "light.under_cabinet_1", "property": "state", "icon": "lightbulb" },
    { "id": "light.under_cabinet_2", "property": "state", "icon": "lightbulb" },
    { "id": "sensor.pi_hole_ads_blocked_today", "property": "state", "icon": "lightbulb" },
    { "id": "sun.sun", "property": "state", "icon": "weather-sunny" }
  ],
  "display": {
    "show_todo": true,
    "show_today_events": true,
    "show_tomorrow_events": true,    
    "show_weather": true,
    "show_featured_entity": true,
    "show_entity_table": true
  }
}
```

### 4. Start the Service
```
$ sudo service nook-dashboard start
```

## Usage

### 1. Load the main page

In a browser go to: http://<ip_address_of_host>:8888
You should see the following:

![landing](https://user-images.githubusercontent.com/6226804/198862147-ae8838c8-700b-4944-81e9-5b84c0f1ad76.png)

If you click on "Dashboard" you should get this. If you don't see this screen, and instead see a 500 Internal Server error, it's probably because the server.py code is trying to load a Home Assistant entity which you don't have setup. If this is the case, ensure you have all of the same entities, or delete any sensors you don't have. 

<img width="790" height="592" alt="image" src="https://github.com/user-attachments/assets/9cd12298-400f-46c7-8afe-20229aad7673" />

And if you click on To Do Manager you'll see something like this:

<img width="790" height="592" alt="image" src="https://github.com/user-attachments/assets/3ab367f3-c91a-46df-ae8e-ea03aba5b8d1" />

You can bookmark http://<ip_address_of_host>:8888/todo on your phone to easily add new items within your home network. Eventually I'd like to switch this to use the Todoist integration from Home Assistant. If anyone feels ambitious and wants to jump on that, feel free to submit a pull request!

Clicking a checkbox next to an item will remove it from the to do list

## How it Works Under the Hood
When you run the app, a local SQLite database (todolist.db) is created. This database will store your to do list items.
The weather, tide, sensor states, and calendar information, is queried from Home Assistant. You can edit the calendar which it pulls from in the config file. The other sensors/weather information currently has to be edited in the server.py file. Additional items will be added to the config file eventually.

** Disclaimer: This code could use some work. There's really not much error handling, and I'm sure some of it could be simplified a bit. I threw this together in a couple of days, so if you want to make updates or improvements, feel free to put in a pull request and we can improve it together
