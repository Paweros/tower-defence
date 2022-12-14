from enum import Enum

from timer import new_timer


class TargetingPriority(Enum):
    First = 1
    Strongest = 2


class TowerType:
    def __init__(self, price, max_range, firing_time, damage, color, base_colour_id, name, targeting_priority):
        self.price = price
        self.max_range = max_range
        self.firing_time = firing_time
        self.damage = damage

        self.colour = color
        self.base_colour_id = base_colour_id
        self.name = name
        self.targeting_priority = targeting_priority


TOWER_GRAY = (100, 100, 100)
TOWER_GREEN = (50, 200, 50)
TOWER_BLUE = (50, 50, 200)
TOWER_RED = (200, 50, 50)

Normal = TowerType(50, 2.5, 60, 25, TOWER_GRAY, 1, "Normal Tower", TargetingPriority.First)
Heavy = TowerType(100, 3, 60, 50, TOWER_RED, 2, "Heavy Tower", TargetingPriority.First)
MachineGun = TowerType(125, 1.5, 5, 5, TOWER_GREEN, 3, "Machine Gun Tower", TargetingPriority.First)
Sniper = TowerType(175, 4.5, 125, 200, TOWER_BLUE, 4, "Sniper Tower", TargetingPriority.Strongest)


class Tower:
    def __init__(self, position, tower_type: TowerType):
        self.max_range = tower_type.max_range
        self.firing_time = tower_type.firing_time
        self.damage = tower_type.damage
        self.targeting_priority = tower_type.targeting_priority

        self.position = list(position)
        self.target = None
        self.firing_timer = new_timer(self.firing_time)
        self.ready_to_shoot = True

        self.colour = tower_type.colour

    def get_target(self, game_state):
        if self.targeting_priority == TargetingPriority.Strongest:
            enemies = sorted(game_state.enemies, key=lambda x: x.health, reverse=True)
        else:
            enemies = game_state.enemies
        for enemy in enemies:
            squared_distance = sum([(enemy.position[i] - self.position[i])**2 for i in range(2)])
            if squared_distance < self.max_range**2:
                self.target = enemy
                return
        else:
            self.target = None

    def shoot(self, game_state):
        game_state.projectiles.append((self.position, self.target.position))
        self.ready_to_shoot = False
        if self.target.damage_check(self.damage):
            self.target.on_death(game_state)
            self.target = None

    def tick(self, game_state):
        self.get_target(game_state)
        if self.ready_to_shoot and self.target is not None and not self.target.is_gone:
            self.shoot(game_state)
        if not self.ready_to_shoot and next(self.firing_timer):
            self.ready_to_shoot = True
