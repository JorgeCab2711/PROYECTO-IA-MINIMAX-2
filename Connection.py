from socketIO_client import SocketIO
import random
import numpy as np
import time


server_url = "http://localhost"
server_port = 4000
socketIO = SocketIO(server_url, server_port)



class Connect4AI:
    def __init__(self):
        self.ROWS = 6
        self.COLS = 7
        self.EMPTY = 0
        self.PLAYER = 1
        self.AI = 2

    def create_board(self):
        board = np.zeros((self.ROWS, self.COLS))
        return board

    def print_board(self, board):
        for r in range(self.ROWS-1, -1, -1):
            for c in range(self.COLS):
                if board[r][c] == self.EMPTY:
                    print("| ", end="")
                elif board[r][c] == self.PLAYER:
                    print("|X", end="")
                elif board[r][c] == self.AI:
                    print("|O", end="")
            print("|")
        print("-----------------")

    def drop_piece(self, board, row, col, piece):
        board[row][col] = piece

    def is_valid_location(self, board, col):
        return board[self.ROWS-1][col] == self.EMPTY

    def get_next_open_row(self, board, col):
        for r in range(self.ROWS):
            if board[r][col] == self.EMPTY:
                return r

    def winning_move(self, board, piece):
        for c in range(self.COLS - 3):
            for r in range(self.ROWS):
                if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                    return True

        for c in range(self.COLS):
            for r in range(self.ROWS - 3):
                if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                    return True

        for c in range(self.COLS - 3):
            for r in range(self.ROWS - 3):
                if board[r][c] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                    return True

        for c in range(self.COLS - 3):
            for r in range(3, self.ROWS):
                if board[r][c] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                    return True

        return False

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = self.PLAYER if piece == self.AI else self.AI

        if np.count_nonzero(window == piece) == 4:
            score += 1000
        elif np.count_nonzero(window == piece) == 3 and np.count_nonzero(window == self.EMPTY) == 1:
            score += 10
        elif np.count_nonzero(window == piece) == 2 and np.count_nonzero(window == self.EMPTY) == 2:
            score += 5

        if np.count_nonzero(window == opp_piece) == 3 and np.count_nonzero(window == self.EMPTY) == 1:
            score -= 100

        return score

    def score_position(self, board, piece):
        score = 0

        # Evaluación de ventanas horizontales
        row_windows = np.lib.stride_tricks.sliding_window_view(board, window_shape=(4, self.COLS))
        score += np.sum(self.evaluate_window(row_windows, piece))

        # Evaluación de ventanas verticales
        col_windows = np.lib.stride_tricks.sliding_window_view(board, window_shape=(self.ROWS, 4))
        score += np.sum(self.evaluate_window(col_windows, piece))

        # Evaluación de ventanas diagonales positivas
        diagonal_pos_windows = np.lib.stride_tricks.sliding_window_view(board, window_shape=(4, 4))
        score += np.sum(self.evaluate_window(diagonal_pos_windows, piece))

        # Evaluación de ventanas diagonales negativas
        diagonal_neg_windows = np.lib.stride_tricks.sliding_window_view(np.flip(board, axis=0), window_shape=(4, 4))
        score += np.sum(self.evaluate_window(diagonal_neg_windows, piece))

        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, self.AI):
                    return (None, 100000000000000)
                elif self.winning_move(board, self.PLAYER):
                    return (None, -10000000000000)
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(board, self.AI))

        if maximizing_player:
            value = -np.Inf
            column = np.random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                temp_board = board.copy()
                self.drop_piece(temp_board, row, col, self.AI)
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
        else:
            value = np.Inf
            column = np.random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                temp_board = board.copy()
                self.drop_piece(temp_board, row, col, self.PLAYER)
                new_score = self.minimax(temp_board, depth - 1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def is_terminal_node(self, board):
        return self.winning_move(board, self.PLAYER) or self.winning_move(board, self.AI) or len(self.get_valid_locations(board)) == 0

    def get_valid_locations(self, board):
        valid_locations = []
        for col in range(self.COLS):
            if self.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations

    

    def play_game(self):
        board = self.create_board()
        game_over = False
        time_taken = 0

        while not game_over:
            col = int(input("Selecciona una columna (0-6): "))

            if self.is_valid_location(board, col):
                row = self.get_next_open_row(board, col)
                self.drop_piece(board, row, col, self.PLAYER)

                if self.winning_move(board, self.PLAYER):
                    print("La IA 1 ha ganado.")
                    game_over = True

            start = time.time()
            col, _ = self.minimax(board, 6, -np.inf, np.inf, True)
            end = time.time()
            print(f'Tiempo de ejecución de minimax: {end - start} segundos')

            if self.is_valid_location(board, col):
                row = self.get_next_open_row(board, col)
                self.drop_piece(board, row, col, self.AI)

                if self.winning_move(board, self.AI):
                    print("La IA 2 ha ganado.")
                    game_over = True

            if len(self.get_valid_locations(board)) == 0 and not game_over:
                print("¡Es un empate!")
                game_over = True

            for i in board:
                print(i)

ia = Connect4AI()

def on_connect():
    print("Connected to server")
    socketIO.emit('signin', {
        'user_name': "George Knight",
        'tournament_id': 5555,
        'user_role': 'player'
    })

def on_ok_signin():
    print("Login")

def on_ready(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    board = data['board'][::-1]
    print("I'm player:", player_turn_id)
    for i in board:
        print(i)
    
    # Your logic / user input here
    move = ia.minimax(np.array(board), 5, -np.Inf, np.Inf, True)[0]
    print("Move in:", move)
    socketIO.emit('play', {
        'tournament_id': 5555,
        'player_turn_id': player_turn_id,
        'game_id': game_id,
        'movement': move
    })

def on_finish(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    winner_turn_id = data['winner_turn_id']
    board = data['board']

    # Your cleaning board logic here

    print("Winner:", winner_turn_id)
    for i in board:
        print(i)
    socketIO.emit('player_ready', {
        'tournament_id': 5555,
        'player_turn_id': player_turn_id,
        'game_id': game_id
    })

socketIO.on('connect', on_connect)
socketIO.on('ok_signin', on_ok_signin)
socketIO.on('finish', on_finish)
socketIO.on('ready', on_ready)
socketIO.on('finish', on_finish)

socketIO.wait()
