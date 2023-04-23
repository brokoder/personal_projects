"""
Created a 2048 game with pygame and pandas. 

w - > up
a - > left
s - > down
d - > right
r -> return to the previous position
"""


import pygame
import pandas as pd
import random
# initial set up
WIDTH = 400
HEIGHT = 500

class GameDimensions:
    WIDTH = 95
    HEIGHT = 95
    PADDING = 20
    INNER_WIDTH = 75
    INNER_HEIGHT = 75
    INNER_CIRCLE_RADIUS = 0
    CORNER_RADIUS = 5
    TEXT_LEFT_SHIFT = 57 
    TEXT_TOP_SHIFT= 57
    BORDER_THICKNESS= 2
    BORDER_RADIUS = 5


# 2048 game color library
colors = {0: (204, 192, 179),
            2: (238, 228, 218),
            4: (237, 224, 200),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46),
            'light text': (249, 246, 242),
            'dark text': (119, 110, 101),
            'other': (0, 0, 0),
            'bg': (187, 173, 160)}

class Py2048:
    def __init__(self) -> None:
        self.score = 0
        self.over = False
        self.high_score = 0
        self.run = True
    
    def initialize_pygame(self):
        pygame.init()
        pygame.display.set_caption('2048')
        self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        self.timer = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.Font('freesansbold.ttf', 24)
    
    def create_new_board(self):
        self.board_df = pd.DataFrame(0, index=range(4), columns=range(4))
        self.previous_df = self.board_df.copy()
        self.score = 0
        self.score_increase = 0
        self.over = False

    def draw_board(self):
        self.screen.fill('gray')
        pygame.draw.rect(self.screen, colors['bg'], [0, 0, 400, 400], 0, 10)
        score_text = self.font.render(f'Score: {self.score}', True, 'black')
        high_score_text = self.font.render(f'High Score: {self.high_score}', True, 'black')
        self.screen.blit(score_text, (10, 410))
        self.screen.blit(high_score_text, (10, 450))

    def game_over_popup(self):
        pygame.draw.rect(self.screen, 'black', [50, 50, 300, 100], 0, 10)
        game_over_text1 = self.font.render('Game Over!', True, 'white')
        game_over_text2 = self.font.render('Press Enter to Restart', True, 'white')
        self.screen.blit(game_over_text1, (130, 65))
        self.screen.blit(game_over_text2, (70, 105))
    
    def draw_pieces(self):
        tra_df = self.board_df.T
        for col in tra_df:
            for row, value in tra_df[col].items():
                value_color = colors['light text'] if value > 8 else colors['dark text']
                color = colors[value] if colors.get(value) else colors['other']
                pygame.draw.rect(self.screen, color, [row * GameDimensions.WIDTH + GameDimensions.PADDING, col *GameDimensions.HEIGHT + GameDimensions.PADDING, GameDimensions.INNER_WIDTH, GameDimensions.INNER_HEIGHT], GameDimensions.INNER_CIRCLE_RADIUS, GameDimensions.CORNER_RADIUS)
                if value > 0:
                    value_len = len(str(value))
                    font = pygame.font.Font('freesansbold.ttf', 48 - (5 * value_len))
                    value_text = font.render(str(value), True, value_color)
                    text_rect = value_text.get_rect(center=(row * GameDimensions.HEIGHT + GameDimensions.TEXT_LEFT_SHIFT, col * GameDimensions.WIDTH + 57))
                    self.screen.blit(value_text, text_rect)
                    pygame.draw.rect(self.screen, 'black', [row * GameDimensions.HEIGHT + GameDimensions.PADDING, col *  GameDimensions.WIDTH + GameDimensions.PADDING, GameDimensions.INNER_WIDTH, GameDimensions.INNER_HEIGHT], GameDimensions.BORDER_THICKNESS, GameDimensions.BORDER_RADIUS)
    @staticmethod
    def turn_logic(cell_values):
        temp_list =  [i for i in cell_values if i !=0]
        cell_values = temp_list + [0]*(4-len(temp_list))
        score = 0
        if cell_values[0] == cell_values[1] and cell_values[2] == cell_values[3]:# [2,2,4,4] - > [4,8,0,0], [2,2,2,2] - > [4,4,0,0]
            cell_values = [cell_values[0]*2,cell_values[2]*2, 0, 0]
            score = score + cell_values[0] + cell_values[2]
        elif cell_values[0] == cell_values[1] and cell_values[2] != cell_values[3]:# [2,2,4,8] - > [4,4,8,0] , [2,2,2,8] - > [4,2,8,0] 
            cell_values = [cell_values[0]*2,cell_values[2],cell_values[3], 0]
            score = score + cell_values[0]
        elif cell_values[0] != cell_values[1] and cell_values[1] == cell_values[2]:# [2,4,4,8] - > [2,8,8,0], [2,4,4,4] - > [2,8,4,0]
            cell_values = [cell_values[0],cell_values[1]*2,cell_values[3], 0]
            score = score + cell_values[1]
        elif cell_values[0] != cell_values[1] and cell_values[2] == cell_values[3]:# [2,4,8,8] - > [2,4,16,0]
            cell_values = [cell_values[0],cell_values[1],cell_values[2]*2, 0]
            score = score + cell_values[2]
        return cell_values, score

    def turn_up(self):
        self.score_increase = 0
        for col in self.board_df:
            cell_values = self.board_df[col].to_list()
            self.board_df[col], score_increase = self.turn_logic(cell_values)
            self.score_increase += score_increase
        if self.board_df.equals(self.previous_df):# no change 
            return self.check_if_no_moves_present(self.board_df)
        self.score += self.score_increase
        return True

    def turn_down(self):
        self.score_increase = 0
        for col in self.board_df:
            cell_values = self.board_df[col].to_list()
            cell_values.reverse()
            cell_values, score_increase  = self.turn_logic(cell_values)
            cell_values.reverse()
            self.board_df[col] = cell_values
            self.score_increase += score_increase
        if self.board_df.equals(self.previous_df):# no change 
            return self.check_if_no_moves_present(self.board_df)
        self.score += self.score_increase
        return True

    def turn_left(self):
        self.score_increase = 0
        for row, val in self.board_df.iterrows():
            cell_values = val.to_list()
            self.board_df.loc[row], score_increase  = self.turn_logic(cell_values)
            self.score_increase += score_increase
        if self.board_df.equals(self.previous_df):# no change 
            return self.check_if_no_moves_present(self.board_df)
        self.score += self.score_increase
        return True

    def turn_right(self):
        self.score_increase = 0
        for row, val in self.board_df.iterrows():
            cell_values = val.to_list()
            cell_values.reverse()
            cell_values,score_increase  = self.turn_logic(cell_values)
            cell_values.reverse()
            self.board_df.loc[row] = cell_values
            self.score_increase += score_increase
        if self.board_df.equals(self.previous_df):# no change 
            return self.check_if_no_moves_present(self.board_df)
        self.score += self.score_increase
        return True

    @staticmethod
    def get_zero_indexes(board_df:pd.DataFrame):
        _index_list: list[tuple[int,int]] = []
        for col in board_df:
            for row, val in board_df[col].items():
                if val == 0:
                    _index_list.append((col,row))
        return _index_list

    @staticmethod
    def check_if_no_moves_present(board_df:pd.DataFrame):
        for col in board_df:
            for row, val in board_df[col].items():
                if col > 0: #left
                    if board_df[col][row] == board_df[col-1][row]:
                        return False
                if col < 3: #right
                    if board_df[col][row] == board_df[col+1][row]:
                        return False
                if row > 0: #up
                    if board_df[col][row] == board_df[col][row-1]:
                        return False
                if row < 3: #down
                    if board_df[col][row] == board_df[col][row+1]:
                        return False
        return True

    def set_new_pieces(self, count=1) ->bool:
        index_list = self.get_zero_indexes(self.board_df)
        if not index_list:
            return False
        for _ in range(count):
            col,row = random.choice(index_list)
            self.board_df[col][row] = 4 if random.randint(1, 10) == 10 else 2
        if not self.get_zero_indexes(self.board_df):
            return self.check_if_no_moves_present(self.board_df)
        return False

