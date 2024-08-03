import numpy as np
import random
import time
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal

class SudokuGame:
    def __init__(self):
        self.board = None
        self.solution = None
        self.difficulty = None
        self.hint_count = 3
        self.start_time = None
        self.end_time = None
        self.invalid_moves = 0
        self.max_invalid_moves = 3

    def is_valid(self, board, row, col, num):
        # Check if the number already exists in the row
        for i in range(9):
            if board[row, i] == num:
                return False

        # Check if the number already exists in the column
        for i in range(9):
            if board[i, col] == num:
                return False

        # Check if the number already exists in the 3x3 box
        box_row = row // 3 * 3
        box_col = col // 3 * 3
        for i in range(3):
            for j in range(3):
                if board[box_row + i, box_col + j] == num:
                    return False

        return True

    def generate_board(self, difficulty):
        self.solution = np.zeros((9, 9), dtype=int)
        self.board = np.zeros((9, 9), dtype=int)

        self.solve(self.solution)
        self.board = self.solution.copy()
        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for i in range(9):
            for j in range(9):
                if self.board[i, j] != 0:
                    self.board[i, j] = numbers[self.board[i, j] - 1]

        # Remove some numbers based on the difficulty level
        num_cells_to_remove = 0
        if difficulty == "easy":
            num_cells_to_remove = random.randint(5, 10)
        elif difficulty == "medium":
            num_cells_to_remove = random.randint(41, 49)
        elif difficulty == "hard":
            num_cells_to_remove = random.randint(50, 65)

        cells_removed = 0
        while cells_removed < num_cells_to_remove:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if self.board[row, col] != 0:
                self.board[row, col] = 0
                cells_removed += 1

        self.start_time = time.time()

    def solve(self, board):
        empty_cell = self.find_empty_cell(board)
        if not empty_cell:
            return True

        row, col = empty_cell
        for num in range(1, 10):
            if self.is_valid(board, row, col, num):
                board[row, col] = num
                if self.solve(board):
                    return True
                board[row, col] = 0

        return False

    def find_empty_cell(self, board):
        for i in range(9):
            for j in range(9):
                if board[i, j] == 0:
                    return i, j
        return None

    def is_board_solved(self):
        for i in range(9):
            for j in range(9):
                if self.board[i, j] == 0:
                    return False
        return True

