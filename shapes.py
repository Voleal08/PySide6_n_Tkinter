from math import *

class Figure:
    def __init__(self):
        pass
    @property
    def area(self):
        return self.get_area()
    @area.setter
    def area(self, value):
        pass

class Triangle(Figure):
    def __init__(self,a,b,c):
        self.a = a
        self.b = b
        self.c = c
        self.p = ((self.a+self.b+self.c)/2)
        if 2 * max(self.b, self.c, self.a) > sum([self.a, self.b, self.c]):
            raise ValueError ( "Треугольника не существует")
    def name(self):
        return "Треугольник"

    def get_area(self):
            return f" Площадь треугольника - {(self.p*(self.p-self.a)*(self.p-self.b)*(self.p-self.c))**(0.5)}, периметр - {self.p}"
    def __str__(self):
        return f'Triangle({self.a},{self.b}, {self.c})'

class Rectangle(Figure):
    def __init__(self,a,b):
        self.a = a
        self.b = b
        if a<=0 or b<=0:
            raise ValueError("Прямоугольника не существует")
    def ar1(self, a = float, b = float):
        self.a = a
        self.b = b
    def get_area(self):
        return f" Площадь прямоугольника - {self.a * self.b}, периметр - {2 * (self.a + self.b)}"
    def name(self):
        return "Прямоугольник"

    def __str__(self):
        return f'Rectangle({self.a},{self.b})'
class Circle(Figure):
    def __init__(self,rad):
        self.rad = rad
        if rad<=0:
            raise ValueError("Круга не существует")
    def ar(self, rad = float ):
        self.rad = rad
    def get_area(self):
        return f" Площадь круга - {pi * (self.rad) ** 2}, периметр - {2 * pi * self.rad}"

    def __str__(self):
        return f'Circle({self.rad})'
    def __repr__(self):
        return f'Circle({self.rad})'
    def name(self):
        return "Круг"

# tri = Triangle(1,2,2)
# print(tri.area)
# cir = Circle(2)
# print(Circle.area(cir))
# rec = Rectangle(3,4)
# print(Rectangle.area(rec))
# tri1 = Triangle(1,2,6)
# print(Triangle.area(tri1))


shapes = [
    Rectangle(7, 4),
    Circle(-3),
    Triangle(7, 4, 5)
]

for shape in shapes:
    print(shape, shape.area)



