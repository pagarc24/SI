#clase con las constantes del agente
class AgentConsts:
    #inputs
    NEIGHBORHOOD_UP = 0
    NEIGHBORHOOD_DOWN = 1 
    NEIGHBORHOOD_RIGHT = 2
    NEIGHBORHOOD_LEFT = 3
    NEIGHBORHOOD_DIST_UP = 4 
    NEIGHBORHOOD_DIST_DOWN = 5
    NEIGHBORHOOD_DIST_RIGHT = 6
    NEIGHBORHOOD_DIST_LEFT = 7
    PLAYER_X = 8
    PLAYER_Y = 9
    COMMAND_CENTER_X = 10
    COMMAND_CENTER_Y = 11
    AGENT_X = 12
    AGENT_Y = 13
    CAN_FIRE = 14
    HEALTH = 15
    LIFE_X = 16
    LIFE_Y = 17
    TIME = 18

    #movimientos
    NO_MOVE = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_RIGHT = 3
    MOVE_LEFT = 4

    #map y valores de la percepción.
    NOTHING = 0
    UNBREAKABLE = 1
    BRICK = 2
    COMMAND_CENTER = 3
    PLAYER = 4
    SHELL = 5 
    OTHER = 6
    LIFE = 7
    SEMI_BREKABLE = 8
    SEMI_UNBREKABLE = 9