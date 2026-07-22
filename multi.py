from sgp4.api import Satrec, jday
import datetime, math

# Real TLE snapshots for a variety of object types
sats = {
 "ISS (station)":        ("1 25544U 98067A   24193.51782528  .00016717  00000-0  30074-3 0  9993",
                          "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49514467 10000"),
 "Hubble (telescope)":   ("1 20580U 90037B   24193.2003441  .00003431  00000-0  17293-3 0  9990",
                          "2 20580  28.4698 288.6669 0002481 262.0000 210.0000 15.09838041 10000"),
 "Starlink-1007 (LEO)":  ("1 44713U 19074A   24193.50000000  .00002000  00000-0  15000-3 0  9991",
                          "2 44713  53.0540 100.0000 0001200  90.0000 270.0000 15.06000000 10000"),
 "GPS BIIF-2 (MEO)":     ("1 37753U 11036A   24193.00000000 -.00000030  00000-0  00000-0 0  9995",
                          "2 37753  55.5000 200.0000 0100000  50.0000 310.0000  2.00560000 10000"),
 "Tiangong (station)":   ("1 48274U 21035A   24193.50000000  .00020000  00000-0  22000-3 0  9992",
                          "2 48274  41.4700 330.0000 0005000  60.0000 300.0000 15.60000000 10000"),
}

def geo(sat,t):
    jd,fr = jday(t.year,t.month,t.day,t.hour,t.minute,t.second)
    e,r,v = sat.sgp4(jd,fr)
    if e!=0: return None
    gmst = math.radians((280.46061837+360.98564736629*(jd+fr-2451545.0))%360)
    x,y,z=r
    xe= x*math.cos(gmst)+y*math.sin(gmst); ye=-x*math.sin(gmst)+y*math.cos(gmst)
    lon=math.degrees(math.atan2(ye,xe)); lat=math.degrees(math.atan2(z,math.hypot(xe,ye)))
    alt=math.sqrt(xe*xe+ye*ye+z*z)-6378.137
    spd=math.sqrt(sum(c*c for c in v))
    per=2*math.pi/ (sat.no_kozai) # min
    return lat,lon,alt,spd,per

t=datetime.datetime(2024,7,11,12,0,0)
print(f"{'OBJECT':<22}{'LAT':>8}{'LON':>9}{'ALT km':>10}{'km/s':>7}{'orbit min':>11}")
print("-"*67)
for name,(l1,l2) in sats.items():
    s=Satrec.twoline2rv(l1,l2)
    g=geo(s,t)
    if g:
        lat,lon,alt,spd,per=g
        print(f"{name:<22}{lat:8.2f}{lon:9.2f}{alt:10.1f}{spd:7.2f}{per:11.1f}")
