# Example to work up basemap tiles

from math import floor, log, radians, tan
import gv.basemap

p_wgs = (133, -25)  # center point in Australia
p_mrc = radians(p_wgs[0]), log(tan(radians(45) + radians(p_wgs[1] / 2)))
# Flip Y and convert to root texture coordinates
p_img = (radians(180) + p_mrc[0]) / radians(360), (radians(180) - p_mrc[1]) / radians(360)
print(p_img)

rez = 2  # TODO: determine resolution from zoom and center location
n = 2 ** rez
x, y = [floor(n * x) for x in p_img]
print(x, y)
# Australia is on tile 3, 2, 2

basemap = gv.basemap.Basemap()
tile = basemap.fetch_tile(x, y, rez)
print(tile)
tile.image.show()
