import requests
import os
import re
from datetime import datetime



API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    raise SystemExit("Missing Google Maps API key. Set GOOGLE_MAPS_API_KEY in GitHub secrets.")

# Route details
ORIGIN = "Am Neuwirtshaus 4, 63457 Hanau"
DESTINATION = "Mergenthalerallee 3-5, 65760 Eschborn"

# API endpoint
url = "https://routes.googleapis.com/directions/v2:computeRoutes"

# Headers
headers = {
    'Content-Type': 'application/json',
    'X-Goog-Api-Key': API_KEY,
    'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.staticDuration,routes.legs,routes.description,routes.polyline'
}

# Request body
body = {
    "origin": {"address": ORIGIN},
    "destination": {"address": DESTINATION},
    "travelMode": "DRIVE",
    "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
    "computeAlternativeRoutes": True,
    "routeModifiers": {
        "avoidTolls": False,
        "avoidHighways": False,
        "avoidFerries": False
    },
    "languageCode": "de-DE",
    "units": "METRIC",
    "requestedReferenceRoutes": ["FUEL_EFFICIENT"]  # Fügt alternative Route hinzu
}

# Make the request
response = requests.post(url, json=body, headers=headers)

# Check response
if response.status_code == 200:
    data = response.json()
    
    if 'routes' in data and len(data['routes']) > 0:
        # Aktuelle lokale Zeit
        now = datetime.now()
        day = now.strftime("%Y-%m-%d")
        time =now.strftime("%H:%M:%S")
        
        # Loop through all routes
        for idx, route in enumerate(data['routes'], 1):
            #print(f"\nROUTE {idx}:")
            #print("-" * 80)

            resultstring = ''
            
            # Extract major roads from the route
            major_roads = set()
            if 'legs' in route:
                for leg in route['legs']:
                    if 'steps' in leg:
                        for step in leg['steps']:
                            # Look for navigation instructions that mention road names
                            if 'navigationInstruction' in step:
                                instruction = step['navigationInstruction'].get('instructions', '')
                                # Extract road names (they often contain keywords like "Hwy", "Rd", "St", "Motorway", etc.)
                                if 'Autobahn' in instruction or re.search(r'\bA\d{1,3}\b', instruction):
                                    major_roads.add(instruction)
            
            # if major_roads:
                #print(f"Route via: {', '.join(list(major_roads)[:99])}")  # Show first 3 roads
            
            # Fallback to manual calculation if localized values not available
            # Get duration (format: "1234s")
            duration_str = route.get('duration', '0s')
            duration_seconds = int(duration_str.rstrip('s'))
            duration_minutes = duration_seconds / 60
            
            # Get distance (in meters)
            distance_meters = route.get('distanceMeters', 0)
            distance_km = distance_meters / 1000
            
            # print(f"Duration: {duration_minutes:.1f} minutes ({duration_seconds} seconds)")
            # print(f"Distance: {distance_km:.1f} km")

            resultstring = (f"{day};{time};{distance_km:.1f};{duration_minutes:.1f}")

            
            
            # If you want traffic-aware duration (staticDuration is without traffic)
            if 'staticDuration' in route:
                static_duration = int(route['staticDuration'].rstrip('s'))
                static_minutes = static_duration / 60
                delay = duration_seconds - static_duration
                # print(f"Duration without traffic: {static_minutes:.1f} minutes")
                # print(f"Traffic delay: {delay} seconds ({delay/60:.1f} minutes)")
                
                resultstring += f";{static_minutes:.1f}"
                resultstring += f";{delay/60:.1f}"


            print(resultstring)
            # print("-" * 80)
    else:
        print("No routes found")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
