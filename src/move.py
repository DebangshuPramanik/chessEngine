
class Move:
    def __init__(self, initital, final):  #initial and final are squares
        self.initial = initital
        self.final = final
    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final