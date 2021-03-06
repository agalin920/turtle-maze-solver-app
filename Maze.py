import turtle

from node import Node
from tkinter import *

PART_OF_PATH = 'O'
TRIED = '.'
OBSTACLE = '+'
DEAD_END = '-'
VISITED = 'x'
CLEAR = ' '

#Splash screen boiii
class SplashScreen(Frame):
    def __init__(self, master=None, width=0.8, height=0.6, useFactor=True):
        Frame.__init__(self, master)
        self.pack(side=TOP, fill=BOTH, expand=YES)

        # get screen width and height
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        w = (useFactor and ws*width) or width
        h = (useFactor and ws*height) or height
        # calculate position x, y
        x = (ws/2) - (w/2) 
        y = (hs/2) - (h/2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.master.overrideredirect(True)
        self.lift()


class Maze:
    def __init__(self, maze_file_name):
        rows_in_maze = 0
        columns_in_maze = 0
        self.maze_list = []
        maze_file = open(maze_file_name,'r')
        #rows_in_maze = 0
        for line in maze_file:
            row_list = []
            col = 0
            for ch in line[: -1]:
                row_list.append(ch)
                if ch == 'S':
                    self.start_row = rows_in_maze
                    self.start_col = col
                col = col + 1
            rows_in_maze = rows_in_maze + 1
            self.maze_list.append(row_list)
            columns_in_maze = len(row_list)

        self.rows_in_maze = rows_in_maze
        self.columns_in_maze = columns_in_maze
        self.x_translate = - columns_in_maze / 2
        self.y_translate = rows_in_maze / 2
        self.t = turtle.Turtle()
        self.t.shape('turtle')
        self.wn = turtle.Screen()
        self.wn.setworldcoordinates(- (columns_in_maze - 1) / 2 - .5,
                - (rows_in_maze - 1) / 2 - .5,
                (columns_in_maze - 1) / 2 + .5,
                (rows_in_maze - 1) / 2 + .5)


    def draw_maze(self):
        self.t.speed(2000)
        for y in range(self.rows_in_maze):
            for x in range(self.columns_in_maze):
                if self.maze_list[y][x] == OBSTACLE:
                    self.draw_centered_box(x + self.x_translate,
                        - y + self.y_translate, 'lightblue')
        self.t.color('black')
        self.t.fillcolor('green')


    def draw_centered_box(self, x, y, color):
        self.t.up()
        self.t.goto(x - .5, y - .5)
        self.t.color(color)
        self.t.fillcolor(color)
        self.t.setheading(90)
        self.t.down()
        self.t.begin_fill()
        for i in range(4):
            self.t.forward(1)
            self.t.right(90)
        self.t.end_fill()


    def move_turtle(self, x, y):
        self.t.up()
        self.t.setheading(self.t.towards(x + self.x_translate,
                    - y + self.y_translate))
        self.t.goto(x + self.x_translate, - y + self.y_translate)


    def drop_bread_crumb(self, color):
        self.t.dot(10, color)


    def update_position(self, row, col, val=None):
        if val:
            self.maze_list[row][col] = val
        self.move_turtle(col, row)

        if val == PART_OF_PATH:
            color = 'green'
        elif val == OBSTACLE:
            color = 'red'
        elif val == TRIED:
            color = 'black'
        elif val == DEAD_END:
            color = 'red'
        elif val == VISITED:
            color = 'gray'
        elif val == "exit":
            color = 'yellow'
        else:
            color = None

        if color:
            self.drop_bread_crumb(color)


    def is_exit(self, row, col):
        return (row == 0 or
            row == self.rows_in_maze - 1 or
            col == 0 or
            col == self.columns_in_maze - 1)


    def __getitem__(self, idx):
        return self.maze_list[idx]


ListQ = [] # Lista de coordenadas visitadas
ListT = [] # Lista de nodos
Route = [] # Lista de coordenadas de la mejor ruta (salida a inicio)

## Recorre la mejor ruta desde inicio a fin

def BE_FREE(maze):
    print("Free at Last!")
    while Route:
        row = Route.pop()
        col = Route.pop()
        maze.update_position(row, col, PART_OF_PATH)

## Cuando encuentra la salida, retrocede al inicio guardando las coordenadas
## por las que va pasando

def best_route(maze, start_row, start_column, tree):

    #maze.update_position(start_row, start_column, PART_OF_PATH)
    #print(tree.name)
    if tree.name == "start":
        Route.append(start_column)
        Route.append(start_row)
        BE_FREE(maze)
        return True
    Route.append(start_column)
    Route.append(start_row)
    tree = tree.prev()
    best_route(maze, tree.row, tree.col, tree)

## Iterative deepening search

def search_from(maze, start_row, start_column, tree):
    ## Verifica si es una salida
    if maze.is_exit(start_row, start_column):
        print("is exit")
        maze.update_position(start_row, start_column, "exit")
        best_route(maze, start_row, start_column, tree)
        return True

    ## Si no checa los vecinos del nodo
    Vrow=start_row
    Vcol=start_column
    Tval=ListT[0]

    del ListQ[0]
    del ListQ[0]
    del ListT[0]


    listTemp = []
    # RIGHT
    move(maze, start_row, start_column + 1, 'RIGHT', tree, listTemp)
    # LEFT
    move(maze, start_row, start_column - 1, 'LEFT', tree, listTemp)
    # DOWN
    move(maze, start_row + 1, start_column, 'DOWN', tree, listTemp)
    # UP
    move(maze, start_row - 1, start_column, 'UP', tree, listTemp)

    listTemp = []  

    try:
        tree = ListT[0] # Pone el puntero en el primer nodo del siguiente nivel
    except:
        raise Exception('No exit in maze.')

    search_from(maze, ListQ[0], ListQ[1], tree) # Vuelve a comenzar la búsqueda por nivel

    


def move(maze, start_row, start_column, dir, tree, listTemp):

    if maze[start_row][start_column] == CLEAR:

        treeName = tree.name # Original tree name

        maze.update_position(start_row, start_column, VISITED)
        
        tree =  tree.add()  # add a node to the partens
        tree.name = dir     # name the node
        tree.row = start_row
        tree.col = start_column

        if treeName == 'start':
            ListQ.append(start_row)
            ListQ.append(start_column)
            ListT.append(tree)
        else:
            ListQ.insert(0, start_column)
            ListQ.insert(0, start_row)
            listTemp.insert(0, tree)
            ListT.insert(0, listTemp.pop())

        print(tree.name)
        tree = tree.prev()



#Splash screen creation
root = Tk()
sp = SplashScreen(root)
sp.config(bg="#3366ff")
logo = PhotoImage(file="/home/agalin/Desktop/AI_practice1/treeFiddy.gif")

m2 = Label(sp, image = logo)
m2.pack(side=TOP, expand=YES)

m = Label(sp, text="Practica 01 \n Agentes que resuelven Problemas mediante Busqueda Tarea\n\nEstefania Jacobo\nJorge Luis Ibarra Borbas\nAndres Galindo")
m.pack(side=TOP, expand=YES)
m.config(bg="#3366ff", justify=CENTER, font=("calibri", 16))
Button(sp, text="Set the turtle free!", bg='green', command=root.destroy).pack(side=BOTTOM, fill=X)
root.mainloop()

# Maze Creation
my_maze = Maze('maze2.txt')
my_maze.draw_maze()
my_maze.update_position(my_maze.start_row, my_maze.start_col)

# Tree Creation

tree=Node()  #create a node
tree.name="start" #name it root
tree.row = my_maze.start_row
tree.col = my_maze.start_col

print(tree.name)

ListQ.append(tree.row)
ListQ.append(tree.col)
ListT.append(tree)
my_maze.update_position(tree.row, tree.col, PART_OF_PATH)

search_from(my_maze, ListQ[0], ListQ[1], tree)

#stop it from ending
k=input("press close to exit")