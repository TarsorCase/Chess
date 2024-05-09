import pygame
import sys
import chess
from const import *
from game import Game
from square import Square
from move import Move
import copy


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Game()
        self.computer_player = False  # Variable to track if playing against computer

    def mainloop(self):

        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        def machine_move(boardCopy):
            max_value = -99999
            movement = ""
            legal_moves = boardCopy.legal_moves()
            for move in legal_moves:
                result = alphabeta_pruning(copy.deepcopy(boardCopy), move, 3, -999999, 9999999, False)
                if result > max_value:
                    movement = move
                    max_value = result
            return movement

        def alphabeta_pruning(boardCopy, movement, depth, alpha, beta, maximizingPlayer):
            if depth == 0:
                return evaluateBoard(boardCopy, movement)

            boardCopy.push(chess.Move.from_uci(movement))
            legal_moves = [str(mov) for mov in boardCopy.legal_moves]

            if maximizingPlayer:
                value = -999999
                for move in legal_moves:
                    value = max(value, alphabeta_pruning(boardCopy.copy(), move, depth - 1, alpha, beta, False))
                    if value >= beta:
                        break
                    alpha = max(alpha, value)
                return value
            else:
                value = 999999
                for move in legal_moves:
                    value = min(value, alphabeta_pruning(boardCopy.copy(), move, depth - 1, alpha, beta, True))
                    if value <= alpha:
                        break
                    beta = min(beta, value)
                return value

        def evaluateBoard(boardCopy, movement):
            value = 0
            boardCopy.push(chess.Move.from_uci(movement))
            for i in range(8):
                for j in range(8):
                    piece = str(boardCopy.piece_at(chess.Square((i * 8 + j))))
                    value += getValueOfPiece(piece)
            return value

        def getValueOfPiece(letter):
            if letter == 'r':
                return 50
            if letter == 'n':
                return 30
            if letter == 'b':
                return 30
            if letter == 'q':
                return 90
            if letter == 'k':
                return 900
            if letter == 'p':
                return 10

            if letter == 'R':
                return -50
            if letter == 'N':
                return -30
            if letter == 'B':
                return -30
            if letter == 'Q':
                return -90
            if letter == 'K':
                return -900
            if letter == 'P':
                return -10

            return 0

        while True:
            # show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.computer_player:  # Human vs Human
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        # if clicked square has a piece ?
                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            # valid piece (color) ?
                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                                # show methods
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                    else:  # Human vs Computer
                        # Computer makes a move
                        movement = machine_move(board)
                        board.push(chess.Move.from_uci(movement))

                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE

                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        # show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)

                # click release
                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        # create possible move
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        # valid move ?
                        if board.valid_move(dragger.piece, move):
                            # normal capture
                            captured = board.squares[released_row][released_col].has_piece()
                            board.move(dragger.piece, move)

                            board.set_true_en_passant(dragger.piece)

                            # sounds
                            game.play_sound(captured)
                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            # next turn
                            game.next_turn()

                    dragger.undrag_piece()

                # key press
                elif event.type == pygame.KEYDOWN:

                    # changing themes
                    if event.key == pygame.K_t:
                        game.change_theme()

                    # changing themes
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger

                    # Toggle between Human vs Human and Human vs Computer modes
                    if event.key == pygame.K_c:
                        self.computer_player = not self.computer_player

                # quit application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()


main = Main()
main.mainloop()
