class Move:
    def __init__(
        self, initital, final, is_a_capture=False, is_a_pawn_move=False
    ):  # initial and final are squares
        self.initial = initital
        self.final = final
        self.is_a_capture = is_a_capture
        self.is_a_pawn_move = is_a_pawn_move

    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final

    def is_it_pawn_move(self):
        return self.is_a_pawn_move

    def is_it_a_capture(self):
        return self.is_a_capture

    def pawn_move_or_capture(self):
        return self.is_a_pawn_move or self.is_a_capture

    def set_pawn_move(self, condition):
        self.is_a_pawn_move = condition

    def set_capture(self, condition):
        self.is_a_capture = condition

    def set_pawn_move_and_capture(self, condition):
        self.is_a_capture = condition
        self.is_a_pawn_move = condition
