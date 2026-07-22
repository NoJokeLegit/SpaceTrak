from sgp4.api import Satrec, jday
import datetime, math

# A real ISS (ZARYA) TLE snapshot (NORAD 25544)
l1 = "1 25544U 98067A   24193.51782528  .00016717  00000-0  30074-3 0  9993"
l2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49514467 10000"
sat = Satrec.twoline2rv(l1, l2)

def ecef_to_latlonalt(r, gmst):
    x,y,z = r
    # rotate ECI->ECEF by GMST
    xe =  x*math.cos(gmst)+y*math.sin(gmst)
    ye = -x*math.sin(gmst)+y*math.cos(gmst)
    ze = z
    lon = math.degrees(math.atan2(ye,xe))
    hyp = math.hypot(xe,ye)
    lat = math.degrees(math.atan2(ze,hyp))
    alt = math.sqrt(xe*xe+ye*ye+ze*ze)-6378.137
    return lat,lon,alt

print("Propagating ISS from ONE snapshot at 3 different times:\n")
for mins in [0, 30, 90]:
    t = datetime.datetime(2024,7,11,12,0,0)+datetime.timedelta(minutes=mins)
    jd,fr = jday(t.year,t.month,t.day,t.hour,t.minute,t.second)
    e,r,v = sat.sgp4(jd,fr)
    gmst = (280.46061837+360.98564736629*(jd+fr-2451545.0))%360
    lat,lon,alt = ecef_to_latlonalt(r, math.radians(gmst))
    spd = math.sqrt(sum(c*c for c in v))
    print(f"  +{mins:>3} min | lat {lat:7.2f}  lon {lon:8.2f}  alt {alt:6.1f} km  speed {spd:.2f} km/s")
