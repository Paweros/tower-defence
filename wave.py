from enemy import EnemyType
from timer import new_timer


class Wave:
    def __init__(self, spawn_time, enemy_type: EnemyType, total_amount, spawn_subtime, batch_amount):
        self.spawn_time = spawn_time
        self.enemy_type = enemy_type
        self.current_amount = 0
        self.total_amount = total_amount

        self.spawn_subtime = spawn_subtime
        self.batch_amount = batch_amount
        self.current_batch_amount = 0
        self.inside_batch = False

        self.spawn_timer = new_timer(self.spawn_time)
        if spawn_subtime != 0:
            self.spawn_subtimer = new_timer(self.spawn_subtime)

    def enemy_to_spawn(self):
        while self.current_amount < self.total_amount:
            if self.inside_batch:
                while self.current_batch_amount < self.batch_amount:
                    if next(self.spawn_subtimer):
                        self.current_batch_amount += 1
                        self.current_amount += 1
                        yield self.enemy_type
                self.current_batch_amount = 0
                self.inside_batch = False
            elif next(self.spawn_timer):
                if self.spawn_subtime == 0:
                    self.current_amount += 1
                    yield self.enemy_type
                else:
                    self.inside_batch = True
            yield None
        yield None


PURPLE = (220, 0, 220)
GREEN = (80, 220, 80)
RED = (220, 40, 40)
BLUE = (40, 40, 220)
ORANGE = (220, 120, 20)

Regular = EnemyType("Regular", 0.1, 1, 25, 4, 10, PURPLE)
Tough = EnemyType("Tough", 0.1, 1, 50, 6, 10, RED)
Fast = EnemyType("Fast", 0.15, 1, 30, 6, 8, GREEN)
Tougher = EnemyType("Tougher", 0.07, 2, 200, 12, 15, RED)
RegularPlus = EnemyType("Regular+", 0.12, 1, 45, 10, 11, ORANGE)
Boss = EnemyType("Boss", 0.04, 20, 4500, 20, 20, BLUE)

DEFAULT_WAVES = [
    Wave(50, Regular, 20, 0, 1),
    Wave(25, Regular, 20, 0, 1),
    Wave(25, Tough, 25, 0, 1),
    Wave(20, Fast, 30, 0, 1),
    Wave(40, Regular, 60, 1, 3),
    Wave(30, Tougher, 20, 0, 1),
    Wave(45, Fast, 30, 1, 5),
    Wave(10, RegularPlus, 30, 0, 1),
    Wave(45, Tougher, 30, 1, 3),
    Wave(1, Boss, 1, 0, 1)]

TEST_WAVES = [Wave(20, Fast, 18, 1, 20),
              Wave(1, Boss, 1, 0, 1)]