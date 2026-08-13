ENEMY_SPAWN_DATA = [
    {
        # Level 1
        "weak": 10,
        "strong": 0
    },
    {
        # Level 2
        "weak": 10,
        "strong": 5
    },
    {
        # Level 3
        "weak": 20,
        "strong": 10
    },
    {
        # Level 4
        "weak": 20,
        "strong": 25
    },
    {
        # Level 5 - Final Boss Level
        "weak": 30,
        "strong": 30,
        "boss": 1
    }
]

ENEMY_DATA = {
    "weak": {
        "health": 20,
        "speed": 2.8,
        "damage": 10,
        "armor": 0,
        "regen": 0,
        "reward": 25
    },
    "strong": {
        "health": 65,
        "speed": 2,
        "damage": 20,
        "armor": 0.10,
        "regen": 0,
        "reward": 55
    },
    "boss": {
        "health": 1000000,
        "speed": 1,
        "damage": 100,
        "armor": 0.25,
        "regen": 0.10,
        "reward": 2500
    }
}