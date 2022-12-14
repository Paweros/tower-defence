import pygame

from display import Display
from game_state import GameState
from tower import Normal, MachineGun, Sniper, Heavy
from wave import DEFAULT_WAVES, TEST_WAVES

MOVEMENT_TILES_DICT = {pygame.K_UP: [0, -1], pygame.K_DOWN: [0, 1], pygame.K_LEFT: [-1, 0], pygame.K_RIGHT: [1, 0]}
VALUE_TOWER_DICT = {pygame.K_1: Normal,
                    pygame.K_2: Heavy,
                    pygame.K_3: MachineGun,
                    pygame.K_4: Sniper}

PATH = [[3, -1], [3, 0], [3, 1], [3, 2], [3, 3], [4, 3], [5, 3], [6, 3], [7, 3], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7],
        [8, 8], [7, 8], [6, 8], [6, 9], [6, 10], [6, 11], [6, 12]]


class App:
    def __init__(self, width, height, path, waves, tile_pixels, menu_pixels,
                 tower_panel_pixels, counter_pixels, health, gold):
        self.running = True
        self.display = Display(width, height, tile_pixels, menu_pixels, tower_panel_pixels, counter_pixels)
        self.game_state = GameState(width, height, path, waves, health, gold)

    @staticmethod
    def on_init():
        pygame.init()

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in MOVEMENT_TILES_DICT.keys():
                self.game_state.cursor_move(MOVEMENT_TILES_DICT[event.key])
            elif event.key in VALUE_TOWER_DICT.keys():
                if self.game_state.selected_tower_type == VALUE_TOWER_DICT[event.key]:
                    self.game_state.buy_tower()
                else:
                    self.game_state.selected_tower_type = VALUE_TOWER_DICT[event.key]
            elif event.key == pygame.K_p:
                self.game_state.paused = not self.game_state.paused
        if event.type == pygame.QUIT:
            pygame.quit()

    def on_loop(self):
        if not self.game_state.paused:
            self.game_state.move_enemies()
            self.game_state.tick_towers()
            self.game_state.tick_wave()

    def on_render(self):
        self.display.draw(self.game_state)

    def on_cleanup(self):
        if self.game_state.game_won:
            self.display.draw_win()
        else:
            self.display.draw_loss()

    def on_execute(self):
        self.on_init()
        clock = pygame.time.Clock()
        while self.game_state.running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            clock.tick(30)
        self.on_cleanup()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()


if __name__ == "__main__":
    app = App(12, 12, PATH, DEFAULT_WAVES, 50, 400, 80, 160, 20, 150)
    app.on_execute()
