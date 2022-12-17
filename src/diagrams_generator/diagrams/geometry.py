class Position:
    x: float
    y: float

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Geometry:
    p: Position
    __w: float
    __h: float

    def __init__(self, x=0.0, y=0.0, w=0.0, h=0.0):
        self.__w = w
        self.__h = h
        self.p = Position(x, y)

    @property
    def x(self):
        return self.p.x

    @property
    def y(self):
        return self.p.y

    @x.setter
    def x(self, value):
        self.p.x = float(value)

    @y.setter
    def y(self, value):
        self.p.y = float(value)

    @property
    def w(self):
        return self.__w

    @property
    def h(self):
        return self.__h

    @w.setter
    def w(self, value):
        self.__w = float(value)

    @h.setter
    def h(self, value):
        self.__h = float(value)
