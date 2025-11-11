from dataclasses import dataclass

@dataclass
class Diff:
    a_delta: int
    b_delta: int

class Scorer:

    def __init__(self):
        self.a = 0
        self.b = 0

    def apply(self, who: str, action: str):
        if action == 'PLUS1':
            if who == 'A':
                self.a += 1
            elif who == 'B':
                self.b += 1
        elif action == 'MINUS1':
            if who == 'A':
                self.a = max(0, self.a - 1)
            elif who == 'B':
                self.b = max(0, self.b - 1)

    def undo(self):

        if self.a>0 or self.b>0:

            pass
