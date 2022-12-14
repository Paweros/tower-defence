import math

from numpy.random import default_rng


class EnemyType:
    def __init__(self, name, speed, damage, health, reward, pixels, colour):
        self.name = name
        self.speed = speed
        self.damage = damage
        self.health = health
        self.reward = reward
        self.pixels = pixels
        self.colour = colour


class Enemy:
    def __init__(self, position, enemy_type: EnemyType):
        rng = default_rng()
        self.offset = [rng.uniform(-0.2, 0.2) for _ in range(2)]
        self.position = list(position)

        self.speed = enemy_type.speed
        self.damage = enemy_type.damage
        self.max_health = enemy_type.health
        self.health = enemy_type.health
        self.reward = enemy_type.reward

        self.pixels = enemy_type.pixels
        self.colour = enemy_type.colour

        self.node_at = 0
        self.is_gone = False

    def move_to(self, destination):
        effective_destination = [destination[i]+self.offset[i] for i in range(2)]
        difference_vector = [effective_destination[i]-self.position[i] for i in range(2)]
        norm = math.sqrt(sum([i ** 2 for i in difference_vector]))
        move_delta = [difference_vector[i] / norm * self.speed for i in range(2)]
        if norm < self.speed:
            self.node_at += 1
        self.position[0] += move_delta[0]
        self.position[1] += move_delta[1]

    def on_death(self, game_state):
        game_state.gold += self.reward
        game_state.enemies.remove(self)
        self.is_gone = True

    def on_pass(self, game_state):
        game_state.take_damage(self.damage)
        game_state.enemies.remove(self)
        self.is_gone = True

    def damage_check(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True
        return False
