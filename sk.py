import pyxel
import random

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self, x, y, size):
        wall_offset = size
        if self.walls['top']:
            pyxel.line(x + wall_offset, y, x + size - wall_offset, y, 7)
        if self.walls['right']:
            pyxel.line(x + size, y + wall_offset, x + size, y + size - wall_offset, 7)
        if self.walls['bottom']:
            pyxel.line(x + wall_offset, y + size, x + size - wall_offset, y + size, 7)
        if self.walls['left']:
            pyxel.line(x, y + wall_offset, x, y + size - wall_offset, 7)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 2  # プレイヤーのサイズを狭い道幅に合わせて変更
        self.delay_timer = 0
    def set_position(self, maze):
        # プレイヤーの位置を迷路の右下に設定
        self.x = maze.cols - 1
        self.y = maze.rows - 1

    def draw(self, x, y, cell_size):
        # プレイヤーの描画位置を調整
        player_offset = (cell_size) // 2
        pyxel.rect(x + player_offset, y + player_offset, self.size, self.size, 8)

    def move(self, maze, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        # 移動先が迷路の範囲内にあるかチェック
        if 0 <= new_x < maze.cols and 0 <= new_y < maze.rows:
            current_cell = maze.cells[self.y][self.x]

            # 移動先のセルの壁の状態を確認して移動可能か判断
            if dx == -1 and not current_cell.walls['left']:
                self.x = new_x
            elif dx == 1 and not current_cell.walls['right']:
                self.x = new_x
            if dy == -1 and not current_cell.walls['top']:
                self.y = new_y
            elif dy == 1 and not current_cell.walls['bottom']:
                self.y = new_y
        # ゴール判定（迷路の左上）
        if self.x == 0 and self.y == 0:
            self.handle_goal()

    def handle_goal(self):
        global maze, game
        self.delay_timer = 60
        text = "Goal reached! Resizing maze..."
        text_width = len(text) * 4
        text_height = 5
        x = (pyxel.width - text_width) / 2
        y = (pyxel.height - text_height) / 2
        pyxel.text(x, y, text, 7)
        pyxel.flip()
        maze.reset_maze()  # 迷路をリセット
        self.x, self.y = maze.cols - 1, maze.rows - 1
        game.reset_timer() 
        game.increment_clear_count()

    def update(self, maze):
        if self.delay_timer > 0:
            self.delay_timer -= 1  # タイマーをデクリメント
            return  # 遅延中は残りの更新をスキップ


    
class Maze:
    def __init__(self, rows, cols, cell_size=24):
        self.rows = rows
        self.cols = cols
        self.cells = [[Cell(row, col) for col in range(cols)] for row in range(rows)]
        self.current_cell = self.cells[0][0]
        self.stack = []
        self.completed = False
        self.cell_size = cell_size
        self.base_rows = rows
        self.base_cols = cols
        self.cell_size = cell_size
        self.reset_maze()
        self.is_generated = False

    def generate_maze(self):
        while not self.completed:
            self.current_cell.visited = True
            next_cell = self.get_next_cell(self.current_cell)

            if next_cell:
                next_cell.visited = True
                self.stack.append(self.current_cell)
                self.remove_walls(self.current_cell, next_cell)
                self.current_cell = next_cell
            elif self.stack:
                self.current_cell = self.stack.pop()
            else:
                self.completed = True  # 迷路の生成が完了した
                self.cells[self.rows - 1][self.cols - 1].walls['bottom'] = False  # スタート地点の下の壁を削除
                self.cells[0][0].walls['top'] = False  # ゴール地点の上の壁を削除
                self.is_generated = True


    def get_next_cell(self, cell):
        neighbors = []

        row, col = cell.row, cell.col
        directions = [('top', row - 1, col), ('bottom', row + 1, col),
                      ('left', row, col - 1), ('right', row, col + 1)]

        for direction, r, c in directions:
            if (0 <= r < self.rows) and (0 <= c < self.cols) and not self.cells[r][c].visited:
                neighbors.append((direction, self.cells[r][c]))

        return random.choice(neighbors)[1] if neighbors else None

    def remove_walls(self, current, next):
        dx = current.col - next.col
        dy = current.row - next.row

        if dx == 1:  # Current is right of next
            current.walls['left'] = False
            next.walls['right'] = False
        elif dx == -1:  # Current is left of next
            current.walls['right'] = False
            next.walls['left'] = False
        if dy == 1:  # Current is below next
            current.walls['top'] = False
            next.walls['bottom'] = False
        elif dy == -1:  # Current is above next
            current.walls['bottom'] = False
            next.walls['top'] = False

    def draw(self):
        offset_x = (pyxel.width - self.cols * self.cell_size) // 2
        offset_y = (pyxel.height - self.rows * self.cell_size) // 2

        for row in self.cells:
            for cell in row:
                x = cell.col * self.cell_size + offset_x
                y = cell.row * self.cell_size + offset_y
                cell.draw(x, y, self.cell_size)


        goal_x, goal_y = 0, 0
        goal_cell_x = goal_x * self.cell_size + offset_x
        goal_cell_y = goal_y * self.cell_size + offset_y
        pyxel.rect(goal_cell_x+1, goal_cell_y+1, self.cell_size*12/16, self.cell_size*12/16, 11)  # 例えば明るい赤色
        pyxel.rect(x+1, y+1, self.cell_size*12/16, self.cell_size*12/16, 10)  # 例えば明るい青色

    def reset_maze(self):
        self.rows = min(20, self.base_rows + 1)
        self.cols = min(20, self.base_cols + 1)
        
        self.base_rows += 1
        self.base_cols += 1
        self.rows = self.base_rows
        self.cols = self.base_cols
        # セルサイズを減らす（ただし、最小値に制限を設ける）
        self.cell_size = max(4, self.cell_size - 1)

        # 迷路の初期化
        self.cells = [[Cell(row, col) for col in range(self.cols)] for row in range(self.rows)]
        self.current_cell = self.cells[0][0]
        self.stack = []
        self.completed = False
        self.cell_size = max(4, self.cell_size - 1) 

class Game:
    def __init__(self):
        self.timer = 570
        self.game_over = False
        self.clear_count = 0
        self.game_clear = False

    def update(self):
        if self.game_over:
            return

        self.timer -= 1
        if self.timer <= 0:
            self.game_over = True

    def draw(self):
        if self.game_clear:
            self.draw_game_clear()  # ゲームクリアメッセージを描画
        elif self.game_over:
            self.draw_game_over()
        else:
            self.draw_timer()
            self.draw_clear_count()

    def draw_timer(self):
        # タイマーの表示（右上）
        seconds = max(0, (self.timer + 30) // 30)  # 秒単位に変換
        pyxel.text(pyxel.width - 40, 15, f"Time: {seconds}", 7)

    def draw_game_over(self):
        pyxel.cls(0)
        # ゲームオーバーのテキストを表示
        pyxel.text(pyxel.width // 2 - 20, pyxel.height // 2, "Game Over", 8)
    
    def reset_timer(self):
        self.timer = 570+(int(self.clear_count)*20)
    
    def draw_clear_count(self):
        # 左上にクリア回数を表示
        pyxel.text(5, 5, f"level: {self.clear_count+1}/10", 7)

    def increment_clear_count(self):
        self.clear_count += 1  # クリア回数を増やす
        if self.clear_count == 10:  # クリア回数が10回になった場合
            self.game_clear = True 
    def draw_game_clear(self):
        pyxel.cls(7)
        # ゲームクリアのテキストを表示
        pyxel.text(pyxel.width // 2 - 55, pyxel.height // 2, "Game Clear!! Congratulations!!", 10)



# その他のクラス（Player, Maze, Cell）は変更なし



def update():
    global maze, player, game
    player.update(maze)
    if not game.game_clear and not game.game_over:
        if pyxel.btnp(pyxel.KEY_SPACE):
            maze.generate_maze()

        if not maze.completed:
            return  # Do not move the player if the maze is not completed

        # Player movement
        if pyxel.btnp(pyxel.KEY_LEFT):
            player.move(maze, -1, 0)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            player.move(maze, 1, 0)
        if pyxel.btnp(pyxel.KEY_UP):
            player.move(maze, 0, -1)
        if pyxel.btnp(pyxel.KEY_DOWN):
            player.move(maze, 0, 1)

    game.update()  # ゲームのタイマー更新

def draw():
    pyxel.cls(0)
    offset_x = (pyxel.width - maze.cols * maze.cell_size) // 2
    offset_y = (pyxel.height - maze.rows * maze.cell_size) // 2
    maze.draw()
    player.draw(player.x * maze.cell_size + offset_x, player.y * maze.cell_size + offset_y, maze.cell_size)
    if not game.game_over:
        maze.draw()
        player.draw(player.x * maze.cell_size + offset_x, player.y * maze.cell_size + offset_y, maze.cell_size)
    if not maze.is_generated:
        # 迷路がまだ生成されていない場合、指示を表示
        pyxel.text(pyxel.width // 2 - 50, pyxel.height - 10, "Press SPACE to generate maze", 7)
    game.draw()  # タイマーやゲームオーバーの表示

game = Game()
maze = Maze(4, 4)
player = Player(maze.cols - 1, maze.rows - 1)  # プレイヤーの初期位置を右下に設定

pyxel.init(200, 200)
offset_x = (pyxel.width - maze.cols * 8) // 2
offset_y = (pyxel.height - maze.rows * 8) // 2
pyxel.run(update, draw)