import io
import json
import requests

from PIL import Image

# Read personal access token from outside of source control
with open("C:/Users/cmbruns/biospud_arcgis_api_key.txt") as fh:
    access_token = fh.read().strip()
# print(access_token)

# Choose base map type
# https://developers.arcgis.com/documentation/mapping-apis-and-services/maps/services/basemap-layer-service/
basemap_style = "ArcGIS:Imagery"
basemap_type = "style"  # Mapbox style json
url = f"https://basemaps-api.arcgis.com/arcgis/rest/services/styles/" \
      f"{basemap_style}?type={basemap_type}&token={access_token}"

# Fetch raster tile url
r = requests.get(url=url)
j = r.json()
# print(json.dumps(j, indent=2))
raster_tile_url = None
sources = j["sources"]
for source, content in sources.items():
    if content["type"] == "raster":
        raster_tile_url = content["tiles"][0]
        break
print(raster_tile_url)

# Fetch root tile
x = y = z = 0
tile_url = raster_tile_url.format(x=x, y=y, z=z)
print(tile_url)
response = requests.get(url=tile_url)
print(response)

img = Image.open(io.BytesIO(response.content))
print(img)
img.show()
