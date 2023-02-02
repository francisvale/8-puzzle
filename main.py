from copy import deepcopy
import pygame, sys
from pygame.locals import *
import random
from queue import PriorityQueue
import time


#General Setup
pygame.init()
clock = pygame.time.Clock()

pygame.display.init()

# Display Screen
screen_width = 480
screen_height = 540
screen = pygame.display.set_mode((screen_width, screen_height))

font = pygame.font.SysFont("cambria", 60)
wd = 80+15
x = 105
y = 97
done_solving = False
solving = False
count = 0
value = 0
animating = False
s = []
asol = []


solved_loc = [[x+wd*1, y+wd*0, 1], [x+wd*2, y+wd*0, 2], 
        [x+wd*0, y+wd*1, 3], [x+wd*1, y+wd*1, 4], [x+wd*2, y+wd*1, 5], 
        [x+wd*0, y+wd*2, 6], [x+wd*1, y+wd*2, 7], [x+wd*2, y+wd*2, 8]]


loc = [[x+wd*0, y+wd*0, 3], [x+wd*1, y+wd*0, 1], [x+wd*2, y+wd*0, 2],  
        [x+wd*0, y+wd*1, 7], [x+wd*2, y+wd*1, 6],
        [x+wd*0, y+wd*2, 4], [x+wd*1, y+wd*2, 8], [x+wd*2, y+wd*2, 5]]

empty_slot = [x+wd*1, y+wd*1, 0]

def check(done, loc, solved_loc):
    flag = 0
    for i in loc:
        if i in solved_loc:
            flag += 1
    if flag >= 8:
        done = True

# click on the piece to move to blank
def moving_piece(pos,win):
    global loc
    global empty_slot
    pressed = False
    for i in range(len(loc)):
        if pos[0]>loc[i][0] and pos[0]<loc[i][0]+80 and pos[1]>loc[i][1] and pos[1]<loc[i][1]+80:
            pressed = True
            #print(loc[i])
            break
        
    if pressed:
        if loc[i][0]+wd == empty_slot[0] and loc[i][1] == empty_slot[1]:
            temp = loc[i]
            empty_slot[2] = loc[i][2]
            loc[i] = empty_slot
            empty_slot = temp
            empty_slot[2] = 0
            pygame.draw.rect(win,(0,0,0),(empty_slot[0],empty_slot[1],80,80))
        elif loc[i][0] == empty_slot[0] and loc[i][1]+wd == empty_slot[1]:
            temp = loc[i]
            empty_slot[2] = loc[i][2]
            loc[i] = empty_slot
            empty_slot = temp
            empty_slot[2] = 0
            pygame.draw.rect(win,(0,0,0),(empty_slot[0],empty_slot[1],80,80))
        elif loc[i][0]-wd == empty_slot[0] and loc[i][1] == empty_slot[1]:
            temp = loc[i]
            empty_slot[2] = loc[i][2]
            loc[i] = empty_slot
            empty_slot = temp
            empty_slot[2] = 0
            pygame.draw.rect(win,(0,0,0),(empty_slot[0],empty_slot[1],80,80))
        elif loc[i][0] == empty_slot[0] and loc[i][1]-wd == empty_slot[1]:
            temp = loc[i]
            empty_slot[2] = loc[i][2]
            loc[i] = empty_slot
            empty_slot = temp
            empty_slot[2] = 0
            pygame.draw.rect(win,(0,0,0),(empty_slot[0],empty_slot[1],80,80))

# elements that dont move
def static(win):
    for i in range(4):
        pygame.draw.line(win,(200,200,200),(x-15, y-8+95*i),(x-2+3*95,y-8+95*i),15)
    for i in range(4):
        pygame.draw.line(win,(200,200,200),(x-8+95*i, y-15),(x-8+95*i,y-1+95*3),15)
    
    prefont = pygame.font.SysFont('04b', 50)
    prefont2 = pygame.font.SysFont('04b', 25)
    display = prefont.render("8 PUZZLE GAME", True, (255, 255, 255))
    display2 = prefont2.render("Solve using:", True, (255, 255, 255))
    display3 = prefont2.render("Solution:", True, (255,255,255))
    win.blit(display, (107, 27))
    win.blit(display2, (65, 397))
    win.blit(display3, (65, 471))

