import aiohttp
from typing import Dict, Any


async def get_weather(location: str) -> Dict[str, Any]:
	try:
		async with aiohttp.ClientSession() as session:
			url = f"http://api.openweathermap.org/data/2.5/weather"
			params = {
				"q": location,
				"appid": "YOUR_OPENWEATHER_API_KEY",
				"units": "imperial"
			}

			async with session.get(url, params=params) as response:
				if response.status == 200:
					data = await response.json()

					return {
						"success": True,
						"data": {
							"location": data["name"],
							"temperature": data["main"]["temp"],
							"feels_like": data["main"]["feels_like"],
							"humidity": data["main"]["humidity"],
							"conditions": data["weather"][0]["description"],
							"wind_speed": data["wind"]["speed"]
						}
					}
				else:
					return {
						"success": False,
						"error": f"Weather API returned status {response.status}"
					}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}
