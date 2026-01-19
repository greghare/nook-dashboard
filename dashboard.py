import requests
import datetime
from datetime import timedelta
from pytz import timezone

class Dashboard:
    
    def __init__(self, ha_url, ha_access_token, timezone, calendar, weather, featured_entity, entities):
        self.ha_url = ha_url
        self.ha_access_token = ha_access_token
        self.timezone = timezone
        self.calendar = calendar
        self.weather = weather
        self.featured_entity = featured_entity
        self.entities = entities
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.ha_access_token
        }

        
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
    
    def get_today_events(self):
        
        today = datetime.datetime.now().astimezone(timezone(self.timezone)).strftime("%Y-%m-%d")
        start = today + "T00:00:00"
        end = today + "T23:59:59"

        response = requests.get(self.ha_url + "/api/calendars/" + self.calendar + "?start="+start+"&end="+end, headers=self.headers, verify=False)
        events = response.json()
        return events
    
    def get_tomorrow_events(self):
        
        tomorrow = (datetime.datetime.now().astimezone(timezone(self.timezone)) + timedelta(days=1)).strftime("%Y-%m-%d")
        start = tomorrow + "T00:00:00"
        end = tomorrow + "T23:59:59"
        response = requests.get(self.ha_url + "/api/calendars/" + self.calendar + "?start="+start+"&end="+end, headers=self.headers, verify=False)
        events = response.json()
        return events
    
    def get_weather(self):
                
        # Get weather                
        response = requests.get(self.ha_url + "/api/states/" + self.weather, headers=self.headers, verify=False)
                    
        if response.status_code == 200:
            weather = response.json()["attributes"]
            weather_temp = weather["temperature"]
            weather_state = response.json()["state"]            
            weather_icon = self.get_weather_icon(weather_state)
         
            weather_data = {
                "temperature": weather["temperature"],
                "icon": weather_icon
            }
            
        else:
            weather_data = {
                "state": "unavailable",
                "icon": "img/icons/weather-unknown.png"
            }
        
        return weather_data
        
    def get_weather_forecast(self):

        payload = {
            "entity_id": self.weather,
            "type": "daily"
        }
        
        # Get weather forecast
        response = requests.post(
            f"{self.ha_url}/api/services/weather/get_forecasts?return_response", 
            headers=self.headers, 
            json=payload, 
            verify=False
        )
        
        if response.status_code == 200:
        
            forecast_data = response.json()["service_response"][self.weather]["forecast"]                   
                        
            five_day_forecast = []
 
            for f in forecast_data:
                                
                # Get current date
                today = datetime.datetime.now().astimezone(timezone(self.timezone)).strftime("%Y-%m-%d")

                # Get forecast datetime
                dt = datetime.datetime.strptime(f["datetime"], '%Y-%m-%dT%H:%M:%S%z').astimezone(timezone(self.timezone))
                forecast_date = dt.strftime("%Y-%m-%d")
                forecast_day = dt.strftime("%a")
                
                five_day_forecast.append({
                    "dow": forecast_day,
                    "high": f["temperature"],
                    "low": f["templow"]
                })
                
            five_day_forecast = five_day_forecast[:5]  # Limit to 5 days     
            
            return five_day_forecast

        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
        
    def get_featured_entity(self):
        
        entity_id = self.featured_entity["id"]
        icon = self.featured_entity["icon"]
        
        # Query the Home Assistant API for this entity
        r = requests.get(f"{self.ha_url}/api/states/{entity_id}", headers=self.headers, verify=False)

        if r.status_code == 200:
            data = r.json()
            featured_entity = {
                "id": entity_id,
                "icon": icon,
                "property": data["state"] if not self.featured_entity.get("attribute") else data["attributes"][self.featured_entity.get("attribute")],
                "name": data.get("attributes", {}).get("friendly_name", entity_id)
            }
        else:
            # fallback if entity not found
            featured_entity = {
                "id": entity_id,
                "icon": icon,
                "state": "unavailable",
                "name": entity_id
            }
                    
        return featured_entity       
    
    def get_entities(self):
        
        entities = []
        
        if self.entities:
            
            for entity in self.entities:
                entity_id = entity["id"]
                
                # Query the Home Assistant API for this entity
                r = requests.get(f"{self.ha_url}/api/states/{entity_id}", headers=self.headers, verify=False)

                if r.status_code == 200:
                    data = r.json()
                    entities.append({
                        "id": entity_id,
                        "icon": entity["icon"],
                        "property": data[entity["property"]],
                        "name": data.get("attributes", {}).get("friendly_name", entity_id)
                    })
                else:
                    # fallback if entity not found
                    entities.append({
                        "id": entity_id,
                        "icon": entity["icon"],
                        "property": "unavailable",
                        "name": entity_id
                    })
                    
        return entities
