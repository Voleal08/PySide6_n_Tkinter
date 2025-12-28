# class TRoad:
#     def __init__ (self,length0, width0):
#         if length0>0:
#             self.length = length0
#         else:
#             self.length = 0
#         if width0>0:
#             self.width = width0
#         else:
#             self.width = 0
# road = TRoad(60,3)
# class TCar:
#     def __init__(self, road0, p0, v0):
#         self.road = road0
#         self.p = p0
#         self.v = v0
#         self.x = 0
#     def move(self):
#         self.x += self.v
#         if self.x > self.road.length:
#             self.x = 0
# N = 3
# cars = []
# for i in range(N):
#     cars.append(TCar(road, i+1, 2*(i+1)))
# for k in range(100):
#     for i in range(N):
#         cars[i].move()
# print('После 100 шагов:')
# for i in range(N):
#     print(cars[i].x)


class TLogElement:
    def __init__(self):
        self.__in1 = False
        self.__in2 = False
        self._res = False
        self.__nextEl = None
        self.nextIn = 0
    def link(self, nextEl, nextIn):
        self.__nextEl = nextEl
        self.nextIn = nextIn
    def __setIn1(self, newIn1):
        self.__in1 = newIn1
        self.calc()
        if self.__nextEl != None:
            if self.nextIn==1:
                self.__nextEl.In1 = self._res
            elif self.nextIn == 2:
                self.__nextEl.In2 = self._res

    def __setIn2(self, newIn2):
        self.__in2 = newIn2
        self.calc()
        if self.__nextEl != None:
            if self.nextIn==1:
                self.__nextEl.In1 = self._res
            elif self.nextIn == 2:
                self.__nextEl.In2 = self._res
    In1 = property(lambda x: x.__in1, __setIn1)
    In2 = property(lambda x: x.__in2, __setIn2)
    Res = property(lambda x: x._res)
    def calc(self):
        pass
class TNot(TLogElement):
    def __init__(self):
        TLogElement.__init__(self)
    def calc(self):
        self._res = not self.In1
n = TNot()
n.In1 = False
print(n.Res)
class TLog2In(TLogElement):
    pass
class TAnd(TLog2In):
    def __init__(self):
        TLog2In.__init__(self)
    def calc(self):
        self._res = self.In1 and self.In2
class TOr (TLog2In):
    def __init__(self):
        TLog2In.__init__(self)
    def calc(self):
        self._res = self.In1 or self.In2
elNot = TNot()
elAnd = TAnd()
elAnd.link(elNot, 1)
print(' A | B | not(A&B) ')
print('------------------')
for A in range(2):
    for B in range(2):
        elAnd.In1 = A
        elAnd.In2 = B
        print('', A, "|", B, "|", int(elNot.Res))

elNotB = TNot()
elNotA = TNot()
elAndANotB = TAnd()
elAndNotAB = TAnd()
elOr = TOr()

elNotB.link(elAndANotB, 2)
elNotA.link(elAndNotAB, 1)
elAndNotAB.link(elOr, 2)
elAndANotB.link(elOr, 1)

# (a and not b) or (not a and b)

print('------------------')
print()
print(' A | B | A xor B ')
print('------------------')
for A in range(2):
    for B in range(2):
        elNotB.In1 = B
        elNotA.In1 = A
        elAndANotB.In1 = A
        elAndNotAB.In2 = B
        print('', A, "|", B, "|", int(elOr.Res))




























