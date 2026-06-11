"""
menus:
0: game
1: mainmenu
2: shop
3: helps
4: about
5: mainmenu2 (settings)
6: langselect
7: networkMenu
8: keyboard
9: leaderboard #reserved
10: minigame
11: listNetworks
12: langSelectOnStartup
"""

import network, gc
gc.collect()
wlan = network.WLAN(network.STA_IF)
gc.collect()
wlan.active(True)
from Bit import *
from framebuf import *
from random import randrange
import math, random, array, time
begin()
try:
    _ = LEDs.C
    emulated = False
except NameError:
    emulated = True
from sprite_data import *
sprite_coin = FrameBuffer(coinSprite, 11, 11, RGB565)
sprite_asteroid = FrameBuffer(asteroidSprite, 27, 25, RGB565)
sprite_cup = FrameBuffer(cupSprite, 40, 40, RGB565)
sprite_ship = FrameBuffer(shipSprite, 32, 48, RGB565)
sprite_life2times = FrameBuffer(life2timesSprite, 31, 10, RGB565)
sprite_life = FrameBuffer(lifeSprite, 11, 10, RGB565)
sprite_alien = FrameBuffer(alienSprite, 22, 29, RGB565)
sprite_qr = FrameBuffer(qrSprite, 128, 128, MONO_HLSB)

sprite_hr = FrameBuffer(hrSprite, 15, 8, RGB565)
sprite_en = FrameBuffer(enSprite, 15, 8, RGB565)
sprite_de = FrameBuffer(deSprite, 15, 8, RGB565)

class LVK:
    selectX = 0
    selectY = 0
    inputt = ''
    shifted = False
    keyboardLowercaseText = [
      ["1","2","3","4","5","6","7","8","9","0","-","="],
      ["q","w","e","r","t","y","u","i","o","p","[","]","#"],
      ["a","s","d","f","g","h","j","k","l",";","\'"],
      ["\\","z","x","c","v","b","n","m",",",".","/"]
    ]
    keyboardUppercaseText = [
      ["!",'"',"£","$","%","^","&","*","(",")","_","+"],
      ["Q","W","E","R","T","Y","U","I","O","P","{","}","~"],
      ["A","S","D","F","G","H","J","K","L",":","@"],
      ["|","Z","X","C","V","B","N","M","<",">","?"]
    ]

    #Colors
    textSelectedClr = 0 #33808 #31
    textBgClr = 16904
    textClr = 65535

    @classmethod
    def drawKeyboard(cls):
        display.fill(16)
        for i in range(0,4):
            for j in range(0,13):
                try:
                    _ = cls.keyboardLowercaseText[i][j]
                    if cls.selectX == j and cls.selectY == i:
                        display.rect(j*8+offsetX, i*8, 8, 8, cls.textSelectedClr, True)
                    else:
                        display.rect(j*8+offsetX, i*8, 8, 8, cls.textBgClr, True)
                    if cls.shifted:
                        display.text(cls.keyboardUppercaseText[i][j], j*8+offsetX, i*8, cls.textClr)
                    else:
                        display.text(cls.keyboardLowercaseText[i][j], j*8+offsetX, i*8, cls.textClr)
                except IndexError:
                    pass
        if cls.selectX == 0 and cls.selectY == 4:
            display.rect(0+offsetX, 32, 24, 8, cls.textSelectedClr, True)
        else:
            display.rect(0+offsetX, 32, 24, 8, cls.textBgClr, True)
        display.text('ESC', 0+offsetX, 32, cls.textClr)
        if cls.selectX == 0 and cls.selectY == 5:
            display.rect(0+offsetX, 40, 40, 8, cls.textSelectedClr, True)
        else:
            display.rect(0+offsetX, 40, 40, 8, cls.textBgClr, True)
        display.text('ENTER', 0+offsetX, 40, cls.textClr)
        if cls.selectX == 1 and cls.selectY == 4:
            display.rect(24+offsetX, 32, 40, 8, cls.textSelectedClr, True)
        else:
            display.rect(24+offsetX, 32, 40, 8, cls.textBgClr, True)
        display.text('SPACE', 24+offsetX, 32, cls.textClr)
        if len(cls.inputt) > 16:
            display.text(cls.inputt[-16:], 0+offsetX, 120, cls.textClr)
        else:
            display.text(cls.inputt, 0+offsetX, 120, cls.textClr)
        display.text("A: Select", 0+offsetX, 48, cls.textClr)
        display.text("B: Backspace", 0+offsetX, 56, cls.textClr)
        display.text("C: Shift Toggle", 0+offsetX, 64, cls.textClr)
        if emulated: display.text(lang[3], 0+offsetX, 112, 65535)
        display.commit()
    @classmethod
    def getMod(cls):
        if cls.selectY == 0:
            return 12
        elif cls.selectY == 1:
            return 13
        elif cls.selectY == 2 or cls.selectY == 3:
            return 11
        elif cls.selectY == 4:
            return 2
        else:
            return 1
    @classmethod
    def rightPress(cls):
        cls.selectX = (cls.selectX+1)%cls.getMod()
        cls.drawKeyboard()
    @classmethod
    def leftPress(cls):
        cls.selectX = (cls.selectX-1)%cls.getMod()
        cls.drawKeyboard()
    @classmethod
    def upPress(cls):
        cls.selectY = (cls.selectY-1)%6
        cls.selectX = max(0, min(cls.getMod()-1, cls.selectX))
        cls.drawKeyboard()
    @classmethod
    def downPress(cls):
        cls.selectY = (cls.selectY+1)%6
        cls.selectX = max(0, min(cls.getMod()-1, cls.selectX))
        cls.drawKeyboard()
    @classmethod
    def select(cls):
        try:
            if cls.shifted:
                cls.inputt = str(cls.inputt)+cls.keyboardUppercaseText[cls.selectY][cls.selectX]
            else:
                cls.inputt = str(cls.inputt)+cls.keyboardLowercaseText[cls.selectY][cls.selectX]
            cls.drawKeyboard()
            display.commit()
        except IndexError:
            if cls.selectX == 1 and cls.selectY == 4:
                cls.inputt = str(cls.inputt)+" "
                cls.drawKeyboard()
                display.commit()
            else:
                cls.end()
    @classmethod
    def init(cls):
        global menu
        cls.inputt = ""
        cls.selectX, cls.selectY = 0,0
        menu = 8
        cls.drawKeyboard()
    @classmethod
    def end(cls):
        global ssid, pswd, menu, select
        if cls.selectY == 5:
            if select == 0:
                ssid = cls.inputt
            elif select == 1:
                pswd = cls.inputt
        menu = 7
        networkMenu()
        scroll()
        display.commit()
        networkMenu()
        scroll()
        display.commit()
    @classmethod
    def shiftLock(cls):
        cls.shifted = not cls.shifted
        cls.drawKeyboard()
    @classmethod
    def backspace(cls):
        cls.inputt = cls.inputt[:-1]
        cls.drawKeyboard()

