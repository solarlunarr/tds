ENEMY_SPAWN_DATA = [
    {
        # Level 1
        "weak": 15,
        "strong": 0
    },
    {
        # Level 2
        "weak": 30,
        "strong": 5
    },
    {
        # Level 3
        "weak": 30,
        "strong": 10
    },
    {
        # Level 4
        "weak": 30,
        "strong": 25
    },
    {
        # Level 5 - Final Boss Level
        "weak": 15,
        "strong": 15,
        "boss": 1
    }
]

ENEMY_DATA = {
    "weak": {
        "health": 2,
        "speed": 3,
        "damage": 25,
        "armor": 0,
        "regen": 0,
        "reward": 25
    },
    "strong": {
        "health": 5,
        "speed": 2,
        "damage": 25,
        "armor": 0,
        "regen": 0,
        "reward": 25
    },
    "boss": {
        "health": 30,
        "speed": 1,
        "damage": 55,
        "armor": 0,
        "regen": 0.057,
        "reward": 100
    }
}