# display the board
def show(win, state, empty):
    pygame.draw.rect(win,(0,0,0), ((empty[0]), (empty[1]), 80, 80))
    for l in state:
        pygame.draw.rect(win, (70, 120, 2), (l[0], l[1], 80, 80))
        text = font.render(str(l[2]), True, (255,255,255))
        win.blit(text, (l[0]+25, l[1]+7))
    

# To Make buttons
class Button():
    def __init__(self, x,y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.clicked = False
    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()  [0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

# buttons
shuffle = pygame.image.load('Static/Shuffle.png').convert_alpha()
shuffle_button = Button(290+25, 424+3, shuffle, 0.3)

bfs = pygame.image.load('Static/BFS.png').convert_alpha()
bfs_button = Button(65, 424+5, bfs, 0.25)

astar = pygame.image.load('Static/Astar.png').convert_alpha()
astar_button = Button(165, 424+5, astar, 0.25)


# shuffle pieces
def shuffle(win):
    global loc, empty_slot, done_solving
    done_solving = False
    pygame.draw.rect(win, (0,0,0), (0, 493, 480, 31))
    visited = []
    a = modif()

    visited.append(a)

    while len(visited) < 11:
        move = []
        b = move_list(visited[-1])
        i = random.randint(0, len(b)-1)
        move.append(b[i])

        c = move_tile(visited[-1], move)
        c[0].sort()

        if c[0] not in visited:
            for i in c[0]:
                if i[2] == 0:
                    temp = deepcopy(c[0])
                    empty_slot = temp.pop(temp.index(i))
                    loc = temp
                    break
            visited.append(c[0])
    

# Start for the bfs search
def move_list(start):
    global loc
    global solved_loc
    global empty_slot
    global x, y, wd

    s = deepcopy(start)
    move_list = []
    
    for i in range(len(s)):
        if s[i][2] == 0:
            if s[i][0] < (x+wd*2):
                if "R" not in move_list:
                    move_list.append("R")
            if s[i][1] < (y+wd*2):
                if "D" not in move_list:
                    move_list.append("D")
            if s[i][1] > y:
                if "U" not in move_list:
                    move_list.append("U")
            if s[i][0] > x:
                if "L" not in move_list:
                    move_list.append("L")
    return move_list
    
def move_tile(current_loc, movlist):
    result = []
    temp = deepcopy(current_loc)
    for i in temp:
        if i[2] == 0:
            empty = temp.index(i)
    for j in movlist:
        if j == 'R':
            temp[empty][2], temp[empty+3][2] = temp[empty+3][2], temp[empty][2]
        elif j == 'D':
            temp[empty][2], temp[empty+1][2] = temp[empty+1][2], temp[empty][2]
        elif j == 'L':
            temp[empty][2], temp[empty-3][2] = temp[empty-3][2], temp[empty][2]
        elif j == 'U':
            temp[empty][2], temp[empty-1][2] = temp[empty-1][2], temp[empty][2]
        result.append(temp) 
        temp = deepcopy(current_loc) 
    return result

def modif():
    global loc
    global empty_slot
    curloc = deepcopy(loc)
    emloc = deepcopy(empty_slot)
    curloc.append(emloc)
    curloc.sort()
    return curloc

def backtrace(start, level, end, count):
    path = [end]
    for i in range(count-1, -1, -1):
        if end in level[i] and level[i][0] != start:
            path.append(level[i][0])
            end = level[i][0]
    path.append(start)
    path.reverse()
    return path

def bfs(start):
    global solved_loc
    print("Currently doing Breadth-First search algorithm... ")

    solved = deepcopy(solved_loc)
    solved.append([x+wd*0, y+wd*0, 0])
    solved.sort()

    
    visited = []
    level = {0:[start]}
    queue =[]
    count = 1

    
    queue.append(start)

    
    while queue:
        path = queue.pop(0)  
        if path == solved:
            return backtrace(start, level, solved, count)

        elif path not in visited:
            s = move_list(path)
            t = move_tile(path, s)
            level[count] = [path]
            for adjacent in t:
                if adjacent not in visited:
                        
                    level[count].append(adjacent)
                    queue.append(adjacent)
            count+=1
        visited.append(path)

# --- END for the BFS search ---

# Start for the a* algorithm

class Astarframework:
    goal_state=[0,1,2,3,4,5,6,7,8]
    heuristic=None
    evaluation_function=None
    needs_hueristic=True
    num_of_instances=0

    def __init__(self,state,parent,action,path_cost,needs_hueristic=False):
        self.parent=parent
        self.state=state
        self.action=action
        if parent:
            self.path_cost = parent.path_cost + path_cost
        else:
            self.path_cost = path_cost
        if needs_hueristic:
            self.needs_hueristic=True
            self.manhattan_distance()
            self.evaluation_function=self.heuristic+self.path_cost
        Astarframework.num_of_instances+=1

    def __str__(self):
        return str(self.state[0:3])+'\n'+str(self.state[3:6])+'\n'+str(self.state[6:9])

    def manhattan_distance(self):
        self.heuristic=0
        for num in range(1,9):
            distance=abs(self.state.index(num) - self.goal_state.index(num))
            i=int(distance/3)
            j=int(distance%3)
            self.heuristic=self.heuristic+i+j

    def ifsolved(self):
        if self.state == self.goal_state:
            return True
        return False

    @staticmethod
    def find_legal_actions(i,j, prev_action=''):
        legal_action = ['U', 'D', 'L', 'R']
        if i == 0 or prev_action == 'D':  # up is disable
            legal_action.remove('U')
        if i == 2 or prev_action == 'U':  # down is disable
            legal_action.remove('D')
        if j == 0 or prev_action == 'R': # left is disable
            legal_action.remove('L')
        if j == 2 or prev_action == 'L': # right is disable
            legal_action.remove('R')
        return legal_action

    @staticmethod
    def find_blank_pos(arr):
        x = arr.index(0)
        i = int(x / 3)
        j = int(x % 3)
        return i,j,x

    def generate_child(self):
        children = []
        i,j,x = Astarframework.find_blank_pos(self.state)
        legal_actions = Astarframework.find_legal_actions(i,j)

        for action in legal_actions:
            new_state = self.state.copy()
            if action == 'U':
                new_state[x], new_state[x-3] = new_state[x-3], new_state[x]
            elif action == 'D':
                new_state[x], new_state[x+3] = new_state[x+3], new_state[x]
            elif action == 'L':
                new_state[x], new_state[x-1] = new_state[x-1], new_state[x]
            elif action == 'R':
                new_state[x], new_state[x+1] = new_state[x+1], new_state[x]
            children.append(Astarframework(new_state,self,action,1,self.needs_hueristic))
        return children

    def find_solution(self):
        global sol
        solution = []
        solution.append(self.action)
        path = self
        while path.parent != None:
            path = path.parent
            solution.append(path.action)
        solution = solution[:-1]
        solution.reverse()
        sol = solution
        return 

def astar_search(initial_state):
    print("Currently doing A * search algorithm...")
    count=0
    explored=[]
    start_node=Astarframework(initial_state,None,None,0,True)
    q = PriorityQueue()
    q.put((start_node.evaluation_function,count,start_node))

    while not q.empty():
        node=q.get()
        node=node[2]
        explored.append(node.state)
        if node.ifsolved():
            return node.find_solution()

        children=node.generate_child()
        for child in children:
            if child.state not in explored:
                count += 1
                q.put((child.evaluation_function,count,child))
    return

def move_to(current_loc, move):
    temp = deepcopy(current_loc)
    for i in temp:
        if i[2] == 0:
            empty = temp.index(i)
    if move == 'R':
        temp[empty][2], temp[empty+3][2] = temp[empty+3][2], temp[empty][2]
    elif move == 'D':
        temp[empty][2], temp[empty+1][2] = temp[empty+1][2], temp[empty][2]
    elif move == 'L':
        temp[empty][2], temp[empty-3][2] = temp[empty-3][2], temp[empty][2]
    elif move == 'U':
        temp[empty][2], temp[empty-1][2] = temp[empty-1][2], temp[empty][2]
    return temp
    

sol = []

def convert(current_loc):
    place = []
    for i in current_loc:
        place.append(i[2])
    return place

def takeSecond(elem): 
    return elem[1]

def convert2(sol, start):
    global asol2
    temp = deepcopy(start)
    count = 0
    result= [temp]
    for i in sol:
        x = move_to(result[count], i)
        #print("this is the x: "+ str(x))
        s = deepcopy(x)
        result.append(s)
        count +=1
    return result

def a_star(start):
    global sol
    hold = deepcopy(start)
    hold.sort(key=takeSecond)
    x = convert(hold)
    astar_search(x)

    z = convert2(sol, start)

    return z
# --- END for the a* search algorithm ---

# conver to adjust for input in A* algo
def convert(current_loc):
    temp = deepcopy(current_loc)
    place = []
    for i in temp:
        place.append(i[2])
    return place

# helpful in converting
def takeSecond(elem):
    return(elem[1])

# get solution
def solution(s):
    sol = []
    for i in range(0,len(s)):
        a = move_list(s[i])
        for j in a:
            b = move_tile(s[i], j)
            b[0].sort()
            s[i].sort()
            try:
                if b[0] == s[i+1]:
                    sol.append(j)
                    break
            except:
                pass
    return sol

# display solution to screen
def dispSol(win, sol):
    pygame.draw.rect(win, (0,0,0), (0, 493, 480, 31))
    this = ' '.join(sol)

    if len(sol) > 16:
        x = 32
        y = 507
    else:
        x = 155
        y = 493

    prefont2 = pygame.font.SysFont('04b', 30)
    display3 = prefont2.render(this, True, (255,255,255))
    win.blit(display3, (x, y))



# main           
def game(animating, value):
    global loc, empty_slot, done_solving
    game = True
    while game:
        clock.tick(60)
        for event in pygame.event.get():
            if bfs_button.draw():
                if done_solving == False:
                    start = modif()
                    start2 = time.time()
                    s = bfs(start)
                    end = time.time()
                    print("Solution Found in " + str(end - start2) +" seconds!")
                    g = solution(s)
                    dispSol(screen, g)
                    done_solving = True
                else:
                    if animating == False:
                        animating = True
                        game = False
                        solve(animating, value, s)
                    else:
                        animating = False
            if astar_button.draw():
                if done_solving == False:
                    start = modif()
                    start2 = time.time()
                    s = a_star(start)
                    end = time.time()
                    print("Solution Found in " + str(end - start2) +" seconds!")
                    g = solution(s)
                    dispSol(screen, g)
                    done_solving = True
                else:
                    if animating == False:
                        animating = True
                        game = False
                        solve(animating, value, s)
                    else:
                        animating = False
            if shuffle_button.draw():
                shuffle(screen)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                #done_solving = False
                pos1 = pygame.mouse.get_pos()
                moving_piece(pos1, screen)
                if pos1[0] > 75 and pos1[0] < 375 and pos1[1] > 135 and pos1[1] < 405:
                    #check(done, loc, solved_loc)
                    done_solving = False
                show(screen, loc, empty_slot)

        pygame.display.flip()
        show(screen, loc, empty_slot)

# solving        
def solve(animating, value, moves):
    global loc, empty_slot, done_solving
    solve = True
    while solve:
        clock.tick(5)
        if value >= len(moves):
            value = 0
            animating = False
            solve = False
            done_solving = False
            game(animating, value)
            
        try:
            move = moves[value]
        except:
            pass

        if animating == True:
            for i in move:
                if i[2] == 0:
                    temp = deepcopy(move)
                    empty_slot = temp.pop(temp.index(i))
                    loc = temp
                    break
        pygame.display.flip()
        show(screen, loc, empty_slot)
        #screen.fill((0,0,0))

        if animating == True:
            value += 1
    screen.fill((0,0,0))

# display static elements
static(screen)

# run game    
game(animating, value)

    