if wlan.isconnected():
  print('Connection OK')

def connected():
  if wlan.isconnected():
    return ' (OK)'
  else: return ''

lang_en = [
"for Bit",
"Textures:",
"Programming:",
"EMULATED",
"(B) Back",
"Play",
"Shop",
"Settings",
"About",
"Sound: ",
"Confirm",
"Change",
"selection",
'Stronger',
'Laser',
'More',
'Meteors',
'Coins',
"< Money and",
"progress",
"multiplier",
"Help page ",
"(A) Continue...",
"(B) Skip",
'< "More Coins"',
"upgrade",
"Network"+connected(),
"A: Shoot",
"Menu: Exit",
"< and >: Move",
"(A) Let's play!",
"Faster",
"Translations:",
"Language",
"(!!!)",
"SSID",
"Password",
"Connect",
"Leaderboard",
'Save',
'Erase data',
'Reset',
'Refresh'
]

lang_hr = [
"za Bit",
"Teksture:",
"Programiranje:",
"EMULIRANO",
"(B) Nazad",
"Igraj",
"Trgovina",
"Postavke",
"O",
"Zvuk: ",
"Potvrdi",
"Promjeni",
"odabir",
'Jaci',
'Laser',
'Vise',
'Meteora',
'Novaca',
"< Novci i",
"multiplikator",
"napretka",
"Pomocna str. ",
"(A) Nastavak...",
"(B) Preskoci",
'< "Vise Novaca"',
"nadogradnja",
"Mreza"+connected(),
"A: Pucaj",
"Menu: Izlaz",
"< and >: Pomici",
"(A) Ajmo igrati!",
"Brzi",
"Prijevodi:",
"Jezik",
"(!!!)",
"SSID",
"Zaporka",
"Spoji se",
"Rang-lista",
'Spremi',
'Obrisi podatke',
'Ponovno pokreni',
'Osvježi'
]

lang_de = [
'fuer Bit',
'Texturen:',
'Programmierung:',
'EMULIERT',
'(B) Zurueck',
'Spielen',
'Shop',
'Einstellungen',
'Ueber',
'Klang: ',
'Bestaetigen',
'Aendern',
'Auswahl',
'Staerker',
'Laser',
'Mehr',
'Meteore',
'Muenzen',
'< Geld und',
'Fortschritt',
'Multiplikator',
'Hilfeseite',
'(A) Weiter...',
'(B) ueberspringen',
'< "Mehr Muenzen"',
'Upgrade',
'Netzwerk'+connected(),
'A: Schiessen',
'Menue: Beenden',
'< und >: Bewegen',
"(A) Los geht's!",
'Schneller',
'Uebersetzungen:',
'Sprache',
'(!!!)',
'SSID',
'Passwort',
'Verbinden',
'Bestenliste',
'Speichern',
'Daten loeschen',
'Zuruecksetzen',
'Aktualisieren'
]

lang_es = []

lang_fr = []

startValue = None
targetValue = None
step = None
select = None
i = 0
x = None
menu = None
money = 0
item = None
laser = 0
item2 = None
meteors = 0
coinsUpg = 0
value = 0
temp = None
shipPos = 1
shipX = -4
shipXchngBy = 52 #tu mijenjaj brzinu
meteorAY = -40
mAH = 3 #meteorAHealth
meteorBY = -40
mBH = 3
meteorCY = -40
mCH = 3
meteorKill = 63
meteorNoKill = 115
meteorsShotInSession = 0
fVA = 1 #fall value a,b,c
fVB = 2
fVC = 3
inCooldown = False
multi = 1
flicker = False
cupsList = [0,0,0,0,1,1,1,2] #  0 su vanzemaljci, 1 su +1 život, a 2 su +2 života
tone = True
code = 5
version = "1.3.2 'GAMMA'"
lives = 1
livesTick = 1
totalDistance = 0
lang = None
fastl = 0
selectMeteor = [0, 1, 0]
ssid = None
pswd = None
running = True
networks = None
offsetX = 0

