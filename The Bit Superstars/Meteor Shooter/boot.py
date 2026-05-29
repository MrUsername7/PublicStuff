
import network, time
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print('Connected:',str(wlan.isconnected()))
try:
    with open('wifi.txt', 'r') as f:
        ssid = f.readline().strip()
        pswd = f.readline().strip()
    if not wlan.isconnected():
        wlan.connect(ssid, pswd)
        time.sleep(5)
except Exception as e:
    from Bit import begin, display
    begin()
    display.text(repr(e), 64-len(repr(e))*4,60,65535)
    display.commit()
    import time
    time.sleep(5)
