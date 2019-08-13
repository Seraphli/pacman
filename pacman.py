import numpy as np
import random
from pacman_enum import Elements

DIRECTIONS = ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))
ACTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))


class MovingObj(object):
    def __init__(self, pos, dir):
        self.start_pos = tuple(pos)
        self.pos = pos
        self.dir = dir

    def next_pos(self):
        return self.pos[0] + self.dir[0], self.pos[1] + self.dir[1]


class Ghost(MovingObj):
    ESCAPE_CD = 20
    STUN_CD = 20

    def __init__(self, index, pos, dir):
        super(Ghost, self).__init__(pos, dir)
        self.index = index
        self.escape = False
        self.escape_cd = 0
        self.stun_cd = 0


class Pacman(MovingObj):
    def __init__(self, pos, dir):
        super(Pacman, self).__init__(pos, dir)
        self.life = 3


class Env(object):
    def __init__(self, map):
        self.map = map
        self.actions = ACTIONS
        self.max_x = self.map.shape[1]
        self.max_y = self.map.shape[2]
        self._display = None

    def render(self):
        import pygame
        n = 20
        pygame.init()
        self._display = pygame.display.set_mode((self.max_y * n,
                                                 self.max_x * n))
        self._render_unit = np.ones((n, n))

    def reset(self):
        self.cur_map = np.copy(self.map)
        self.game_over = False
        self.win = None
        self.ghosts = []
        for i in range(4, self.map.shape[0]):
            pos = list(np.argwhere(self.map[i, :, :] == 1)[0])
            self.ghosts.append(Ghost(i - 4, pos, random.choice(ACTIONS)))
        pos = list(np.argwhere(self.map[3, :, :] == 1)[0])
        self.pacman = Pacman(pos, (0, 0))

    def get_state(self):
        state = self.cur_map[0] + self.cur_map[2]
        state[self.pacman.pos[0], self.pacman.pos[1]] = Elements.PACMAN
        for i in range(4, self.map.shape[0]):
            ghost = self.ghosts[i - 4]
            state[ghost.pos[0], ghost.pos[1]] = Elements.GHOST_ESCAPE \
                if ghost.escape else Elements.GHOST
        return state

    def update_ghost(self):
        for ghost in self.ghosts:
            if ghost.stun_cd > 0:
                ghost.stun_cd -= 1
                continue
            if ghost.escape_cd > 0:
                ghost.escape_cd -= 1
            else:
                ghost.escape = False
            _a = list(ACTIONS)
            if self.cur_map[1, ghost.pos[0], ghost.pos[1]] == 1:
                _a.remove((-ghost.dir[0], -ghost.dir[1]))
                ghost.dir = random.choice(_a)
            while True:
                next_pos = ghost.next_pos()
                if next_pos[0] == self.max_x:
                    ghost.pos = (0, next_pos[1])
                    break
                elif next_pos[0] == -1:
                    ghost.pos = (self.max_x - 1, next_pos[1])
                    break
                elif next_pos[1] == self.max_y:
                    ghost.pos = (next_pos[0], 0)
                    break
                elif next_pos[1] == -1:
                    ghost.pos = (next_pos[0], self.max_y - 1)
                    break
                elif self.cur_map[0, next_pos[0], next_pos[1]] != Elements.WALL:
                    ghost.pos = ghost.next_pos()
                    break
                _a.remove(ghost.dir)
                ghost.dir = random.choice(_a)

    def update_pacman(self, action):
        state = self.get_state()
        next_pos = self.pacman.pos
        if state[next_pos[0], next_pos[1]] == Elements.GHOST:
            self.pacman.dir = (0, 0)
            self.pacman.pos = self.pacman.start_pos
            self.pacman.life -= 1
            return
        elif state[next_pos[0], next_pos[1]] == Elements.GHOST_ESCAPE:
            for ghost in self.ghosts:
                if ghost.escape and ghost.pos == next_pos:
                    ghost.pos = ghost.start_pos
                    ghost.escape = False
                    ghost.cd = Ghost.STUN_CD
        self.pacman.dir = action
        next_pos = self.pacman.next_pos()
        if next_pos[0] == self.max_x:
            self.pacman.pos = (0, next_pos[1])
            return
        elif next_pos[0] == -1:
            self.pacman.pos = (self.max_x - 1, next_pos[1])
            return
        elif next_pos[1] == self.max_y:
            self.pacman.pos = (next_pos[0], 0)
            return
        elif next_pos[1] == -1:
            self.pacman.pos = (next_pos[0], self.max_y - 1)
            return
        elif self.map[0, next_pos[0], next_pos[1]] == Elements.WALL:
            self.pacman.dir = (0, 0)
            self.pacman.pos = self.pacman.next_pos()
            return
        next_pos = self.pacman.next_pos()
        if state[next_pos[0], next_pos[1]] == Elements.GHOST:
            self.pacman.dir = (0, 0)
            self.pacman.pos = self.pacman.start_pos
            self.pacman.life -= 1
            return
        elif state[next_pos[0], next_pos[1]] == Elements.GHOST_ESCAPE:
            for ghost in self.ghosts:
                if ghost.escape and ghost.pos == next_pos:
                    ghost.pos = ghost.start_pos
                    ghost.escape = False
                    ghost.cd = Ghost.STUN_CD
        elif state[next_pos[0], next_pos[1]] == Elements.SUPER_BEAN:
            self.cur_map[2, next_pos[0], next_pos[1]] = 0
            for ghost in self.ghosts:
                if ghost.stun_cd == 0:
                    ghost.escape = True
                    ghost.escape_cd = Ghost.ESCAPE_CD
            self.pacman.pos = next_pos
        elif state[next_pos[0], next_pos[1]] == Elements.BEAN:
            self.cur_map[2, next_pos[0], next_pos[1]] = 0
            self.pacman.pos = next_pos
        else:
            self.pacman.pos = next_pos

    def take_action(self, action):
        self.update_ghost()
        self.update_pacman(action)

        if self.pacman.life <= 0:
            self.game_over = True
            self.win = False
        if not np.any(self.cur_map[2, :, :]):
            self.game_over = True
            self.win = True

        if self._display:
            import pygame
            state = self.get_state()
            state = state.transpose()
            state[state > Elements.SUPER_BEAN] *= 5
            state = 255 * state / state.max()
            state = np.kron(state, self._render_unit)
            surf = pygame.surfarray.make_surface(state)
            self._display.blit(surf, (0, 0))
            pygame.display.update()

    def close(self):
        if self._display:
            import pygame
            pygame.quit()


if __name__ == '__main__':
    import pickle
    import time

    L = 1
    fn = f'maps/level{L}.pkl'
    st = time.time()
    env = Env(pickle.load(open(fn, 'rb')))
    # env.render()
    step = 0
    for i in range(1000):
        # print(i)
        env.reset()
        # step = 0
        while not env.game_over:
            env.take_action(random.choice(env.actions))
            # input()
            step += 1
            # if step == 108:
            #     break
    env.close()
    print((time.time() - st))
    print(step / 1000)
