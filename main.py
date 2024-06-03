import timeit
import numpy as np
from collections import Counter, defaultdict
from termcolor import colored
import os
import time
import random

dist = 3

COLORS = ['red', 'green', 'cyan', 'blue', 'magenta']

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

def pmat_anim(mat):
    pmat(mat)
    time.sleep(1/8)
    os.system('cls')


def blank_world(w, h):
    return np.zeros((w, h), np.int16)


from numba import njit

@njit
def resolve_combat(world, players):
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

def find_diamond_coordinates(W, H, N, X, Y):
    # Determine the minimum radius r that includes at least N points
    r = 0
    while (2 * r * r + 2 * r + 1) < N:
        r += 1

    # Collect all valid points in the diamond shape within the grid
    points = []
    for dx in range(-r, r + 1):  # range from -r to r
        for dy in range(-r, r + 1):  # range from -r to r
            if abs(dx) + abs(dy) <= r:  # condition for diamond shape (Manhattan distance)
                nx, ny = X + dx, Y + dy
                if 0 <= nx < W and 0 <= ny < H:  # check grid bounds
                    points.append((nx, ny))

    return points


def resolve_movmement(world, flow):

    w,h = world.shape

    targets = defaultdict(list)

    for x in range(w):
        for y in range(h):
            
            if world[x, y] == 0:
                continue
            
            d = flow[x, y]
            
            if (x == 0 and d == 4) or (x == w-1 and d == 2) or (y == 0 and d == 1) or (y == h-1 and d == 3):
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
            pos = positions.pop(random.randint(0, len(positions)-1))
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


players = np.array([1, 2])

world = blank_world(32, 32)
w,h = world.shape

world[1,1] = 1

world[0:8:2, ::2] = players[0]
world[24:32:2, ::2] = players[1]

# pts = find_diamond_coordinates(w, h, 40, 16, 16)
# for x, y in pts:
#     world[x, y] = 2

def goto(x, y, ax, ay):
    dx = x-ax
    dy = y-ay

    if dx == 0 and dy == 0:
        return 0

    if abs(dx) >= abs(dy):
        return 2 if dx < 0 else 4
    else:
        return 3 if dy < 0 else 1


i = 0
while True:
    i += 1
    pmat_anim(world)
    
    flow = np.zeros_like(world)
    p1s = np.array(list(zip(*np.where(world == 1))))
    p2s = np.array(list(zip(*np.where(world == 2))))


    p1pos = (0, 0)
    p2pos = (0, 0)

    x1s, y1s = 0, 0
    if len(p1s):
        for x, y in p1s:
            x1s += x
            y1s += y
        x1s //= len(p1s)
        y1s //= len(p1s)

    x2s, y2s = 0, 0
    if len(p2s):
        for x, y in p2s:
            x2s += x
            y2s += y
        x2s //= len(p2s)
        y2s //= len(p2s)

    # for x, y in p1s:
        
    #     c = 0
    #     if x != 0 and world[x-1, y] == 1:
    #         c += 1
    #     if x != w-1 and world[x+1, y] == 1:
    #         c += 1
    #     if y != 0 and world[x, y-1] == 1:
    #         c += 1
    #     if y != h-1 and world[x, y+1] == 1:
    #         c += 1

    #     if c < 2:
    #         flow[x, y] = goto(x, y, x1s, y1s)
    #     else:
    #         if (i+x+y) % 10 == 0:
    #             flow[x, y] = random.randint(1, 4)
    #         else:
    #             flow[x, y] = p1target


    p2form = sorted(find_diamond_coordinates(w, h, len(p2s), x2s, y2s), key=lambda p: (abs(p[0]-x1s) + abs(p[1]-y1s)))

    for x, y in p2s:
        flow[x, y] = goto(x, y, x2s, y2s)

    for i, (fx, fy) in enumerate(p2form):
        if i < len(p2s):
            p2s = sorted(p2s, key=lambda p: (abs(p[0]-fx) + abs(p[1]-fy)))
            x, y = p2s.pop()
            flow[x, y] = goto(x, y, fx, fy)


    # for x, y in p2s:
    #     coord = p2form.pop(-1)
    #     if (i) % 8 == 0:
    #         flow[x, y] = random.randint(1, 4)
    #     else:
    #         flow[x, y] = goto(x, y, *coord)

    #     # print(i)
        # exit()

        # if c <= 2:
        #     flow[x, y] = goto(x, y, x2s, y2s)
        # else:
        

    world = resolve_movmement(world, flow)
    world = resolve_combat(world, players)





# players = np.array([1, 2])

# world = blank_world(128, 128)

# # world[0, 0] = players[0]
# world[0:64:2, ::2] = players[0]
# world[64:128:2, ::2] = players[1]



# def test_movement():
#     global world
#     flow = np.random.randint(0, 5, (128, 128))
#     world = resolve_movmement(world, flow)

# test_movement()

# print(timeit.timeit(test_movement, number=100))

# def test_combat():
#     global world
#     world = resolve_combat(world, players)

# test_combat()

# print(timeit.timeit(test_combat, number=100))
