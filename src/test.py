from board import Board
from number_board import *

# board = Board()
nb = NumberBoard(Board())
# print(nb.calc_moves_no_check((7, 1)))
print(nb.calc_moves((6, 1)))
nb.print()
print(nb.calc_moves_no_check((1, 7)))
# print(nb.calc_moves((6, 0)))
# print(nb.calc_moves((6, 3)))
# print(nb.calc_moves((7, 1)))

# nb.print()
#
#nb.from_string(
#    """
#p . k p p p p p
#. P p p p p p p
#. . . . . . . .
#. . . . . . . .
#. . . . . . . .
#. . . . . . . .
#P P P P P P P P
#P P P P P P P P
#"""
#)
#
#nb.print()
#
#print([str(m) for m in nb.calc_moves((0, 0))])
#print([str(m) for m in nb.calc_moves((1, 1))])
#nb.move(Move.from_string('a8->b7'))
#nb.print()
# print(nb.in_check(Move()))

while True:
    nb.print(True)
    m = Move.from_string(input("Enter move:").rstrip())
    nb.move(m)
