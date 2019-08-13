import numpy as np
import pickle
from pacman_enum import Elements

L = 1
fn = f'level{L}.csv'
with open('maps/' + fn) as f:
    lines = f.read().split('\n')
    csv_map = []
    for line in lines:
        if line == '':
            break
        csv_map.append([int(i) for i in line.split(',')][1:])
csv_map = np.array(csv_map[1:])
ghost_num = len(np.argwhere(csv_map == Elements.GHOST))
map = np.zeros((4 + ghost_num, csv_map.shape[0], csv_map.shape[1]),
               dtype=np.int8)
_map = np.copy(csv_map)
_map[_map != Elements.WALL] = 0
map[0, :, :] = _map

_map[_map == 0] = 1
_map[_map == Elements.WALL] = 0
D = ((1, 1), (1, -1), (-1, 1), (-1, -1))
for dx, dy in D:
    intersect = _map[1 + dx:None if dx == 1 else dx - 1, 1:-1] + \
                _map[1:-1, 1 + dy:None if dy == 1 else dy - 1] + \
                _map[1:-1, 1:-1]
    for index in np.argwhere(intersect == 3):
        map[1, index[0] + 1, index[1] + 1] = 1

_map = np.copy(csv_map)
_map[_map > Elements.SUPER_BEAN] = 0
map[2, :, :] = _map
_map = np.copy(csv_map)
index = np.argwhere(_map == Elements.PACMAN)[0]
map[3, index[0], index[1]] = 1
indexes = np.argwhere(_map == Elements.GHOST)
for i, index in enumerate(indexes):
    map[4 + i, index[0], index[1]] = 1
pickle.dump(map, open(f'maps/level{L}.pkl', 'wb'))
