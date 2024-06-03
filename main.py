
import numpy as np
from collections import Counter, defaultdict

dist = 3

players = np.array([1, 2])

from termcolor import colored

COLORS = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']

def pmat(mat):
    w, h = mat.shape
    
    counter = Counter()
    
    cw = 0
    
    for y in range(h):
        for x in range(w):
            val = mat[x, y].__repr__()
            mat[x, y] = val
            if len(val) > cw:
                cw = len(val)
            counter[val] += 1
            
    colors = {k: COLORS[i % len(COLORS)] for i, (k,v) in enumerate(sorted(counter.items(), key=lambda t: t[1]))}

    print(((cw+1)*w)*'-')
    
    for y in range(h):
        for x in range(w):
            val = mat[x, y].__repr__()
            print(colored(val, colors[val]) + ' '*(1+(cw-len(val))), end="")
        print()


def blank_world(w, h):
    return np.zeros((w, h), np.int16)


def resolve_combat(world):
    w,h = world.shape

    damage = np.zeros((w, h, len(players)+1), world.dtype)

    for x in range(w):
        for y in range(h):
            cell = world[x, y]
            if cell == 0: continue
            xslice = slice(max(0, x-dist), min(w, x+dist+1))
            yslice = slice(max(0, y-dist), min(h, y+dist+1))
            damage[xslice, yslice, cell:cell+1] += 1

    for x in range(w):
        for y in range(h):
            cell = world[x, y]
            if cell == 0: continue
            fight = damage[x, y]
            domcell = np.argmax(fight)
            blocked = np.count_nonzero(fight[:] == fight[domcell]) > 1
            
            if blocked or domcell == cell: continue
            
            world[x, y] = domcell
        
    return world    


def resolve_movmement(world, flow):

    w,h = world.shape

    targets = defaultdict(list)

    for x in range(w):
        for y in range(h):
            
            if world[x, y] == 0:
                continue
            
            d = flow[x, y]
            
            if (x == 0 and d == 4) or (x == w-1 and d == 2) or (y == 0 and d == 3) or (y == h-1 and d == 1):
                d = 0
        
            nx, ny = x, y
        
            if d == 1:
                ny -= 1
            elif d == 3:
                ny += 1
            elif d == 2:
                nx += 1
            elif d == 4:
                nx -= 1
                
            targets[(nx, ny)].append((x, y))
        
    new_world = np.zeros_like(world)

    def fixblock(x, y):
        positions = targets[x, y]
        
        while len(positions) > 1:
            pos = positions.pop()
            targets[pos].insert(0, pos)
            fixblock(*pos)

    for x, y in list(targets.keys()):
        fixblock(x,y)
        
    for x, y in list(targets.keys()):
        from_positions = targets[x, y]
        if len(from_positions) == 0: continue
        from_x, from_y = from_positions[0]
        cell = world[from_x, from_y]
        new_world[x, y] = cell
        
    return new_world


world = blank_world(16, 16)

world[-1, -1] = players[1]
world[-1, -2] = players[1]
world[1, 1] = players[0]
world[1, 2] = players[0]
world[1, 3] = players[0]
# world[1, 4] = players[0]

world = resolve_combat(world)

pmat(world)

flow = np.zeros_like(world)
flow[1, 1] = 2
flow[1, 2] = 2
flow[1, 3] = 2
# flow[1, 4] = 2

world = resolve_movmement(world, flow)

pmat(world)

world = resolve_combat(world)

pmat(world)