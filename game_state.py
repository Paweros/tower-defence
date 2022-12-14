from typing import Union

from enemy import Enemy, EnemyType
from tower import TowerType, Tower


class GameState:
    def __init__(self, width, height, path, waves, health, gold):
        self.game_won = False
        self.running = True
        self.paused = True

        self.width = width
        self.height = height

        self.path = path
        self.map = [[-1 if [i, j] in self.path else 0 for j in range(self.height)] for i in range(self.width)]

        self.waves = waves
        self.current_wave_id = 0
        self.current_wave = waves[0]
        self.enemies = list()

        self.health = health
        self.gold = gold
        self.cursor = [width//2, height//2]
        self.selected_tower_type: Union[TowerType, None] = None
        self.towers = list()
        self.projectiles = list()

    def cursor_move(self, vector):
        self.cursor[0] = (self.cursor[0] + vector[0]) % self.width
        self.cursor[1] = (self.cursor[1] + vector[1]) % self.height

    def set_tile(self, value):
        if self.map[self.cursor[1]][self.cursor[0]] < 0:
            return
        self.map[self.cursor[1]][self.cursor[0]] = value

    def take_damage(self, value):
        self.health -= value
        if self.health <= 0:
            self.on_lose()

    def on_lose(self):
        self.running = False

    def on_win(self):
        self.game_won = True
        self.running = False

    def spawn_enemy(self, enemy_type: EnemyType):
        self.enemies.append(Enemy([self.path[0][0], self.path[0][1]], enemy_type))
        pass

    def move_enemies(self):
        enemies_to_delete = list()
        for enemy in self.enemies:
            if enemy.node_at == len(self.path) - 1:
                enemies_to_delete.append(enemy)
            else:
                enemy.move_to(self.path[enemy.node_at + 1])
        for enemy in enemies_to_delete:
            enemy.on_pass(self)

    def tick_wave(self):
        tick_result = next(self.current_wave.enemy_to_spawn())
        if tick_result is not None:
            self.spawn_enemy(tick_result)
        if self.current_wave.current_amount == self.current_wave.total_amount and len(self.enemies) == 0:
            if self.current_wave_id == len(self.waves) - 1:
                if self.running:
                    self.on_win()
                return
            else:
                self.current_wave_id += 1
                self.current_wave = self.waves[self.current_wave_id]

    def buy_tower(self):
        if self.map[self.cursor[0]][self.cursor[1]] != 0 or self.gold < self.selected_tower_type.price:
            return
        self.gold -= self.selected_tower_type.price
        self.towers.append(Tower((self.cursor[0], self.cursor[1]), self.selected_tower_type))
        self.map[self.cursor[0]][self.cursor[1]] = self.selected_tower_type.base_colour_id
        self.selected_tower_type = None

    def tick_towers(self):
        self.projectiles.clear()
        for tower in self.towers:
            tower.tick(self)
