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
$ pip install tornado
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
$ cp example.conf app.conf
```
Open app.conf in your favorite text editor, and set your Home Assistant URL, Access Token, and Calendar entity to use.
Open server.py and edit/remove any of the sensor states to configure it as you like.

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

![image](https://user-images.githubusercontent.com/6226804/232252874-a0903732-f9f3-40bb-8c92-3dbd8757b225.png)

And if you click on To Do Manager you'll see something like this:

![image](https://user-images.githubusercontent.com/6226804/232253106-7e14bec3-4308-4081-b23a-073b32acc6f5.png)

You can bookmark http://<ip_address_of_host>:8888/todo on your phone to easily add new items within your home network. Eventually I'd like to switch this to use the Todoist integration from Home Assistant. If anyone feels ambitious and wants to jump on that, feel free to submit a pull request!

Clicking a checkbox next to an item will remove it from the to do list

## How it Works Under the Hood
When you run the app, a local SQLite database (todolist.db) is created. This database will store your to do list items.
The weather, tide, sensor states, and calendar information, is queried from Home Assistant. You can edit the calendar which it pulls from in the config file. The other sensors/weather information currently has to be edited in the server.py file. Additional items will be added to the config file eventually.

** Disclaimer: This code could use some work. There's really not much error handling, and I'm sure some of it could be simplified a bit. I threw this together in a couple of days, so if you want to make updates or improvements, feel free to put in a pull request and we can improve it together
