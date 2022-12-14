import pygame

from game_state import GameState
from tower import TowerType, Normal, MachineGun, Sniper, Heavy
from wave import Wave

BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
GRAY = (70, 70, 70)
LIGHT_GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (220, 0, 220)

TOWER_BASE_GRAY = (50, 50, 50)
TOWER_BASE_GREEN = (20, 120, 20)
TOWER_BASE_BLUE = (20, 20, 120)
TOWER_BASE_RED = (120, 20, 20)

COLOR_VALUES_DICT = {-1: WHITE,
                     0: BLACK,
                     1: TOWER_BASE_GRAY,
                     2: TOWER_BASE_RED,
                     3: TOWER_BASE_GREEN,
                     4: TOWER_BASE_BLUE}


class Display:
    def __init__(self, board_width, board_height, tile_pixels, menu_pixels, tower_panel_pixels, counter_pixels):
        self.board_size = self.board_width, self.board_height = board_width, board_height
        self.tile_pixels = tile_pixels
        self.menu_pixels = menu_pixels
        self.tower_panel_pixels = tower_panel_pixels
        self.counter_pixels = counter_pixels

        self.pixels_width = board_width * tile_pixels + menu_pixels + counter_pixels
        self.pixels_height = board_height * tile_pixels
        self.pixels = self.pixels_width, self.pixels_height
        self.screen = pygame.display.set_mode((self.pixels_width, self.pixels_height))

        pygame.display.set_caption('Tower Defence')

        pygame.font.init()
        self.menu_font = pygame.font.SysFont("consolas", 36)
        self.regular_font = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 12)
        self.tiny_font = pygame.font.SysFont("consolas", 10)

    def draw(self, game_state: GameState):
        self.draw_tiles(game_state)
        self.draw_cursor(game_state)
        self.draw_enemies(game_state)
        self.draw_towers(game_state)
        self.draw_tower_range(game_state)
        self.draw_projectiles(game_state)
        self.draw_menu(game_state)
        self.draw_wave_counter(game_state)
        if game_state.paused:
            self.draw_pause()
        pygame.display.flip()

    def draw_tile(self, position, colour):
        pygame.draw.rect(
            self.screen,
            colour,
            (*position, self.tile_pixels,
             self.tile_pixels))

    def draw_tiles(self, game_state: GameState):
        for i in range(self.board_width):
            for j in range(self.board_height):
                tile_colour = COLOR_VALUES_DICT[game_state.map[i][j]]
                self.draw_tile((self.menu_pixels + i * self.tile_pixels, j * self.tile_pixels), tile_colour)

    def draw_cursor(self, game_state: GameState):
        cursor_box = pygame.Rect(
            self.menu_pixels + game_state.cursor[0] * self.tile_pixels,
            game_state.cursor[1] * self.tile_pixels,
            self.tile_pixels,
            self.tile_pixels)
        pygame.draw.rect(self.screen, YELLOW, cursor_box, width=2)

    def draw_enemy(self, position, pixels, colour):
        enemy_box = pygame.Rect(*position, pixels, pixels)
        pygame.draw.rect(self.screen, colour, enemy_box)

    def draw_enemies(self, game_state: GameState):
        for enemy in game_state.enemies:
            self.draw_enemy(
                (self.menu_pixels + enemy.position[0] * self.tile_pixels + (self.tile_pixels - enemy.pixels) / 2,
                 enemy.position[1] * self.tile_pixels + (self.tile_pixels - enemy.pixels) / 2), enemy.pixels,
                tuple(enemy.colour[i] * enemy.health/enemy.max_health for i in range(3)))

    def draw_tower(self, position, color):
        pygame.draw.circle(self.screen,
                           color,
                           position,
                           radius=1 / 4 * self.tile_pixels)

    def draw_towers(self, game_state):
        for tower in game_state.towers:
            self.draw_tower((self.menu_pixels + self.tile_pixels * (tower.position[0] + 1 / 2),
                             self.tile_pixels * (tower.position[1] + 1 / 2)),
                            tower.colour)

    def draw_tower_range(self, game_state: GameState):
        if game_state.selected_tower_type is None:
            return
        pygame.draw.circle(self.screen,
                           YELLOW,
                           (self.menu_pixels + self.tile_pixels * (game_state.cursor[0] + 1/2),
                            self.tile_pixels * (game_state.cursor[1] + 1/2)),
                           radius=game_state.selected_tower_type.max_range * self.tile_pixels,
                           width=2)

    def draw_projectiles(self, game_state: GameState):
        for projectile in game_state.projectiles:
            line_start = (self.menu_pixels + self.tile_pixels * (projectile[0][0] + 1/2),
                          self.tile_pixels * (projectile[0][1] + 1/2))
            line_end = (self.menu_pixels + self.tile_pixels * (projectile[1][0] + 1/2),
                        self.tile_pixels * (projectile[1][1] + 1/2))
            pygame.draw.line(self.screen, YELLOW, line_start, line_end)

    def draw_menu(self, game_state: GameState):
        menu_panel = pygame.Rect(0, 0, self.menu_pixels, self.pixels_height)
        pygame.draw.rect(self.screen, GRAY, menu_panel)

        health_text = self.regular_font.render(f'Health {game_state.health}', True, WHITE)
        gold_text = self.regular_font.render(f'Gold {game_state.gold}', True, WHITE)

        self.screen.blit(health_text, (20, 20))
        self.screen.blit(gold_text, (200, 20))

        for i, tower_type in enumerate([Normal, Heavy, MachineGun, Sniper]):
            self.draw_tower_info((10, 60 + i * self.tower_panel_pixels), i+1, tower_type, game_state)
        self.draw_instructions((10, 70 + 4 * self.tower_panel_pixels))

    def draw_tower_info(self, position, key: int, tower_type: TowerType, game_state: GameState):
        tower_panel = pygame.Rect(*position, self.menu_pixels - 20, self.tower_panel_pixels - 10)

        if tower_type.price > game_state.gold:
            panel_colour = DARK_GRAY
            tower_price_text_colour = LIGHT_GRAY
        else:
            panel_colour = LIGHT_GRAY
            tower_price_text_colour = YELLOW

        pygame.draw.rect(self.screen, panel_colour, tower_panel)
        if tower_type == game_state.selected_tower_type:
            pygame.draw.rect(self.screen, tower_price_text_colour, tower_panel, width=2)

        tower_base_position = (position[0] + 10, position[1] + 10)
        self.draw_tile(tower_base_position, COLOR_VALUES_DICT[tower_type.base_colour_id])

        tower_position = (tower_base_position[0] + self.tile_pixels/2, tower_base_position[1] + self.tile_pixels/2)
        self.draw_tower(tower_position, tower_type.colour)

        name_text = self.regular_font.render(tower_type.name, True, WHITE)
        self.screen.blit(name_text, (position[0] + self.tile_pixels + 20, position[1] + 10))

        price_text = self.regular_font.render(str(tower_type.price), True, tower_price_text_colour)
        self.screen.blit(price_text, (position[0] + self.menu_pixels - 80, position[1] + 10))

        damage_text = self.small_font.render(f"{tower_type.damage} DMG", True, WHITE)
        self.screen.blit(damage_text, (position[0] + self.tile_pixels + 20, position[1] + self.tower_panel_pixels - 30))

        time_text = self.small_font.render(f"{tower_type.firing_time} TIME", True, WHITE)
        self.screen.blit(time_text, (position[0] + self.tile_pixels + 90, position[1] + self.tower_panel_pixels - 30))

        range_text = self.small_font.render(f"{tower_type.max_range} RANGE", True, WHITE)
        self.screen.blit(range_text, (position[0] + self.tile_pixels + 190, position[1] + self.tower_panel_pixels - 30))

        key_panel_position = (position[0] + self.menu_pixels - 45, position[1] + self.tower_panel_pixels - 35)
        key_panel = pygame.Rect(*key_panel_position, 20, 20)
        pygame.draw.rect(self.screen, GRAY, key_panel)

        key_text_position = (key_panel_position[0] + 5, key_panel_position[1])
        key_text = self.regular_font.render(str(key), True, panel_colour)
        self.screen.blit(key_text, key_text_position)

    def draw_instructions(self, position):
        title_text = self.regular_font.render("How to play", True, WHITE)
        self.screen.blit(title_text, (position[0], position[1]))
        instruction_lines = [self.small_font.render("Move around using arrow keys", True, WHITE),
                             self.small_font.render("Press 'P' to pause/unpause", True, WHITE),
                             self.small_font.render("Use 1-4 keys to select a tower type", True, WHITE),
                             self.small_font.render("Press the number again to build a tower", True, WHITE),
                             self.small_font.render("Kill enemies to get more gold", True, WHITE),
                             self.small_font.render("Don't let them reach the exit", True, WHITE),
                             self.small_font.render("You lose if you run out of health!", True, WHITE),
                             self.small_font.render("Finish all the waves to win", True, WHITE)]
        for i, line in enumerate(instruction_lines):
            self.screen.blit(line, (position[0], position[1] + 20 * (i+2)))

    def draw_wave_counter(self, game_state: GameState):
        counter_panel = pygame.Rect(self.pixels_width - self.counter_pixels, 0, self.counter_pixels, 50)
        pygame.draw.rect(self.screen, GRAY, counter_panel)

        current_wave = game_state.current_wave_id + 1
        total_waves = len(game_state.waves)
        wave_counter_text = self.regular_font.render(f"Wave {current_wave}/{total_waves}", True, WHITE)
        self.screen.blit(wave_counter_text, (self.pixels_width - self.counter_pixels + 5, 10))

        remaining_enemies = game_state.current_wave.total_amount + len(game_state.enemies) - \
            game_state.current_wave.current_amount
        total_enemies = game_state.current_wave.total_amount
        enemy_counter_text = self.small_font.render(f"{remaining_enemies}/{total_enemies} enemies", True, WHITE)
        self.screen.blit(enemy_counter_text, (self.pixels_width - self.counter_pixels + 5, 32))
        right_panel = pygame.Rect(self.pixels_width - self.counter_pixels, 50,
                                  self.counter_pixels, self.pixels_height - 50)
        pygame.draw.rect(self.screen, DARK_GRAY, right_panel)
        for i, wave in enumerate(game_state.waves[game_state.current_wave_id: game_state.current_wave_id + 5]):
            self.draw_wave_info((self.pixels_width - self.counter_pixels, (i + 1) * 60),
                                game_state.current_wave_id + i + 1, wave, game_state)

    def draw_wave_info(self, position, number, wave: Wave, game_state: GameState):
        if wave == game_state.current_wave:
            panel_colour = LIGHT_GRAY
        else:
            panel_colour = GRAY

        info_panel = pygame.Rect(*position, self.counter_pixels, 50)
        pygame.draw.rect(self.screen, panel_colour, info_panel)

        wave_name_text = self.small_font.render(f"Wave {number}: {wave.enemy_type.name} x{wave.total_amount}",
                                                True, WHITE)
        wave_name_text_rect = wave_name_text.get_rect(centerx=info_panel.centerx + 10, centery=info_panel.centery-10)
        self.screen.blit(wave_name_text, wave_name_text_rect)

        if wave.batch_amount == 0:
            self.draw_enemy((position[0] + 10, position[1] + 10), wave.enemy_type.pixels, wave.enemy_type.colour)
        else:
            for i in range(wave.batch_amount):
                enemy_position = (position[0] + 5 + 2 * i, position[1] + 10 + 2 * i * (2 * (i % 2) - 1))
                self.draw_enemy(enemy_position, wave.enemy_type.pixels, wave.enemy_type.colour)

        health_text = self.tiny_font.render(f"{wave.enemy_type.health} HP", True, WHITE)
        self.screen.blit(health_text, (position[0] + 10, position[1] + 30))

        speed_text = self.tiny_font.render(f"{wave.enemy_type.speed} SPD", True, WHITE)
        self.screen.blit(speed_text, (position[0] + 50, position[1] + 30))

        reward_text = self.tiny_font.render(f"{wave.enemy_type.reward} GOLD", True, WHITE)
        self.screen.blit(reward_text, (position[0] + 110, position[1] + 30))

    def draw_pause(self):
        pause_text1 = self.menu_font.render("Game is paused", True, PURPLE)
        pause_text2 = self.menu_font.render("press 'P' to unpause", True, PURPLE)
        pause_text1_center = ((self.menu_pixels + self.pixels_width - self.counter_pixels)/ 2,
                              self.pixels_height / 2 - 30)
        pause_text2_center = ((self.menu_pixels + self.pixels_width - self.counter_pixels)/ 2,
                              self.pixels_height / 2 + 30)
        pause_text1_rect = pause_text1.get_rect(center=pause_text1_center)
        pause_text2_rect = pause_text2.get_rect(center=pause_text2_center)
        self.screen.blit(pause_text1, pause_text1_rect)
        self.screen.blit(pause_text2, pause_text2_rect)
        pygame.display.flip()

    def draw_win(self):
        self.screen.fill(GRAY)
        win_text = self.menu_font.render("You win! Congratulations!", True, WHITE)
        win_text_rect = win_text.get_rect(center=(self.pixels_width / 2, self.pixels_height / 2))
        self.screen.blit(win_text, win_text_rect)
        pygame.display.flip()

    def draw_loss(self):
        self.screen.fill(GRAY)
        loss_text = self.menu_font.render("You lose :c Better luck next time!", True, WHITE)
        loss_text_rect = loss_text.get_rect(center=(self.pixels_width / 2, self.pixels_height / 2))
        self.screen.blit(loss_text, loss_text_rect)
        pygame.display.flip()
