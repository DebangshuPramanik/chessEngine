from board import Board
from number_board import *
from other_bot import *

# board = Board()
nb = NumberBoard(Board())


def interactive_test():
    print(
        """
    The format for a move is like: a4->b6
    To signify a castle, do the move the king would make.
    To signify promotion, add an =Piece, like a7->a8=Q.
    Valid piece values are [N,B,R,Q] (must be uppercase)
    There is no checking for valid moves. (but promotion will only work if going to the last row)
    """
    )
    nb = NumberBoard(Board())

    while True:
        nb.print(True)
        m = Move.from_string(input("Enter move:").rstrip())
        nb.move(m)


# nb.from_string(
#     """
# r n b q k b n r
# . p p p . p p p
# . . . . . . . .
# p . . . p . . .
# . . B . P . . .
# . . . . . . . .
# P P P P . P P P
# R N B Q K . N R
# """
# )


nb.from_string(
    """
. . . . . . . .
. . . K . . . .
. . . . . . . .
. . . . . . . .
. n n . . . . .
. . . . . . . .
. k . . . . . .
. . . . . . . .
"""
)
nb.print()
print(nb.draw_by_insufficient_material())

nb.from_string(
    """
. . . . . . . .
. . . K . . . .
. . . . P . . .
. . . . . . . .
. n n . . . . .
. . . . . . . .
. k . . . . . .
. . . . . . . .
"""
)
nb.print()
print(nb.draw_by_insufficient_material())

nb.from_string(
    """
. . . . . . . .
. . . K . . . .
. . . . . . . .
. . . . . . . .
. b b . . . . .
. . . . . . . .
. k . . . . . .
. . . . . . . .
"""
)
nb.print()
print(nb.draw_by_insufficient_material())

nb.from_string(
    """
. . . . . b . .
. . . K b b . .
. . . b . . . .
. . b . . . . .
. b . . . . . .
. . . . . . . .
. k . . . . . .
. . . . . . . .
"""
)
nb.print()
print(nb.draw_by_insufficient_material())

nbb = NumberBoard(Board())
nbb.print()


s = """
r n b q k b . r
p p p p p p p p
. . . . . . . .
. . . . . . . .
. . . . n . . .
. . . B . . . .
P P P P . P P P
R N B Q K . N R
"""