def save():
  with open('data.txt', 'w') as f:
    global money, laser, meteors, coinsUpg, tone, totalDistance, lang, fastl, ssid, pswd
    f.write(str(money)+'\n')
    f.write(str(laser)+'\n')
    f.write(str(meteors)+'\n')
    f.write(str(coinsUpg)+'\n')
    f.write(str(tone)+'\n')
    f.write(str(totalDistance)+'\n')
    if lang == lang_en:
      f.write('en\n')
    elif lang == lang_hr:
      f.write('hr\n')
    elif lang == lang_de:
      f.write('de\n')
    elif lang == lang_es:
      f.write('es\n')
    elif lang == lang_fr:
      f.write('fr\n')
    f.write(str(fastl)+'\n')

def load():
  try:
    with open('data.txt', 'r') as f:
      global money, laser, meteors, coinsUpg, tone, totalDistance, lang, fastl
      money = float(f.readline().strip())
      laser = int(f.readline().strip())
      meteors = int(f.readline().strip())
      coinsUpg = int(f.readline().strip())
      tone = f.readline().strip() == 'True'
      totalDistance = int(f.readline().strip())
      lang = f.readline().strip()
      if lang == "en":
        lang = lang_en[:]
      elif lang == "hr":
        lang = lang_hr[:]
      elif lang == "de":
        lang = lang_de[:]
      elif lang == "es":
        lang = lang_es[:]
      elif lang == "fr":
        lang = lang_fr[:]
      fastl = int(f.readline().strip())
  except:
    pass
  try:
    with open('wifi.txt', 'r') as f:
      global ssid, pswd
      ssid = f.readline().strip()
      pswd = f.readline().strip()
  except:
    pass

def langSelectOnStartup():
  global startValue, targetValue, step, mod, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  display.fill(0)
  display.text('SETUP '+lang[33], 64-len('SETUP '+lang[33])*4+offsetX, 0, 65535)
  display.text("English", 128-len("English")*8+offsetX, (0-select+4)*15, 65535)
  display.text("Hrvatski", 128-len("Hrvatski")*8+offsetX, (0-select+5)*15, 65535)
  display.text("Deutsch "+lang[34], 128-len("Deutsch "+lang[34])*8+offsetX, (0-select+6)*15, 65535)
  display.blit(sprite_en, 8+offsetX, (0-select+4)*15, 0)
  display.blit(sprite_hr, 8+offsetX, (0-select+5)*15, 0)
  display.blit(sprite_de, 8+offsetX, (0-select+6)*15, 65535)

def startup():
    display.fill(1234)
    display.blit(sprite_hr, 113, 0, 0)
    display.blit(sprite_en, 113, 8, 0)
    display.blit(sprite_de, 113, 16, 65535)
    for i in range(113,128,2):
        display.pixel(i, 24, 0)
    display.commit()
    time.sleep(1)
    global lang, menu
    load()
    if lang == None:
        lang = lang_en[:]
        menu = 12
        langSelectOnStartup()
        display.text('>', 0+offsetX, 60, 65535)
        display.commit()
    else:
        save()
        menu = 1
        display.fill(0)
        t1 = 'The Bit'
        t2 = 'Superstars'
        t3 = 'present...'
        display.text(t1, 64-len(t1)*4+offsetX, 52, 65535)
        display.text(t2, 64-len(t2)*4+offsetX, 60, 65535)
        display.text(t3, 64-len(t3)*4+offsetX, 68, 65535)
        display.commit()
        time.sleep(1.25)
        mainmenu()
        display.text(str(">"), 0+offsetX, 60, 65535)
        display.commit()

def shuffle(array):
    global lives, select, livesTick
    if array == cupsList:
        select = 0
        if lives > 1:
            livesTick = 125
        lives -= 1
    for i in range(len(array) - 1, 0, -1):
        j = randrange(i + 1)
        array[i], array[j] = array[j], array[i]

def shuffleMeteors():
    global selectMeteor, meteorAY, meteorBY, meteorCY
    while True:
        shuffle(selectMeteor)
        if (((meteorAY <= -25 or meteorAY >= 128) or selectMeteor[0]) and
            ((meteorBY <= -25 or meteorBY >= 128) or selectMeteor[1]) and
            ((meteorCY <= -25 or meteorCY >= 128) or selectMeteor[2])):
            break

def about():
  global menu, select
  menu = 4
  select = 0
  display.fill(16)
  display.text("Meteor Shooter", 8+offsetX, 0, 65535)
  display.text(lang[0], 36+offsetX, 8, 65535)
  display.text(version, 0+offsetX, 20, 65535)
  display.text(lang[1], 0+offsetX, 28, 65535)
  display.text("Adrian", 8+offsetX, 36, 65535)
  display.text(lang[2], 0+offsetX, 54, 65535)
  display.text("Leon", 8+offsetX, 60, 65535)
  display.text(lang[32], 0+offsetX, 76, 65535)
  display.text("Leon", 8+offsetX, 84, 65535)
  if emulated: display.text(lang[3], 0+offsetX, 112, 65535)
  display.text(lang[4], 64-len(lang[4])*4+offsetX, 120, 65535)
  display.commit()

