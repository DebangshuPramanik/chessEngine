class Move:
    def __init__(self, initital, final):  # initial and final are squares
        self.initial = initital
        self.final = final
        self.is_a_capture = False

    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final and self.is_a_capture == other.is_a_capture