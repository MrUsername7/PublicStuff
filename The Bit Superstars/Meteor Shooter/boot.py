import network, time
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print('Connected:',str(wlan.isconnected()))
from Bit import begin, display
begin()
try:
    with open('wifi.txt', 'r') as f:
        ssid = f.readline().strip()
        pswd = f.readline().strip()
    if not wlan.isconnected():
        wlan.connect(ssid, pswd)
        time.sleep(5)
        display.text(str(wlan.ifconfig()),0,0,65535)
        display.commit()
        time.sleep(2.5)
except Exception as e:
    display.text(repr(e),0,0,65535)
    display.commit()
    time.sleep(2.5)
if wlan.isconnected():
    display.fill(0)
    display.text('webrepl 1234',0,0,65535)
    display.commit()
    time.sleep(2.5)
