class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def as_tuple(self) -> tuple:
        return self.x, self.y

    def __str__(self):
        return f'({self.x}, {self.y})'
