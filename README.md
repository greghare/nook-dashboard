# nook-dashboard

This repository contains the files necessary for creating a simple web-based To Do List dashboard for a Nook E-Ink display. 

** Disclaimer: This code could use some work. There's really not much error handling, and I'm sure some of it could be simplified a bit. I threw this together in a couple of days, so if you want to make updates or improvements, feel free to put in a pull request and we can improve it together

![dashboard](https://user-images.githubusercontent.com/6226804/198899087-2bd523be-e4f0-4dbd-aa77-48b873de05dd.png)

### There are 4 files and 1 directory
1. nook.py - This contains the main logic for the todo list application, as well as the web server code
2. templates/index.html - This is the main dashboard
3. templates/todo.html - This is the to do list controller
4. static/css/style.css - Contains all application styles
5. static/img/ - This is used to store image files locally, when querying cameras or other image based results from HA.

## Configuration
### 1. First edit nook.py to enter your Home Assistant URL and your Home Assistant Access Token

#### > HA_URL 
This should be the URL of your Home Assistant instance, including the port. If you are using Nabu Casa or another custom domain, you may need to set this to your local IP address, including the port

#### > HA_ACCESS_TOKEN 
This should be your long-lived access token. You can create one by clicking your username in the bottom left of Home Assistant and selecting "create token" at the very bottom.

## Usage
### 1. Install Python Tornado
` pip install tornado `

### 2. Run the server
You can start the application like this

` ./nook.py `

or 

` python3 nook.py `

To run it in the background on a Linux system, use this instead

` nohup ./nook.py & `

### 3. Load the main page

In a browser go to: http://<ip_address_of_host>:8888
You should see the following:

![landing](https://user-images.githubusercontent.com/6226804/198862147-ae8838c8-700b-4944-81e9-5b84c0f1ad76.png)

If you click on "Dashboard" you should get this

![dashboard](https://user-images.githubusercontent.com/6226804/198899087-2bd523be-e4f0-4dbd-aa77-48b873de05dd.png)

And if you click on To Do Manager you'll see this

![todo](https://user-images.githubusercontent.com/6226804/198899129-f62fb8d1-6cd5-467e-af05-7c4db5e37a7a.png)

Clicking on the checkboxes next to an item will remove it from the to do list

## How it Works
When you run the app, a local SQLite database (todolist.db) is created. This database will store your to do list items.
The weather information is queried from a Home Assistant entity named "weather.home". You can edit the Python code to change what this queries


