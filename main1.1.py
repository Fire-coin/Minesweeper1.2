from tkinter import *
from threading import Thread, Event
from time import sleep, strftime, gmtime
from random import randint

settings = {
    "flags": 0,
    "curTime": 0,
    "difficulties": ["easy", "medium", "hard", "custom"],
    "difficulty": "easy",
    "squareSize": 50,
    "gridSize": [10, 11],
    "grid": [],
    "minesRatio": 0.2,
    "flagsCount": 0,
    "timerStarted": False,
    "time": 0,
    "zerosList": []
}

colours = {
    "1": "blue",
    "2": "green",
    "3": "red",
    "4": "dark blue",
    "5": "brown",
    "6": "#00bbbb",
    "7": "black",
    "8": "#d3d3d3",
    "-1": "black"
}

cells = {}

event1 = Event()


def zeroUncover(zeros: list[list[int]], w: Canvas):
    if zeros == []:
        return
    zeros2 = []
    a = [-1, 0, 1]
    b = []
    for i in a:
        for j in a:
            if i == j == 0:
                continue
            b.append([i, j])
    
    for i, j in zeros:
        for k in b:
            row = i + k[0]
            column = j + k[1]
            if row < 0 or row > len(settings["grid"]) or column < 0 or column > len(settings["grid"][0]):
                continue
            tag = f"cell{column + 1} {row + 1}"
            if tag not in cells:
                continue
            if settings["grid"][row][column] == 0 and cells[tag] != 1 and cells[tag] != 2:
                w.itemconfigure(tag, fill= "white")
                cells[tag] = 1
                zeros2.append([row, column])
            elif settings["grid"][row][column] > 0 and (cells[tag] != 1 and cells[tag] != 2):
                w.itemconfigure(tag, fill= "white")
                colour = colours[str(settings["grid"][row][column])]
                if settings["difficulty"] == "hard":
                    w.create_text(column * settings["squareSize"] + int(settings["squareSize"] / 2) + 2, row * settings["squareSize"] + int(settings["squareSize"] / 2) + 2, fill= colour, text= str(settings["grid"][row][column]), font= ("Arial", 6))
                else: 
                    w.create_text(column * settings["squareSize"] + int(settings["squareSize"] / 2), row * settings["squareSize"] + int(settings["squareSize"] / 2), fill= colour, text= str(settings["grid"][row][column]))
                cells[tag] = 1
    else:
        zeroUncover(zeros2, w)


def setGrid():
    z = True
    while z:
        settings["grid"] = []
        for i in range(int((winHeight - 50) / settings["squareSize"])):
            row = []
            for j in range(int(winWidth / settings["squareSize"])):
                if randint(1, 100) <= settings["minesRatio"] * 100:
                    row.append(-1)
                    settings["flagsCount"] += 1
                else:
                    row.append(0)
            settings["grid"].append(row)

        a = [-1, 0, 1]
        b = []
        for i in a:
            for j in a:
                if i == j == 0:
                    continue
                b.append([i, j])

        for i in range(int((winHeight - 50) / settings["squareSize"])):
            for j in range(int(winWidth / settings["squareSize"])):
                mines = 0
                if settings["grid"][i][j] != -1:
                    for k in b:
                        if i + k[0] < 0 or j + k[1] < 0 or i + k[0] > (len(settings["grid"]) - 1) or j + k[1] > (len(settings["grid"][0]) - 1):
                            continue
                        elif settings["grid"][i + k[0]][j + k[1]] == -1:
                            mines += 1
                    if mines == 9:
                        z = False
                        break
                    else:
                        settings["grid"][i][j] = mines
                if not z:
                    break
            if not z:
                z = True
                break
        else:
            z = False
                        

def resetBoard() -> None:
    global event1
    global timerThread
    gameOverLabel.place_forget()
    gameWonLabel.place_forget()
    event1.set()
    sleep(.8)
    event1.clear()
    settings["timerStarted"] = False
    settings["flagsCount"] = 0
    flagLabel.configure(text= "Flags: " + str(settings["flagsCount"]))
    timerThread = Thread(target= updateTimer, args= (event1,))
    myCanvas.tag_bind("cover", "<Button-1>", lambda n: processCell(n, True, myCanvas))
    myCanvas.tag_bind("cover", "<Button-3>", lambda n: processCell(n, False, myCanvas))
    makeGrid(myCanvas)


def updateTimer(event: Event) -> None:
    while not event.is_set():
        timeLabel.configure(text=  "Time: " + strftime("%H:%M:%S", gmtime(settings["time"])))
        sleep(1)
        settings["time"] += 1
    else:
        settings["time"] = 0


def makeGrid(w: Canvas) -> None:
    global cells
    w.delete("cover")
    cells = {}
    for i in range(int(winWidth / settings["squareSize"])):
        for j in range(int((winHeight - 50) / settings["squareSize"])):
            w.create_rectangle(i * settings["squareSize"] + 2, j * settings["squareSize"] + 2, (i + 1) * settings["squareSize"] + 2, (j + 1) * settings["squareSize"] + 2, fill= "grey", outline= "black", tags= ("cover", f"cell{i + 1} {j + 1}"))
            cells[f"cell{i + 1} {j + 1}"] = 0
    else:
        w.itemconfigure("cell55", fill= "red")
        settings["gridSize"] = [int(winWidth / settings["squareSize"]), int((winHeight - 50) / settings["squareSize"])]
        setGrid()


