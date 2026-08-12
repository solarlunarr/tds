ENEMY_SPAWN_DATA = [
    {
        #1
        "weak": 15,
        "strong": 0
    },
    {
        #2
        "weak": 30,
        "strong": 5
    },
    {
        #3
        "weak": 30,
        "strong": 10
    },
    {
        #4
        "weak": 30,
        "strong": 25
    },
    {
        #5 - boss level. A handful of escorts, then the boss itself.
        "weak": 15,
        "strong": 15,
        "boss": 1
    }
]



ENEMY_DATA = {
    "weak": {
        "health": 2,
        "speed": 3,
        "damage": 25,   # damage dealt to base health if it reaches the end
        "armor": 0,     # % of incoming damage ignored (0 = none)
        "regen": 0,     # health regenerated per frame (at game_speed 1)
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
        "regen": 0.057,   # slowly heals
        "reward": 100
    }
}