import tkinter as tk
from random import randint
from tkinter import *
from tkinter import messagebox
window = Tk()
window.geometry("1000x1000")
window.title('Фигуры')
canvas = tk.Canvas(window, width=1000, height=1000, bg="white")
canvas.pack()


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def draw(self):
        canvas.create_oval(self.x, self.y, self.x + 15, self.y + 15, fill="blue", outline="blue")

class Line():
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def draw(self):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, fill="#EEE")

class Rectangle():
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def draw(self):
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill="red")
class Triangle:
    def __init__(self, x1, y1, x2, y2, x3, y3):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
    def draw(self):
        canvas.create_polygon(self.x1, self.y1, self.x2, self.y2, self.x3, self.y3, fill = 'blue')


class Oval:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def draw(self):
        canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill="green")



def on_click(event):
    x, y = event.x, event.y
    point = Point(x, y)
    point.draw()

canvas.bind("<Button-1>", on_click)

for i in range(0,1000,10):
        line = Line(0, i, 1000, i)
        line.draw()
for i in range(0,1000,10):
        line = Line(i, 0, i, 1000)
        line.draw()


x1,y1,x2,y2 = [700,700,900,900]
rectangle = Rectangle(x1, y1, x2, y2)
rectangle.draw()

x1,y1,x2,y2 = [300,300,500,600]
oval = Oval(x1, y1, x2, y2)
oval.draw()
x1,y1,x2,y2,x3,y3 = [100,50,400,200,200,400]
triangle = Triangle(x1, y1, x2, y2, x3, y3)
triangle.draw()

window.mainloop()












