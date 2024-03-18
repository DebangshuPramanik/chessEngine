class Square:

    ALPHACOLS = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}

    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece
        self.alphacol = self.ALPHACOLS[col]

    def has_piece(self):
        return self.piece != None

    def isEmpty(self):
        return not self.has_piece()

    def has_team_piece(self, color):
        return self.has_piece() and self.piece.color == color

    def has_rival_piece(self, color):
        return self.has_piece() and self.piece.color != color

    def isEmpty_or_rival(self, color):
        return self.isEmpty() or self.has_rival_piece(color)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    @staticmethod
    def in_range(*args):
        for argument in args:
            if argument < 0 or argument > 7:
                return False
        return True

    @staticmethod
    def get_alphacol(col):
        ALPHACOLS = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
        return ALPHACOLS[col]
