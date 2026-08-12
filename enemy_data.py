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
        "health": 5,
        "speed": 3,
        "damage": 25,
        "armor": 0,
        "regen": 0,
        "reward": 25
    },
    "strong": {
        "health": 25,
        "speed": 2,
        "damage": 25,
        "armor": 0,
        "regen": 0,
        "reward": 25
    },
    "boss": {
        "health": 1000,
        "speed": 1,
        "damage": 55,
        "armor": 0,
        "regen": 0.057,
        "reward": 100
    }
}