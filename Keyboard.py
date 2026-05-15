from Bit import *

begin()

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
    ["!","\"","£","$","%","^","&","*","(",")","_","+"],
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
                        display.rect(int(j*8), int(i*8), int(8), int(8), cls.textSelectedClr, True)
                    else:
                        display.rect(int(j*8), int(i*8), int(8), int(8), cls.textBgClr, True)
                    if cls.shifted:
                        display.text(cls.keyboardUppercaseText[i][j], j*8, i*8, cls.textClr)
                    else:
                        display.text(cls.keyboardLowercaseText[i][j], j*8, i*8, cls.textClr)
                except IndexError:
                    pass
        if cls.selectX == 0 and cls.selectY == 4:
            display.rect(0, 32, 24, 8, cls.textSelectedClr, True)
        else:
            display.rect(0, 32, 24, 8, cls.textBgClr, True)
        display.text('ESC', 0, 32, cls.textClr)
        if cls.selectX == 0 and cls.selectY == 5:
            display.rect(0, 40, 40, 8, cls.textSelectedClr, True)
        else:
            display.rect(0, 40, 40, 8, cls.textBgClr, True)
        display.text('ENTER', 0, 40, cls.textClr)
        if cls.selectX == 1 and cls.selectY == 4:
            display.rect(24, 32, 40, 8, cls.textSelectedClr, True)
        else:
            display.rect(24, 32, 40, 8, cls.textBgClr, True)
        display.text('SPACE', 24, 32, cls.textClr)
        if len(cls.inputt) > 16:
            display.text(cls.inputt[-16:], 0, 120, cls.textClr)
        else:
            display.text(cls.inputt, 0, 120, cls.textClr)
        display.text("A: Select", 0, 48, cls.textClr)
        display.text("B: Backspace", 0, 56, cls.textClr)
        display.text("C: Shift Toggle", 0, 64, cls.textClr)
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
        except IndexError:
            if cls.selectX == 1 and cls.selectY == 4:
                cls.inputt = str(cls.inputt)+" "
            else:
                cls.end()
        cls.drawKeyboard()
        display.commit()
    @classmethod
    def init(cls):
        cls.drawKeyboard()
    @classmethod
    def end(cls):
        if cls.selectY == 4:
            pass #per-game logic
        elif cls.selectY == 5:
            pass #per-game logic
    @classmethod
    def shiftLock(cls):
        cls.shifted = not cls.shifted
        cls.drawKeyboard()
    @classmethod
    def backspace(cls):
        cls.inputt = cls.inputt[:-1]
        cls.drawKeyboard()


buttons.on_press(Buttons.Right, lambda:LVK.rightPress())
buttons.on_press(Buttons.Left, lambda:LVK.leftPress())
buttons.on_press(Buttons.Up, lambda:LVK.upPress())
buttons.on_press(Buttons.Down, lambda:LVK.downPress())
buttons.on_press(Buttons.A, lambda:LVK.select())
buttons.on_press(Buttons.B, lambda:LVK.backspace())
buttons.on_press(Buttons.C, lambda:LVK.shiftLock())

LVK.init()

while True:
    buttons.scan()
