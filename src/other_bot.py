#!/usr/bin/env python3
from multiprocessing import Pool
from number_board import NumberBoard
from move import *

def tbm(b, nm):
    sq = b.at(nm.start)
    eq = b.at(nm.end)
    return Move(sq, eq)

def ab(board, depth, white):
    def order_moves(moves, board):
        # pv : piece value
        for move in moves:
            pv = board.at(move.start)


    def alphabeta(board, depth, alpha, beta, white):
        #moves = board.calc_color_moves(1) if white else board.calc_color_moves(-1)
        #order_moves(moves, board)
        tb = board.copy()
        if depth==0: return board.evaluate_board()
        if white:
            val = float('-inf')
            for move in board.calc_color_moves(1):
                tb.move(move)
                val = max(val, alphabeta(tb, depth-1, alpha, beta, False))
                if val > beta: break
                alpha = max(alpha, val)
                tb.take_back()
            return val
        else:
            val = float('inf')
            for move in board.calc_color_moves(-1):
                tb.move(move)
                val = min(val, alphabeta(tb, depth-1, alpha, beta, True))
                if val < alpha:
                    break
                beta = min(beta, val)
                tb.take_back()
            return val
    return alphabeta(board, depth, float('-inf'), float('inf'), white)


def eval_move(state):
    board, move = state
    tb = board.copy()
    tb.move(move)
    val = ab(tb, 2, True)
    #print(move)
    #tb.print()
    #print(val)
    #print("---")
    return (move, val)

def find_best_move(board):
    nb = NumberBoard(board)
    assert(nb.move_number % 2 == 1, "Can't play for white")
    mvs = nb.calc_color_moves(-1)
    return tbm(board, min(map(eval_move, [(nb, mv) for mv in mvs]), key=lambda x: x[1])[0])
