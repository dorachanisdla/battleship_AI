import tkinter as tk
import random

# Kích thước bản đồ và danh sách tàu
GRID_SIZE = 10
SHIPS = [5, 4, 3, 2, 1]  # Độ dài các con tàu

class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Battleship Game")

        self.player_board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.ai_board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.player_visible_board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.turn = "Player"  # Lượt chơi ban đầu
        self.current_ship_index = 0
        self.current_ship_orientation = "Horizontal"  # Chiều ngang mặc định
        self.ai_ships = []
        self.player_hits = 0
        self.ai_hits = 0
        self.total_ship_cells = sum(SHIPS)
        self.setup_phase = True
        self.ai_target_queue = []  # Hàng đợi các nước đi ưu tiên của AI
        self.placed_ships = 0  # Đếm số tàu đã được đặt

        # Giao diện
        self.message = tk.Label(root, text="Sắp xếp tàu của bạn!", font=("Arial", 14))
        self.message.pack()

        self.info_label = tk.Label(root, text=f"Đang đặt tàu: {SHIPS[self.current_ship_index]} ô, Chiều: {self.current_ship_orientation}", font=("Arial", 12))
        self.info_label.pack()

        self.board_frame = tk.Frame(root)
        self.board_frame.pack()

        # Bản đồ người chơi
        self.player_buttons = [
            [tk.Button(self.board_frame, width=2, height=1, bg="white", command=lambda x=i, y=j: self.place_ship(x, y))
             for j in range(GRID_SIZE)] for i in range(GRID_SIZE)
        ]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.player_buttons[i][j].grid(row=i, column=j)

        # Điều khiển
        self.controls = tk.Frame(root)
        self.controls.pack()

        self.next_button = tk.Button(self.controls, text="Next Ship", command=self.next_ship)
        self.next_button.grid(row=0, column=0, padx=5)

        self.before_button = tk.Button(self.controls, text="Before Ship", command=self.previous_ship)
        self.before_button.grid(row=0, column=1, padx=5)

        self.turn_button = tk.Button(self.controls, text="Turn", command=self.turn_ship)
        self.turn_button.grid(row=0, column=2, padx=5)

        self.play_button = tk.Button(self.controls, text="Let's Play!", state=tk.DISABLED, command=self.start_game)
        self.play_button.grid(row=0, column=3, padx=5)

        # Bản đồ AI
        self.ai_frame = tk.Frame(root)
        self.ai_frame.pack()

        self.ai_buttons = [
            [tk.Button(self.ai_frame, width=2, height=1, bg="white", command=lambda x=i, y=j: self.player_guess(x, y))
             for j in range(GRID_SIZE)] for i in range(GRID_SIZE)
        ]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.ai_buttons[i][j].grid(row=i, column=j)

        self.place_ai_ships()

    def place_ship(self, x, y):
        if not self.setup_phase:
            return

        length = SHIPS[self.current_ship_index]
        valid = True

        # Kiểm tra đặt tàu hợp lệ
        if self.current_ship_orientation == "Horizontal":
            if y + length > GRID_SIZE:
                valid = False
            else:
                for j in range(y, y + length):
                    if self.player_board[x][j] == 1:
                        valid = False
                        break
        else:
            if x + length > GRID_SIZE:
                valid = False
            else:
                for i in range(x, x + length):
                    if self.player_board[i][y] == 1:
                        valid = False
                        break

        # Đặt tàu nếu hợp lệ
        if valid:
            if self.current_ship_orientation == "Horizontal":
                for j in range(y, y + length):
                    self.player_board[x][j] = 1
                    self.player_buttons[x][j].config(bg="gray")
            else:
                for i in range(x, x + length):
                    self.player_board[i][y] = 1
                    self.player_buttons[i][y].config(bg="gray")

            self.placed_ships += 1
            self.next_ship()

    def next_ship(self):
        if self.setup_phase:
            self.current_ship_index += 1
            if self.current_ship_index >= len(SHIPS):
                if self.placed_ships < len(SHIPS):  # Kiểm tra xem người chơi đã đặt đủ tàu chưa
                    self.message.config(text="Bạn chưa đặt đủ tàu! Hãy đặt tất cả các tàu.")
                    return
                self.setup_phase = False
                self.play_button.config(state=tk.NORMAL)
                self.message.config(text="Hoàn tất! Nhấn Let's Play để bắt đầu.")
            else:
                self.update_info_label()

    def previous_ship(self):
        if self.setup_phase and self.current_ship_index > 0:
            self.current_ship_index -= 1
            self.update_info_label()

            # Cho phép người chơi di chuyển tàu trước đó
            self.remove_last_ship()

    def turn_ship(self):
        self.current_ship_orientation = (
            "Vertical" if self.current_ship_orientation == "Horizontal" else "Horizontal"
        )
        self.update_info_label()

    def update_info_label(self):
        self.info_label.config(text=f"Đang đặt tàu: {SHIPS[self.current_ship_index]} ô, Chiều: {self.current_ship_orientation}")

    def remove_last_ship(self):
        length = SHIPS[self.current_ship_index]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.player_board[i][j] == 1:
                    self.player_board[i][j] = 0
                    self.player_buttons[i][j].config(bg="white")

    def place_ai_ships(self):
        for length in SHIPS:
            placed = False
            while not placed:
                orientation = random.choice(["Horizontal", "Vertical"])
                x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                valid = True

                if orientation == "Horizontal":
                    if y + length > GRID_SIZE:
                        valid = False
                    else:
                        for j in range(y, y + length):
                            if self.ai_board[x][j] == 1:
                                valid = False
                                break
                else:
                    if x + length > GRID_SIZE:
                        valid = False
                    else:
                        for i in range(x, x + length):
                            if self.ai_board[i][y] == 1:
                                valid = False
                                break

                if valid:
                    if orientation == "Horizontal":
                        for j in range(y, y + length):
                            self.ai_board[x][j] = 1
                    else:
                        for i in range(x, x + length):
                            self.ai_board[i][y] = 1
                    placed = True

    def start_game(self):
        self.message.config(text="Trò chơi bắt đầu! Lượt của bạn.")
        self.play_button.config(state=tk.DISABLED)

    def player_guess(self, x, y):
        if self.turn != "Player" or self.setup_phase or self.ai_buttons[x][y]["state"] == tk.DISABLED:
            return

        if self.ai_board[x][y] == 1:
            self.ai_buttons[x][y].config(bg="red")
            self.player_hits += 1
        else:
            self.ai_buttons[x][y].config(bg="blue")

        self.ai_buttons[x][y].config(state=tk.DISABLED)
        if self.player_hits == self.total_ship_cells:
            self.message.config(text="Bạn đã thắng!")
            self.reveal_ships()
            return

        self.turn = "AI"
        self.message.config(text="Lượt của AI.")
        self.ai_turn()

    def ai_turn(self):
        if self.turn != "AI":
            return

        # AI sẽ chọn một ô để tấn công
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        while self.player_buttons[x][y]["state"] == tk.DISABLED:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)

        if self.player_board[x][y] == 1:
            self.player_buttons[x][y].config(bg="red")
            self.ai_hits += 1
        else:
            self.player_buttons[x][y].config(bg="blue")

        self.player_buttons[x][y].config(state=tk.DISABLED)
        if self.ai_hits == self.total_ship_cells:
            self.message.config(text="AI thắng!")
            self.reveal_ships()
            return

        self.turn = "Player"
        self.message.config(text="Lượt của bạn.")

    def reveal_ships(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.player_board[i][j] == 1:
                    self.player_buttons[i][j].config(bg="red")
                if self.ai_board[i][j] == 1:
                    self.ai_buttons[i][j].config(bg="red")

if __name__ == "__main__":
    root = tk.Tk()
    game = BattleshipGame(root)
    root.mainloop()