def mainmenu():
  global startValue, targetValue, step, mod, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  display.fill(16)
  display.text(lang[5], 64-len(lang[5])*4+offsetX, (0-select+4)*15, 65535)
  display.text(lang[6], 64-len(lang[6])*4+offsetX, (0-select+5)*15, 65535)
  display.text(lang[7], 64-len(lang[7])*4+offsetX, (0-select+6)*15, 65535)
  display.text(lang[8], 64-len(lang[8])*4+offsetX, (0-select+7)*15, 65535)
  display.text(lang[38], 64-len(lang[38])*4+offsetX, (0-select+8)*15, 65535)
  display.text('QR', 56+offsetX, (0-select+9)*15, 65535)
  display.rect(0+offsetX, 0, 128, 8, 16, 1)
  display.text("METEOR SHOOT>R", 8+offsetX, 0, 65535)
  if emulated: display.text(lang[3], 0+offsetX, 120, 65535)

def mainmenu2():
  global startValue, targetValue, step, mod, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value, tone, temp
  display.fill(16)
  temp = lang[9]+str(tone)
  display.text(temp,64-len(temp)*4+offsetX,(0-select+4)*15,65535)
  display.text(lang[33],64-len(lang[33])*4+offsetX,(0-select+5)*15,65535)
  display.text(lang[39],64-len(lang[39])*4+offsetX,(0-select+6)*15,65535)
  display.text(lang[40],64-len(lang[40])*4+offsetX,(0-select+7)*15,65535)
  display.text(lang[41],64-len(lang[41])*4+offsetX,(0-select+8)*15,65535)
  if not emulated: display.text(lang[26],64-len(lang[26])*4+offsetX,(0-select+9)*15,65535)
  display.rect(0+offsetX, 0, 128, 8, 16, 1)
  display.text(lang[7], 64-len(lang[7])*4+offsetX, 0, 65535)
  if emulated: display.text(lang[3], 0+offsetX, 120, 65535)

def networkMenu():
    #lang[35] je ssid i lang[36] je lozinka
    global menu, select
    display.fill(16)
    display.text(lang[35], 64-len(lang[35])*4+offsetX, (0-select+4)*15, 65535)
    display.text(lang[36], 64-len(lang[36])*4+offsetX, (0-select+5)*15, 65535)
    display.text(lang[37], 64-len(lang[37])*4+offsetX, (0-select+6)*15, 65535)
    display.rect(0+offsetX, 0, 128, 8, 16, 1)
    display.text(lang[26], 64-len(lang[26])*4+offsetX, 0, 65535)
    if emulated: display.text(lang[3], 0+offsetX, 120, 65535)

def scanNetworks():
    global networks, wlan
    display.fill(16)
    display.text('...', 52+offsetX, 60, 65535)
    display.commit()
    networks = wlan.scan()

def listNetworks():
    global networks, wlan
    display.fill(16)
    display.text(lang[35], 64-len(lang[35])*4+offsetX, 0, 65535)
    display.text(lang[42], 64-len(lang[42])*4+offsetX, (0-select+4)*15, 65535)
    for i in range(5,len(networks)+5):
        display.text(networks[i-5][0].decode(), 64-len(networks[i-5][0].decode())*4+offsetX, (0-select+i)*15, 65535)

def appropriateMenu():
  if menu == 1:
    mainmenu()
  elif menu == 5:
    mainmenu2()
  elif menu == 6:
    langSelect()
  elif menu == 7:
    networkMenu()
  elif menu == 11:
    listNetworks()
  elif menu == 12:
    langSelectOnStartup()

def scroll():
  global startValue, targetValue, step, mod, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  if menu == 1 or (menu >= 5 and menu <= 7) or (menu >= 11 and menu <= 12):
    appropriateMenu()
    display.text(">",0+offsetX,60,65535)
    display.commit()

def minigameSetup():
  global livesTick, lives
  shuffle(cupsList)
  if livesTick == 0 and lives == 0:
    minigame()

def drawgame():
  global shipX, meteorAY, meteorBY, meteorCY, money, coinsUpg, multi, lives, livesTick, shipPos
  display.fill(0)
  display.blit(sprite_ship, shipX+3+offsetX, 80, 0)
  display.blit(sprite_asteroid, 0+offsetX, int(meteorAY), 0)
  display.blit(sprite_asteroid, 52+offsetX, int(meteorBY), 0)
  display.blit(sprite_asteroid, 104+offsetX, int(meteorCY), 0)
  shipPos = ((shipX+4)/52)+1
  display.blit(sprite_coin, 0+offsetX, 0, 0)
  display.text(str(round(money)), 13+offsetX, 0, 65535)
  display.text(str(coinsUpg+1), 0+offsetX, 12, 65535)
  if multi > 1:
    display.text(str("x"), 13 + len(str(round(money)))*8+offsetX, 0, 65535)
    display.text(str(multi), 21 + len(str(round(money)))*8+offsetX, 0, 65535)
  display.blit(sprite_life, 0+offsetX, 31, 0)
  display.text(str(lives)+","+str(livesTick), 11+offsetX, 31, 65535)