def processCell(event, mode: bool, w: Canvas):
    if not settings["timerStarted"]:
        timerThread.start()
        settings["timerStarted"] = True
        flagLabel.configure(text= "Flags: " + str(settings["flagsCount"]))
    x = event.x
    y = event.y
    xPosition = int(x / settings["squareSize"]) + 1
    yPosition = int(y / settings["squareSize"]) + 1
    if mode:
        if cells[f"cell{xPosition} {yPosition}"] == 0:
            if settings["grid"][yPosition - 1][xPosition - 1] == -1:
                endGame()
            cells[f"cell{xPosition} {yPosition}"] = 1
            w.itemconfigure(f"cell{xPosition} {yPosition}", fill= "white")
            if settings["grid"][yPosition - 1][xPosition - 1] == 0:
                zeroUncover([[yPosition - 1, xPosition - 1]], w)
            else:
                colour = colours[str(settings["grid"][yPosition - 1][xPosition - 1])]
                if settings["difficulty"] == "hard":
                    w.create_text((xPosition - 1) * settings["squareSize"] + int(settings["squareSize"] / 2) + 2, (yPosition - 1) * settings["squareSize"] + int(settings["squareSize"] / 2) + 2, fill= colour, text= str(settings["grid"][yPosition - 1][xPosition - 1]), font= ("Arial", 6))
                else: 
                    w.create_text((xPosition - 1) * settings["squareSize"] + int(settings["squareSize"] / 2), (yPosition - 1) * settings["squareSize"] + int(settings["squareSize"] / 2),fill= colour, text= str(settings["grid"][yPosition - 1][xPosition - 1]))
    else:
        if cells[f"cell{xPosition} {yPosition}"] == 0 and settings["flagsCount"] > 0:
            cells[f"cell{xPosition} {yPosition}"] = 2
            settings["flagsCount"] -= 1
            flagLabel.configure(text= "Flags: " + str(settings["flagsCount"]))
            w.itemconfigure(f"cell{xPosition} {yPosition}", fill= "red")
        elif cells[f"cell{xPosition} {yPosition}"] == 2:
            cells[f"cell{xPosition} {yPosition}"] = 0
            settings["flagsCount"] += 1
            flagLabel.configure(text= "Flags: " + str(settings["flagsCount"]))
            w.itemconfigure(f"cell{xPosition} {yPosition}", fill= "grey")
    #TODO Make system which will throw winscreen when all uncovered cells are bombs
    counter = 0
    for key, value in cells.items():
        if value == 0:
            break
    else:
        if counter <= settings["flagsCount"]:
            gameWonLabel.place(relx= .5, rely= .5, anchor= "center")
            global event1
            event1.set()


def endGame():
    global event1
    gameOverLabel.place(relx= .5, rely= .5, anchor= "center")
    myCanvas.tag_unbind("cover", "<Button-1>")
    myCanvas.tag_unbind("cover", "<Button-3>")
    event1.set()


def openSettings() -> None:
    def setting():
        settings["difficulty"] = diff.get()
        updateDifficulty()
        root2.destroy()
        
    
    root2 = Tk()
    root2.geometry("300x400")
    diff = StringVar()
    
    difficultyLabel = Label(root2, text= "Difficulty: ")
    difficultyLabel.pack()
    
    difficultyMenu = OptionMenu(root2, diff, *settings["difficulties"])
    difficultyMenu.pack()
    
    setButton = Button(root2, text= "Set", command= setting).pack()
        

def updateDifficulty():
    if settings["difficulty"] == "easy":
        settings["squareSize"] = 50
    elif settings["difficulty"] == "medium":
        settings["squareSize"] = 25
    elif settings["difficulty"] == "hard":
        settings["squareSize"] = 10
    else:
        settings["squareSize"] = 25
    makeGrid(myCanvas)


def main():
    makeGrid(myCanvas)

timerThread = Thread(target= updateTimer, args= (event1,))
mainThread = Thread(target= main)

root = Tk()
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()

winWidth = 501
winHeight = 600

x = (screenWidth / 2) - (winWidth / 2)
y = (screenHeight / 2) - (winHeight / 2)

#root methods
root.geometry("%dx%d+%d+%d" % (winWidth, winHeight, x, y))
root.resizable(width= 0, height= 0)
root.title("Mine Sweeper 1.0")

myCanvas = Canvas(root, width= winWidth, height= winHeight - 50, bg= "grey")
myCanvas.place(x= -2, y= 48)
myCanvas.tag_bind("cover", "<Button-1>", lambda n: processCell(n, True, myCanvas))
myCanvas.tag_bind("cover", "<Button-3>", lambda n: processCell(n, False, myCanvas))


myFrame = Frame(root, width= winWidth, height= 50)
myFrame.pack()

resetButton = Button(myFrame, text= "Reset", command= resetBoard)
resetButton.place(relx= .5, rely= .5, anchor= "center", width= 45, height= 43)

flagLabel = Label(myFrame, text= "Flags: {}".format(settings["flags"]), font= ("Times New Roman", 15))
flagLabel.place(relx= .13, rely= .5, anchor= "center")

timeLabel = Label(myFrame, text= "Time: 00:00:00", font= ("Time New Roman", 15))
timeLabel.place(relx= .8, rely= .5, anchor= "center")

settingsButton = Button(myFrame, text= "Settings", command= openSettings)
settingsButton.place(relx= .3, rely= .5, anchor= "center")

myCanvas.create_rectangle(0, 0, settings["squareSize"], settings["squareSize"], fill= "black", tag= "cover")

gameOverLabel = Label(root, text= "Game Over", font= ("Times New Roman", 20), fg= "red")
gameOverLabel.place(relx= .5, rely= .5, anchor= "center")
gameOverLabel.place_forget()

gameWonLabel = Label(root, text= "You have won!", font= ("Times New Roman", 20), fg= "green")

mainThread.start()

root.mainloop()