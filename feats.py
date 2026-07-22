from sgp4.api import Satrec, jday
import datetime, math

iss=Satrec.twoline2rv("1 25544U 98067A   24193.51782528  .00016717  00000-0  30074-3 0  9993",
                      "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49514467 10000")
hst=Satrec.twoline2rv("1 20580U 90037B   24193.2003441  .00003431  00000-0  17293-3 0  9990",
                      "2 20580  28.4698 288.6669 0002481 262.0000 210.0000 15.09838041 10000")

def pos(sat,t):
    jd,fr=jday(t.year,t.month,t.day,t.hour,t.minute,t.second)
    e,r,v=sat.sgp4(jd,fr); return r

def track(sat,t0,mins,step):
    jd,fr=jday(t0.year,t0.month,t0.day,t0.hour,t0.minute,t0.second)
    pts=[]
    for m in range(0,mins,step):
        tt=t0+datetime.timedelta(minutes=m)
        j2,f2=jday(tt.year,tt.month,tt.day,tt.hour,tt.minute,tt.second)
        e,r,v=sat.sgp4(j2,f2)
        g=math.radians((280.46061837+360.98564736629*(j2+f2-2451545.0))%360)
        x,y,z=r; xe=x*math.cos(g)+y*math.sin(g); ye=-x*math.sin(g)+y*math.cos(g)
        pts.append((round(math.degrees(math.atan2(z,math.hypot(xe,ye))),1),
                    round(math.degrees(math.atan2(ye,xe)),1)))
    return pts

t0=datetime.datetime(2024,7,11,12,0,0)
tr=track(iss,t0,95,10)
print("1) ISS orbital-path line (one full orbit, lat/lon nodes to draw):")
print("  ", tr,"\n")

print("2) Live ISS<->Hubble separation (proximity/'conjunction' check):")
mind=1e9;mint=None
for m in range(0,180):
    tt=t0+datetime.timedelta(minutes=m)
    a=pos(iss,tt); b=pos(hst,tt)
    d=math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
    if d<mind: mind=d;mint=m
print(f"   closest approach over next 3h: {mind:,.0f} km at +{mint} min")