def game():
  global totalDistance, livesTick, lives, shipX, meteorAY, meteorBY, meteorCY, shipPos, money, meteorKill, meteorNoKill, fVA, fVB, fVC, meteorsShotInSession, multi, menu
  totalDistance += 1
  drawgame()
  if meteorsShotInSession == 0:
    multi = 1
    fVC = 7/4
  elif meteorsShotInSession == 10:
    if fVC != 5/4:
      if tone: piezo.tone(500, 150)
      if tone: piezo.tone(1000, 150)
    fVC = 5/4
  elif meteorsShotInSession == 25:
    if fVA != 2:
      if tone: piezo.tone(500, 150)
      if tone: piezo.tone(1000, 150)
    fVA = 2
    fVB = 3
  elif meteorsShotInSession == 40:
    if fVC != 3/4:
      if tone: piezo.tone(500, 150)
      if tone: piezo.tone(1000, 150)
    fVC = 3/4
    multi = 5/4
  elif meteorsShotInSession == 65:
    if fVC != 3/5:
      if tone: piezo.tone(500, 150)
      if tone: piezo.tone(1000, 150)
    fVC = 3/5
    multi = 3/2
  elif meteorsShotInSession == 100:
    if fVC != 1:
      if tone: piezo.tone(1500, 150)
      if tone: piezo.tone(2000, 150)
    fVC = 1
    fVA = 5
    fVB = 7
    multi = 2
  if emulated: display.text(lang[3], 0+offsetX, 120, 65535)
  display.commit()
  if livesTick == 0:
    if shipPos == 1 and meteorNoKill > meteorAY > meteorKill:
      minigameSetup()
    elif shipPos == 2 and meteorNoKill > meteorBY > meteorKill:
      minigameSetup()
    elif shipPos == 3 and meteorNoKill > meteorCY > meteorKill:
      minigameSetup()
  if livesTick > 0:
    livesTick -= 1

def posBoxX():
    if select == 0 or select == 3 or select == 5:
        return(0)
    elif select == 1 or select == 6:
        return(43)
    else:
        return(86)

def posBoxY():
    global select
    if select <= 2:
        return(0)
    elif select == 3 or select == 4:
        return(43)
    else:
        return(86)

def minigame(aPressed=False): #nedovršeno
  global menu, select, lives, livesTick, cupsList
  menu = 10
  if not aPressed:
    display.fill(0)
    _cupPos = (
        (00, 00), (43, 00), (86, 00),
        (00, 43),           (86, 43),
        (00, 86), (43, 86), (86, 86)
    )
    for x, y in _cupPos:
        display.blit(sprite_cup, x+offsetX, y, 0)
    item = "A:"
    item2 = lang[10]
    item3 = "B:"
    item4 = lang[11]
    item5 = lang[12]
    display.text(item, 64-len(item)*4+offsetX, 48, 65535)
    display.text(item2, 64-len(item2)*4+offsetX, 56, 65535)
    display.text(item3, 64-len(item3)*4+offsetX, 64, 65535)
    display.text(item4, 64-len(item4)*4+offsetX, 72, 65535)
    display.text(item5, 64-len(item5)*4+offsetX, 80, 65535)
    display.rect(posBoxX()+offsetX, posBoxY(), 40, 40, 65535, 0)
    if emulated: display.text(lang[3], 0+offsetX, 120, 65535)
    display.commit()
  else:
    for i in range(44,14,-1):
      display.fill(0)
      display.blit(sprite_cup, 44+offsetX, i, 0)
      display.commit()
    item = cupsList[select]
    if item == 0:
      display.blit(sprite_alien, 53+offsetX, 50, 0)
    elif item == 1:
      display.blit(sprite_life, 59+offsetX, 50, 0)
    elif item == 2:
      display.blit(sprite_life2times, 49+offsetX, 50, 0)
    if emulated: display.text(lang[3], 0+offsetX, 120, 65535)
    display.commit()
    time.sleep(1)
    lives += item
    if lives == 0:
      menuButton()
    else:
      livesTick = 125
      menu = 0

def buymenu():
  global startValue, targetValue, step, mod, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  display.fill(16)
  display.blit(sprite_coin, 0+offsetX, 0, 0)
  display.text(str(money), 13+offsetX, 0, 65535)
  display.rect(36+offsetX, 36, 56, 56, 33808, 1)
  display.rect(32+offsetX, 32, 64, 64, 0, 1)
  display.rect(0+offsetX, 40, 16, 48, 0, 1)
  display.rect(112+offsetX, 40, 16, 48, 0, 1)
  if emulated: display.text(lang[3], 0+offsetX, 120, 65535)
  shopitem()

def buyscrollr(startValue, targetValue, step):
  global mod, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  i = startValue
  while i != targetValue:
    i = i - step 
    display.fill(16)
    display.blit(sprite_coin, 0+offsetX, 0, 0)
    display.text(str(money), 13+offsetX, 0, 65535)
    display.rect(40 + i+offsetX, 40, 48, 48, 0, 1)
    display.rect(-32 + i+offsetX, 40, 48, 48, 0, 1)
    display.rect(112 + i+offsetX, 40, 48, 48, 0, 1)
    display.rect(-72 + i+offsetX, 40, 16, 48, 0, 1)
    display.rect(184 + i+offsetX, 40, 48, 48, 0, 1)
    if emulated: display.text(lang[3], 0+offsetX, 120, 65535)
    display.commit()

def buymenu2(startValue, targetValue, step):
  global mod, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  i = startValue
  while i != targetValue:
    i = i - step
    display.fill(16)
    display.blit(sprite_coin, 0+offsetX, 0, 0)
    display.text(str(money), 13+offsetX, 0, 65535)
    display.rect(int(40-i/2+offsetX), int(40-i/2),48+i,48+i,0,1)
    display.rect(0+offsetX, 40, 16, 48, 0, 1)
    display.rect(112+offsetX, 40, 16, 48, 0, 1)
    if emulated: display.text(lang[3], 0+offsetX, 120, 65535)
    display.commit()