def main():
    game = Py2048()
    game.initialize_pygame()
    game_start = True
    game.create_new_board()
    while game.run:
        game.timer.tick(game.fps)
        if not game.over:
            game.draw_board()
        if game_start:
            game.set_new_pieces(2)
            game_start = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    game.board_df = game.previous_df
                    game.score = game.score - game.score_increase
                if event.key == pygame.K_w:
                    game.previous_df = game.board_df.copy()
                    is_change = game.turn_up()
                    if is_change:
                        game.over = game.set_new_pieces()
                elif event.key == pygame.K_s:
                    game.previous_df = game.board_df.copy()
                    is_change = game.turn_down()
                    if is_change:
                        game.over = game.set_new_pieces()
                elif event.key == pygame.K_a:
                    game.previous_df = game.board_df.copy()
                    is_change = game.turn_left()
                    if is_change:
                        game.over = game.set_new_pieces()
                elif event.key == pygame.K_d:
                    game.previous_df = game.board_df.copy()
                    is_change = game.turn_right()
                    if is_change:
                        game.over = game.set_new_pieces()
                elif event.key == pygame.K_ESCAPE:
                    game.over = True
                if game.over:
                    game.game_over_popup()
                    if event.key == pygame.K_RETURN:
                        game.create_new_board()
                        game.draw_board()
                        game_start = True
                    if event.key == pygame.K_r:
                        game.board_df = game.previous_df
                        game.score = game.score - game.score_increase
                        game.over = False
        if not game.over:
            game.draw_pieces()
        if game.score > game.high_score:
            game.high_score = game.score
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()