class SudokuGUI(QWidget):
    cell_selected = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.cell_selected.connect(self.handle_cell_selected)
        self.game = SudokuGame()
        self.setWindowTitle("Sudoku Game")
        self.setGeometry(100, 100, 400, 400)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setStyleSheet("background-color: #36454F;")

        self.title_label = QLabel("Sudoku Game")
        self.title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.board_layout = QGridLayout()

        self.cells = []
        for i in range(9):
            row = []
            for j in range(9):
                cell_label = QLabel("")
                cell_label.setAlignment(Qt.AlignCenter)
                cell_label.setFixedSize(40, 40)
                cell_label.setStyleSheet("border: 1px solid black; background-color: #707C80; color: white; font-size: 16px;")
                row.append(cell_label)
                self.board_layout.addWidget(cell_label, i, j)
                cell_label.mousePressEvent = lambda event, row=i, col=j: self.cell_select_handler(row, col, event)
            self.cells.append(row)

        self.layout.addLayout(self.board_layout)

        self.difficulty_label = QLabel("Difficulty Level:")
        self.difficulty_label.setStyleSheet("color: white; font-size: 16px;")
        self.layout.addWidget(self.difficulty_label)

        self.difficulty_buttons_layout = QHBoxLayout()
        self.easy_button = QPushButton("Easy")
        self.easy_button.setStyleSheet("background-color: #808080; color: white; font-size: 16px;")
        self.easy_button.clicked.connect(lambda: self.set_difficulty("easy"))
        self.difficulty_buttons_layout.addWidget(self.easy_button)

        self.medium_button = QPushButton("Medium")
        self.medium_button.setStyleSheet("background-color: #666666; color: white; font-size: 16px;")
        self.medium_button.clicked.connect(lambda: self.set_difficulty("medium"))
        self.difficulty_buttons_layout.addWidget(self.medium_button)

        self.hard_button = QPushButton("Hard")
        self.hard_button.setStyleSheet("background-color: #4d4d4d; color: white; font-size: 16px;")
        self.hard_button.clicked.connect(lambda: self.set_difficulty("hard"))
        self.difficulty_buttons_layout.addWidget(self.hard_button)

        self.layout.addLayout(self.difficulty_buttons_layout)

        self.hint_button = QPushButton("Hint (3 left)")
        self.hint_button.setStyleSheet("background-color: #737373; color: white; font-size: 16px;")
        self.hint_button.clicked.connect(self.show_hint)
        self.layout.addWidget(self.hint_button)

        self.quit_button = QPushButton("Quit")
        self.quit_button.setStyleSheet("background-color: #595959; color: white; font-size: 16px;")
        self.quit_button.clicked.connect(self.quit_game)
        self.layout.addWidget(self.quit_button)

        self.setLayout(self.layout)





    def cell_select_handler(self, row, col, event):
        if event.button() == Qt.LeftButton:
            self.cell_selected.emit(row, col)

    def handle_cell_selected(self, row, col):
        if self.game.difficulty is not None and self.game.board[row, col] == 0:
            num, ok = QInputDialog.getInt(self, "Enter Number", "Enter the number (1-9):", min=1, max=9)
            if ok:
                if self.game.is_valid(self.game.board, row, col, num):
                    self.game.board[row, col] = num
                    self.update_board()

                    if self.game.is_board_solved():
                        self.game.end_time = time.time()
                        elapsed_time = self.game.end_time - self.game.start_time
                        self.show_message(f"Congratulations! You solved the Sudoku in {elapsed_time:.2f} seconds.")
                else:
                    self.game.invalid_moves += 1
                    if self.game.invalid_moves >= self.game.max_invalid_moves:
                        self.show_message("Game Over! You made too many invalid moves.")
                        self.quit_game()

    def update_board(self):
        for i in range(9):
            for j in range(9):
                if self.game.board[i, j] != 0:
                    self.cells[i][j].setText(str(self.game.board[i, j]))
                else:
                    self.cells[i][j].setText("")

    def set_difficulty(self, difficulty):
        self.game.difficulty = difficulty
        self.game.generate_board(difficulty)
        self.update_board()

    def show_hint(self):
        if self.game.hint_count > 0:
            empty_cells = np.argwhere(self.game.board == 0)
            if empty_cells.shape[0] > 0:
                hint_cell = random.choice(empty_cells)
                row, col = hint_cell
                num = self.game.solution[row, col]
                self.game.board[row, col] = num
                self.update_board()
                self.game.hint_count -= 1
                self.hint_button.setText(f"Hint ({self.game.hint_count} left)")

    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec()

    def quit_game(self):
       goodbye_window = GoodbyeWindow()
       goodbye_window.show()
       app.quit()


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Sudoku")
        self.setGeometry(100, 100, 400, 200)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setStyleSheet("background-color: black;")

        self.title_label = QLabel("SUDOKU")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: white; font-size: 36px; font-weight: bold;")

        self.layout.addWidget(self.title_label)

        self.start_button = QPushButton("Start Game")
        self.start_button.setStyleSheet("background-color: #335566; color: white; font-size: 16px;")
        self.start_button.clicked.connect(self.start_game)

        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)
    def start_game(self):
        self.close()
        gui = SudokuGUI()
        gui.show()
        
class GoodbyeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Goodbye")
        self.setGeometry(100, 100, 400, 200)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.message_label = QLabel("    GOOD-BYE    ")
        self.message_label = QLabel("Presented by Aqsa Hanzala Yamann")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: black; font-size: 20px; font-weight: bold;")

        self.layout.addWidget(self.message_label)

        self.setLayout(self.layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Set the application style to Fusion
    welcome_window = WelcomeWindow()
    welcome_window.show()
    Goodbye_window = GoodbyeWindow()
    sys.exit(app.exec_())
    GoodbyeWindow.show()