def shopitem():
  global startValue, targetValue, step, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value, temp, fastl
  display.blit(sprite_coin, 0+offsetX, 0, 0)
  display.text(str(money), 13+offsetX, 0, 65535)
  if select == 0:
    item = lang[13]
    item2 = lang[14]
    if laser == 0:
      value = 100
    elif laser == 1:
      value = 150
    elif laser == 2:
      value = 9999
  elif select == 1:
    item = lang[15]
    item2 = lang[16]
    if meteors == 0:
      value = 50
    elif meteors == 1:
      value = 75
    elif meteors == 2:
      value = 9999
  elif select == 2:
    item = lang[15]
    item2 = lang[17]
    if coinsUpg == 0:
      value = 25
    elif coinsUpg == 1:
      value = 50
    elif coinsUpg == 2:
      value = 75
    elif coinsUpg == 3:
      value = 100
    elif coinsUpg == 4:
      value = 150
    elif coinsUpg == 5:
      value = 9999
  elif select == 3:
      item = lang[31]
      item2 = lang[14]
      if fastl == 0:
        value = 250
      elif fastl == 1:
        value = 300
      elif fastl == 2:
        value = 9999
  else:
    item = 'ERR01'
  display.text(str(item), 64 - len(item) * 4+offsetX, 56, 65535)
  display.text(str(item2), 64 - len(item2) * 4+offsetX, 64, 65535)
  if value == 9999:
    temp = "MAX"
  else:
    temp = value
  display.text(str(temp), 64-len(str(temp)) * 4+offsetX, 96, 65535)
  if emulated: display.text(lang[3], 0+offsetX, 120, 65535)
  display.commit()

def helps():
  global menu, money, multi, coinsUpg, cooldown, item, item2, item3
  menu = 3
  display.fill(0)
  display.blit(sprite_coin, 0+offsetX, 0, 0)
  display.text(str(round(money)), 13+offsetX, 0, 65535)
  display.text(str("x"), 13 + len(str(round(money)))*8+offsetX, 0, 65535)
  display.text(str(multi), 21 + len(str(round(money)))*8+offsetX, 0, 65535)
  display.text(str(coinsUpg+1), 0+offsetX, 12, 65535)
  display.text(str(lives)+",0", 11+offsetX, 31, 65535)
  display.blit(sprite_life, 0+offsetX, 31, 0)
  if select == 0:
    display.text(lang[18], 40+offsetX, 0, 65535)
    display.text(lang[19], 40+offsetX, 8, 65535)
    display.text(lang[20], 40+offsetX, 16, 65535)
    item = lang[21]+"1/3"
    item2 = lang[22]
    item3 = lang[23]
  elif select == 1:
    display.text(lang[24], 10+offsetX, 12, 65535)
    display.text(lang[25], 26+offsetX, 18, 65535)
    item = lang[21]+"2/3"
  elif select == 2:
    display.text(lang[27], 0+offsetX, 40, 65535)
    display.text(lang[28], 0+offsetX, 48, 65535)
    display.text(lang[29], 0+offsetX, 56, 65535)
    item = lang[21]+"3/3"
    item2 = lang[30]
  display.text(str(item), 64 - len(item) * 4+offsetX, 104, 65535)
  display.text(str(item2), 64 - len(item2) * 4+offsetX, 112, 65535)
  display.text(str(item3), 64 - len(item3) * 4+offsetX, 120, 65535)
  if emulated: display.text(lang[3], 0+offsetX, 96, 65535)
  display.commit()

def gamePrep():
	global select, menu, shipX, meteorAY, meteorBY, meteorCY, meteorsShotInSession, fVA, fVB, fVC, lives, meteors, selectMeteor, mAH, mBH, mCH
	select = 0
	menu = 0
	shipX = -4
	meteorAY = -40
	mAH = 3
	meteorBY = -40
	mBH = 3
	meteorCY = -40
	mCH = 3
	meteorsShotInSession = 0
	fVA = 2
	fVB = 3
	fVC = 3
	lives = 1
	if meteors == 0:
	    selectMeteor = [0, 1, 0]
	elif meteors == 1:
	    selectMeteor = [1, 0, 1]
	elif meteors == 2:
	    selectMeteor = [1, 1, 1]
	shuffleMeteors()
	game()

def selectModulo():
  global emulated, networks
  if menu == 1:
    return(6)
  elif menu == 5:
    if emulated: return(5)
    else: return(6)
  elif menu == 6 or menu == 12:
    return(3)
  elif menu == 7:
    return(3)
  elif menu == 11:
    temp = len(networks)+1
    return(temp)

def drawlaser(untilWhere):
    global shipX, fastl
    i = 79
    while not i <= untilWhere+20:
      drawgame()
      display.rect(shipX+15+offsetX, i, 3, 6, 63488, 1)
      display.commit()
      i -= fastl+3

def shootlaser():
  global fastl, inCooldown, meteorAY, meteorBY, meteorCY, money, coinsUpg, multi, meteorsShotInSession, shipPos, tone, mAH, mBH, mCH
  if tone: piezo.tone(1000,50)
  inCooldown = True
  if shipPos == 1:
    drawlaser(meteorAY)
    if meteorKill > meteorAY >= -20:
      mAH -= laser+1
      if mAH <= 0:
        mAH = 3
        meteorAY = -40
        money += (coinsUpg + 1)*multi
        meteorsShotInSession += 1
        shuffleMeteors()
  elif shipPos == 2:
    drawlaser(meteorBY)
    if meteorKill > meteorBY >= -20:
      mBH -= laser+1
      if mBH <= 0:
        mBH = 3
        meteorBY = -40
        money += (coinsUpg + 1)*multi
        meteorsShotInSession += 1
        shuffleMeteors()
  elif shipPos == 3:
    drawlaser(meteorCY)
    if meteorKill > meteorCY >= -20:
      mCH -= laser+1
      if mCH <= 0:
        mCH = 3
        meteorCY = -40
        money += (coinsUpg + 1)*multi
        meteorsShotInSession += 1
        shuffleMeteors()

