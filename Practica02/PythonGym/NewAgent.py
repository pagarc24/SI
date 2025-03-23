import random
import time
from enum import Enum
from BaseAgent import BaseAgent

# ─────────────────────────────────────────────────────────
# Ajusta estos valores a tu entorno real de Battle City
# ─────────────────────────────────────────────────────────
NOTHING   = 0
MOVE_UP   = 1
MOVE_DOWN = 2
MOVE_RIGHT= 3
MOVE_LEFT = 4

NOTHING_OBJ = 0
UNBREAKABLE = 1
BRICK = 2
COMMAND_CENTER = 3
PLAYER = 4
SHELL = 5
OTHER = 6

# Objetos disparables
SHOOTABLE = {BRICK, COMMAND_CENTER, PLAYER, OTHER}

class AgentState(Enum):
    MOVE_RANDOM = 0  # El agente no tiene amenaza ni objetivo inmediato: se mueve aleatoriamente
    SHOOT_SHELL = 1  # Hay una bala cerca y podemos dispararla
    EVADE_SHELL = 2  # Hay una bala cerca, pero no podemos disparar => nos movemos en dirección opuesta
    SHOOT_TARGET = 3  # Queremos disparar a tanque / ladrillo / command center

class PerryElOrnitorrinco(BaseAgent):
    def __init__(self, agent_id, name):
        super().__init__(agent_id, name)
        self.state = AgentState.MOVE_RANDOM  # Estado inicial

        # Control interno para el movimiento aleatorio
        self.last_move_time = time.time()
        self.move_delay = 2.0
        self.current_action = random.randint(1, 4)  # 1..4 => UP, DOWN, RIGHT, LEFT

    def Start(self):
        print(f"[{self.name}] Agente iniciado. Estado = {self.state}")

    def Update(self, perception):
        """
        Perception (16 floats):
         [0..3] : objetos en [UP, DOWN, RIGHT, LEFT]
         [4..7] : distancias
         [8..11]: player_x, player_y, base_x, base_y
         [12..15]: agent_x, agent_y, can_fire(1/0), health
        """
        # ────────────── Parseo de la percepción ──────────────
        obj_up, obj_down, obj_right, obj_left = map(int, perception[0:4])
        dist_up, dist_down, dist_right, dist_left = perception[4:8]
        player_x, player_y, base_x, base_y = perception[8:12]
        agent_x, agent_y, can_fire, health = perception[12:16]

        # 1) Detectar si hay una bala cerca (dist < 3), y en qué dirección
        bullet_dir = self._shell_near(
            obj_up, dist_up, obj_down, dist_down,
            obj_right, dist_right, obj_left, dist_left
        )

        # 2) Detectar si hay un “objetivo disparable” en frente o alineado
        #    (tanques, ladrillos o command center)
        target_in_front = self._target_in_front(
            self.current_action, obj_up, obj_down, obj_right, obj_left
        )
        alignment_target = self._alignment_target(agent_x, agent_y, base_x, base_y, player_x, player_y,
                                                  obj_up, obj_down, obj_right, obj_left)

        # ───────────────────── Lógica de transiciones de estado ─────────────────────
        new_state = self.state  # Por defecto mantenemos el estado

        if bullet_dir is not None:
            # Hay bala cerca
            if can_fire >= 1.0:
                # Podemos disparar la bala => pasa a SHOOT_SHELL
                new_state = AgentState.SHOOT_SHELL
            else:
                # No podemos disparar => EVADIR
                new_state = AgentState.EVADE_SHELL
        else:
            # No hay bala cerca => si hay un objetivo disparable, pasa a SHOOT_TARGET
            # "Objetivo disparable" => en frente o alineado
            if can_fire >= 1.0 and (target_in_front or alignment_target):
                new_state = AgentState.SHOOT_TARGET
            else:
                # No hay bala ni objetivo disparable => moverse
                new_state = AgentState.MOVE_RANDOM

        if new_state != self.state:
            print(f"[{self.name}] Cambio de estado: {self.state} -> {new_state}")
            self.state = new_state

        # ───────────────────── Comportamiento según el estado ─────────────────────
        if self.state == AgentState.SHOOT_SHELL:
            return self._handle_shoot_shell()
        elif self.state == AgentState.EVADE_SHELL:
            return self._handle_evade_shell(bullet_dir)
        elif self.state == AgentState.SHOOT_TARGET:
            return self._handle_shoot_target(
                self.current_action, obj_up, obj_down, obj_right, obj_left, can_fire
            )
        else:  # MOVE_RANDOM
            return self._handle_move_random(
                self.current_action, obj_up, obj_down, obj_right, obj_left, can_fire
            )

    def End(self, win):
        print(f"[{self.name}] Fin de la partida. ¿Victoria? {win}")

    # ─────────────────────────────────────────────────────────────────
    #                    MANEJADORES DE ESTADO
    # ─────────────────────────────────────────────────────────────────

    def _handle_shoot_shell(self):
        """
        Estado SHOOT_SHELL:
          Si detectamos una bala y podemos dispararla,
          nos quedamos quietos y disparamos (NOTHING, True)
        """
        # Simplemente disparamos sin movernos
        return (NOTHING, True)

    def _handle_evade_shell(self, bullet_dir):
        """
        Estado EVADE_SHELL:
          - Recibe la dirección de la bala.
          - Nos movemos a la dirección opuesta (o la que elijas).
        """
        # bullet_dir es 'UP', 'DOWN', 'RIGHT' o 'LEFT'.
        if bullet_dir == 'UP':
            return (MOVE_DOWN, False)
        if bullet_dir == 'DOWN':
            return (MOVE_UP, False)
        if bullet_dir == 'RIGHT':
            return (MOVE_LEFT, False)
        if bullet_dir == 'LEFT':
            return (MOVE_RIGHT, False)
        # Por si algo falla:
        return (self.current_action, False)

    def _handle_shoot_target(self, action, obj_up, obj_down, obj_right, obj_left, can_fire):
        """
        Estado SHOOT_TARGET:
          Disparamos a tanques, ladrillos o Command Center en frente o alineados.
          Por simplicidad, si el objeto de frente es disparable, disparamos quedándonos quietos.
        """
        front_obj = self._obj_in_front(action, obj_up, obj_down, obj_right, obj_left)
        if front_obj in SHOOTABLE and can_fire >= 1.0:
            # Disparamos quedándonos quietos o, si prefieres, avanzar y disparar.
            return (NOTHING, True)

        # Si no podemos disparar o no hay un objeto disparable inmediato, no pasa nada
        # Volvemos a la acción actual sin disparar
        return (action, False)

    def _handle_move_random(self, action, obj_up, obj_down, obj_right, obj_left, can_fire):
        """
        Estado MOVE_RANDOM:
         - Cada 'move_delay' segundos se elige una nueva dirección aleatoria.
         - Si la dirección está bloqueada por un objeto disparable (BRICK, PLAYER, OTHER, CC) y can_fire, disparamos.
         - Si está bloqueada por UNBREAKABLE, cambiamos de dirección.
        """
        current_time = time.time()
        if current_time - self.last_move_time > self.move_delay:
            self.current_action = random.randint(1, 4)
            self.last_move_time = current_time

        action = self.current_action
        front_obj = self._obj_in_front(action, obj_up, obj_down, obj_right, obj_left)

        if front_obj != NOTHING_OBJ:
            if front_obj in SHOOTABLE:
                # Disparamos si podemos
                if can_fire >= 1.0:
                    return (action, True)
                # Si no podemos disparar, seguimos en la misma dirección (o cambias aleatoriamente, a tu gusto)
            else:
                # Si es UNBREAKABLE u otro no disparable => cambiar dirección
                self.current_action = random.randint(1, 4)
                action = self.current_action

        return (action, False)

    # ─────────────────────────────────────────────────────────────────
    #                    FUNCIONES DE UTILIDAD
    # ─────────────────────────────────────────────────────────────────

    def _shell_near(self, obj_up, dist_up, obj_down, dist_down, obj_right, dist_right, obj_left, dist_left):
        """
        Devuelve la dirección en la que hay una bala (SHELL) muy cerca (<3).
        Si no hay bala cerca, retorna None.
        """
        if obj_up == SHELL and dist_up < 20:
            return 'UP'
        if obj_down == SHELL and dist_down < 20:
            return 'DOWN'
        if obj_right == SHELL and dist_right < 20:
            return 'RIGHT'
        if obj_left == SHELL and dist_left < 20:
            return 'LEFT'
        return None

    def _obj_in_front(self, action, obj_up, obj_down, obj_right, obj_left):
        """Devuelve el objeto que está 'en frente' según la acción actual."""
        if action == MOVE_UP:
            return obj_up
        elif action == MOVE_DOWN:
            return obj_down
        elif action == MOVE_RIGHT:
            return obj_right
        elif action == MOVE_LEFT:
            return obj_left
        return NOTHING_OBJ

    def _target_in_front(self, action, obj_up, obj_down, obj_right, obj_left):
        """
        Retorna True si el objeto de frente es disparable
        (tanque, ladrillo o command center).
        """
        front_obj = self._obj_in_front(action, obj_up, obj_down, obj_right, obj_left)
        return (front_obj in SHOOTABLE)

    def _alignment_target(self, agent_x, agent_y, base_x, base_y, player_x, player_y,
                          obj_up, obj_down, obj_right, obj_left):
        """
        Retorna True si el player o la base están en la misma fila/columna,
        y la celda inmediata en esa dirección es SHOOTABLE.
        Simplificado: con un umbral <1.0 y no sea UNBREAKABLE.
        """
        # Chequeamos si hay "alineación" con el player/base
        same_row_player = (abs(agent_y - player_y) < 1.0)
        same_col_player = (abs(agent_x - player_x) < 1.0)
        same_row_base   = (abs(agent_y - base_y) < 1.0)
        same_col_base   = (abs(agent_x - base_x) < 1.0)

        # Si player/base está a la izquierda, derecha, arriba o abajo,
        # vemos si la celda inmediata en esa dirección es SHOOTABLE
        # (p.ej., si tenemos ladrillos cubriendo, también es disparable).
        # Esto es una simplificación. En un juego real, quizá harías un raycast.

        # Jugador en la misma fila
        if same_row_player:
            if player_x < agent_x and obj_left in SHOOTABLE:
                return True
            if player_x > agent_x and obj_right in SHOOTABLE:
                return True

        # Jugador en la misma columna
        if same_col_player:
            if player_y < agent_y and obj_up in SHOOTABLE:
                return True
            if player_y > agent_y and obj_down in SHOOTABLE:
                return True

        # Base en la misma fila
        if same_row_base:
            if base_x < agent_x and obj_left in SHOOTABLE:
                return True
            if base_x > agent_x and obj_right in SHOOTABLE:
                return True

        # Base en la misma columna
        if same_col_base:
            if base_y < agent_y and obj_up in SHOOTABLE:
                return True
            if base_y > agent_y and obj_down in SHOOTABLE:
                return True

        return False