def langSelect():
  global startValue, targetValue, step, mod, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  display.fill(16)
  display.text(lang[33], 64-len(lang[33])*4+offsetX, 0, 65535)
  display.text("English", 128-len("English")*8+offsetX, (0-select+4)*15, 65535)
  display.text("Hrvatski", 128-len("Hrvatski")*8+offsetX, (0-select+5)*15, 65535)
  display.text("Deutsch "+lang[34], 128-len("Deutsch "+lang[34])*8+offsetX, (0-select+6)*15, 65535)
  display.blit(sprite_en, 8+offsetX, (0-select+4)*15, 0)
  display.blit(sprite_hr, 8+offsetX, (0-select+5)*15, 0)
  display.blit(sprite_de, 8+offsetX, (0-select+6)*15, 65535)
  if emulated: display.text(lang[3], 0+offsetX, 120, 65535)

def wifi_connect_request():
  display.fill(16)
  display.text('...', 52+offsetX, 60, 65535)
  display.commit()
  if any(net[0].decode() == ssid for net in wlan.scan()):
    global ssid, pswd
    with open('wifi.txt', 'w') as f:
      f.write(ssid + '\n')
      f.write(pswd + '\n')
    save()
    wlan.disconnect()
    import machine
    machine.soft_reset()

def downButton():
  global startValue, targetValue, step, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  if selectModulo():
    select = (select+1)%selectModulo()
    scroll()
  elif menu == 8:
    LVK.downPress()
buttons.on_press(Buttons.Down, downButton)

def upButton():
  global startValue, targetValue, step, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  if selectModulo():
    select = (select-1)%selectModulo()
    scroll()
  elif menu == 8:
    LVK.upPress()
buttons.on_press(Buttons.Up, upButton)

def aButton():
  global ssid, pswd, fastl, tone, code, step, select, i, x, menu, money, item, laser, item2, meteors, coinsUpg, value, shipX, shipPos, meteorAY, meteorBY, meteorCY, meteorsShotInSession, fVA, fVB, fVC, cooldown, inCooldown, multi, lang
  if menu == 0:
    shootlaser()
  elif menu == 1:
    if select == 0:
      select = 0
      helps()
    elif select == 1:
      select = 0
      menu = 2
      buymenu()
    elif select == 2:
      menu = 5
      select = 0
      mainmenu2()
      display.text(">",0+offsetX,60,65535)
      display.commit()
    elif select == 3:
      menu = 4
      about()
    elif select == 4:
      pass
    elif select == 5:
      global running
      running = False
      save()
      display.fill(65535)
      display.blit(sprite_qr, 0, 0, 0)
      display.commit()
  elif menu == 2:
    if value != 9999 and money >= value:
      if tone: piezo.tone(200, 50)
      money -= value
      if select == 0:
        laser += 1
      elif select == 1:
        meteors += 1
      elif select == 2:
        coinsUpg += 1
      elif select == 3:
        fastl += 1
      save()
      buymenu()
      shopitem()
    else:
      temp = value != 9999
      if temp:
        display.text(str(money), 13+offsetX, 0, 63488)
        display.commit()
      if tone: piezo.tone(125, 50)
      time.sleep(0.25)
      if temp:
        display.text(str(money), 13+offsetX, 0, 65535)
        display.commit()
  elif menu == 3:
    if select == 2:
      menu = 0
      gamePrep()
    else:
      select += 1
      helps()
  elif menu == 5:
    if select == 0:
      tone = not tone
      mainmenu2()
      display.text(">",0+offsetX,60,65535)
      display.commit()
    elif select == 1:
      menu = 6
      if lang == lang_en:
        select = 0
      elif lang == lang_hr:
        select = 1
      elif lang == lang_de:
        select = 2
      langSelect()
      display.text(">",0+offsetX,60,65535)
      display.commit()
    elif select == 2:
      save()
      print('Save OK')
      display.text(lang[39],64-len(lang[39])*4+offsetX,60,16)
      display.text('OK',56+offsetX,60,65535)
      display.commit()
    elif select == 3:
      global money, laser, meteors, coinsUpg, tone, totalDistance, lang, fastl, ssid, pswd
      money = 0
      laser = 0
      meteors = 0
      coinsUpg = 0
      tone = True
      totalDistance = 0
      fastl = 0
      ssid = None
      pswd = None
      import os
      try: os.remove('data.txt')
      except OSError: pass
      try: os.remove('wifi.txt')
      except OSError: pass
      print('Reset OK')
      display.text(lang[40],64-len(lang[40])*4+offsetX,60,16)
      display.text('OK',56+offsetX,60,65535)
      display.commit()
    elif select == 4:
      save()
      import machine
      machine.soft_reset()
    elif select == 5:
      menu = 7
      select = 0
      networkMenu()
      display.text(">",0+offsetX,60,65535)
      display.commit()
  elif menu == 6:
    if select == 0:
      lang = lang_en[:]
    elif select == 1:
      lang = lang_hr[:]
    elif select == 2:
      lang = lang_de[:]
    menu = 5
    select = 1
    mainmenu2()
    display.text(">",0+offsetX,60,65535)
    display.commit()
  elif menu == 7:
      if select == 0:
          menu = 11
          select = 0
          scanNetworks()
          listNetworks()
          display.text(">",0+offsetX,60,65535)
          display.commit()
      elif select == 1:
          LVK.init()
      elif select == 2:
          print(ssid,pswd)
          if not (ssid == None or pswd == None):
              wifi_connect_request()
  elif menu == 8:
      LVK.select()
  elif menu == 10:
      minigame(True)
  elif menu == 11:
      if select == 0:
          menu = 11
          select = 0
          scanNetworks()
          listNetworks()
          display.text(">",0+offsetX,60,65535)
          display.commit()
      else:
          ssid = networks[select-1][0].decode()
          menu = 7
          select = 0
          networkMenu()
          display.text(">",0+offsetX,60,65535)
          display.commit()
  elif menu == 12:
    if select == 0:
      lang = lang_en[:]
    elif select == 1:
      lang = lang_hr[:]
    elif select == 2:
      lang = lang_de[:]
    menu = 1
    select = 0
    display.fill(0)
    startup()
buttons.on_press(Buttons.A, aButton)

def menuButton():
  global menu, select, money, code
  if menu == 0 or menu == 10:
    save()
    if tone: piezo.tone(1000, 150)
    if tone: piezo.tone(500, 150)
    select = 0
    menu = 1
    mainmenu()
    scroll()
  elif menu == 1:
    global running
    running = False
    save()
    display.fill(16)
    display.text('webrepl on',0+offsetX,0,65535)
    display.text('pass 1234',0+offsetX,8,65535)
    display.text('port 8266, ip:',0+offsetX,16,65535)
    display.text(wlan.ifconfig()[0],0+offsetX,24,65535)
    display.commit()
    import webrepl
    webrepl.start(password='1234')
  elif menu == 8:
    LVK.shiftLock()
buttons.on_press(Buttons.C, menuButton)

def bButton():
  global startValue, targetValue, step, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value
  if menu == 2:
    menu = 1
    select = 1
    mainmenu()
    display.text(">",0+offsetX,60,65535)
    display.commit()
  elif menu == 4:
    menu = 1
    select = 3
    mainmenu()
    display.text(">",0+offsetX,60,65535)
    display.commit()
  elif menu == 5:
    menu = 1
    select = 2
    mainmenu()
    display.text(">",0+offsetX,60,65535)
    display.commit()
  elif menu >= 6 and menu < 8:
    menu = 5
    select = 0
    mainmenu2()
    display.text(">",0+offsetX,60,65535)
    display.commit()
  elif menu == 3:
    menu = 0
    gamePrep()
  elif menu == 8:
    LVK.backspace()
  elif menu == 10:
    select += 1
    if tone: piezo.tone(200, 50)
    select = select % 8
  elif menu == 11:
    menu = 7
    select = 0
    networkMenu()
    display.text(">", 0+offsetX, 60, 65535)
    display.commit()
buttons.on_press(Buttons.B, bButton)

def rightButton():
	global startValue, targetValue, step, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value, shipX, shipXchngBy
	if menu == 0:
	  shipX = shipX + shipXchngBy
	  if shipX > 100:
	    shipX = 100
	  if tone: piezo.tone(200, 50)
	  game()
	elif menu == 2:
	  buymenu2(16, 0, 2)
	  buyscrollr(0, -72, 3)
	  buymenu2(0, 16, -2)
	  select = (select+1)%4
	  buymenu()
	  shopitem()
	elif menu == 8:
	  LVK.rightPress()
buttons.on_press(Buttons.Right, rightButton)

def leftButton():
	global startValue, targetValue, step, select, i, x, menu, item, laser, item2, meteors, coinsUpg, value, shipX, shipXchngBy
	if menu == 0:
	  shipX = shipX - shipXchngBy
	  if shipX < -4:
	    shipX = -4
	  if tone: piezo.tone(200, 50)
	  game()
	elif menu == 2:
	  buymenu2(16, 0, 2)
	  buyscrollr(0, 72, -3)
	  buymenu2(0, 16, -2)
	  select = (select-1)%4
	  buymenu()
	  shopitem()
	elif menu == 8:
	  LVK.leftPress()
buttons.on_press(Buttons.Left, leftButton)

select = 0
menu = 1
laser = 0
meteors = 0
coinsUpg = 0
print('Meteor Shooter',version)
print('Za Školu budućnosti, Stemi LAB')
print('GitHub: https://github.com/MrUsername7/PublicStuff/tree/main/The%20Bit%20Superstars/Meteor%20Shooter')
startup()
if menu == 1:
    mainmenu()
    display.text(str(">"),0+offsetX,60,65535)
    display.commit()
while running:
  buttons.scan()
  if menu == 0:
    temp = random.randint(0,2)
    if temp == 0 and selectMeteor[0]:
      meteorAY += random.randint(fVA,fVB)/fVC
    elif temp == 1 and selectMeteor[1]:
      meteorBY += random.randint(fVA,fVB)/fVC
    elif temp == 2 and selectMeteor[2]:
      meteorCY += random.randint(fVA,fVB)/fVC
    if meteorAY >= 130:
      mAH = 3
      meteorAY = -40
      shuffleMeteors()
    elif meteorBY >= 130:
      mBH = 3
      meteorBY = -40
      shuffleMeteors()
    elif meteorCY >= 130:
      mCH = 3
      meteorCY = -40
      shuffleMeteors()
    game()
  elif menu == 10:
      minigame()
  if flicker:
    if menu == 0 or menu == 3:
      display.fill(0)
      display.commit()
      if menu == 3:
        help()
