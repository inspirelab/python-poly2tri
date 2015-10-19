#!/usr/bin/env python2.6
import sys
from time import clock
from p2t import *
# PyGame Constants
import pygame
from pygame.gfxdraw import trigon, line, circle
from pygame.locals import *
from pygame import Color
import time
from graph import Graph
from math import sqrt
import random
import matplotlib.path as mplp
import numpy as np

def dist(a, b):
    return int(sqrt((a.x - b.x)*(a.x - b.x) + (a.y - b.y)*(a.y - b.y)))

def load_points(file_name):
    infile = open(file_name, "r")
    points = []
    while infile:
        line = infile.readline()
        s = line.split()
        if len(s) == 0:
            break
        points.append([float(s[0]), float(s[1])])
    return points

def load_holes(file_name):
    infile = open(file_name, "r")
    holes = []
    bbpath = []
    while infile:
        line = infile.readline()
        if(len(line) == 0):
            break
        elif(line[0] == '/'):
            continue
        else:
            hole = []
            while infile:
                if(len(line) == 0):
                    if len(hole) != 0:
                        holes.append(hole)
                    break
                elif(line[0] == '/'):
                    holes.append(hole)
                    break
                s = line.split()
                print s
                hole.append([float(s[0]), float(s[1])])
                line = infile.readline()
            bbpath.append(mplp.Path(np.array(hole)))
    return holes, bbpath

def checkinPoly(point, bbpath):
    for b in bbpath:
        if b.contains_point(point):
            return False
    return True

def main(file_name_map, file_name_obs, translate, zoom, num_tasks):
    
    SCREEN_SIZE = 360,240
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE,0,8)
    pygame.display.set_caption('poly2tri demo')
    
    pygame.mouse.set_visible(True)
    
    black = Color(0,0,0)
    red = Color(0, 0, 0)
    green = Color(255, 255, 255)
    yellow = Color(255, 255, 0)
    
    screen.fill(black)
    
    points = load_points(file_name_map)
    (holes,bbpath) = load_holes(file_name_obs)
    polyline = []
    for p in points:
        p[0] = p[0]*zoom + translate[0]
        p[1] = p[1]*zoom + translate[1]
        polyline.append(Point(p[0],p[1]))

    # initialize clock
    t0 = clock()  
    ##
    ## Step 1: Initialize
    ## NOTE: polyline must be a simple polygon. The polyline's points
    ## constitute constrained edges. No repeat points!!!
    ##
    cdt = CDT(polyline) 
    ##
    ## Step 2: Add holes and interior Steiner points if necessary
    ##
    # xarr = [229, 236, 214, 285, 256, 265]
    # yarr = [193, 224, 246, 190, 260, 214]
    hole_arr = []
    # obstacles = holes
    for h in holes:
        hole = []
        for p in h:
            p[0] = p[0]*zoom + translate[0]
            p[1] = p[1]*zoom + translate[1]
            hole.append(Point(p[0], p[1]))
        cdt.add_hole(hole)
        hole_arr.extend(hole)

    i = 0
    xarr = []
    yarr = []
    while i<num_tasks:
        x = random.randint(1,119)
        y = random.randint(1, 79)
        if checkinPoly((x,y), bbpath):
            px = x*zoom + translate[0]
            py = y * zoom + translate[1]
            if(px in xarr and py in yarr):
                continue
            xarr.append(x*zoom +translate[0])
            yarr.append(y*zoom +translate[1])
            cdt.add_point(Point(x*zoom +translate[0],y*zoom +translate[1]))
            i = i + 1
    ## Step 3: Triangulate
    ##
    triangles = cdt.triangulate()
    
    print "Elapsed time (ms) = " + str(clock()*1000.0)
        
    # The Main Event Loop
    done = False
    vertexArr = []
    g = Graph(len(points) + len(hole_arr) + len(xarr))
    for t in triangles:
        x1 = int(t.a.x)
        y1 = int(t.a.y)
        x2 = int(t.b.x)
        y2 = int(t.b.y)
        x3 = int(t.c.x)
        y3 = int(t.c.y)
        i1 = -1;
        i2 = -1;
        i3 = -1;
        for i in range(len(vertexArr)):
            if(vertexArr[i].x == x1 and vertexArr[i].y == y1):
                i1 = i
            elif(vertexArr[i].x == x2 and vertexArr[i].y == y2):
                i2 = i
            elif(vertexArr[i].x == x3 and vertexArr[i].y == y3):
                i3 = i
        if(i1 == -1):
            vertexArr.append(Point(x1, y1))
            i1 = len(vertexArr) - 1
        if(i2 == -1):
            vertexArr.append(Point(x2, y2))
            i2 = len(vertexArr) - 1
        if(i3 == -1):
            vertexArr.append(Point(x3, y3))
            i3 = len(vertexArr) - 1
        
        trigon(screen, x1, y1, x2, y2, x3, y3, red)
        g.addEdge(i1, i2, int(dist(Point(x1, y1), Point(x2, y2))))
        g.addEdge(i3, i2, int(dist(Point(x2, y2), Point(x3, y3))))
        g.addEdge(i1, i3, int(dist(Point(x3, y3), Point(x1, y1))))
    g.FloydWarshall()

    guard = []
    print "look " + str(len(xarr)) + str(len(vertexArr))
    for i in range(g.sz):
        for j in range(len(xarr)):
            if(xarr[j] == int(vertexArr[i].x) and yarr[j] == int(vertexArr[i].y)):
                guard.append(i)

    g.guard = guard
    (rcdtgrid, parts, mapping) = g.GraphReduction()
    colors = []
    for i in range(len(parts)):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        colors.append(Color(r, g, b))
    flag = 0
    while not done:
        
        # Draw outline
        for i in range(len(points)):
            j = i+1 if i < len(points) - 1 else 0
            x1 = int(points[i][0])
            y1 = int(points[i][1])
            x2 = int(points[j][0])
            y2 = int(points[j][1])
            line(screen, x1, y1, x2, y2, green)
        
        # Draw holes if necessary
        for obs in holes:
            for i in range(len(obs)):
              j = i+1 if i < len(obs) - 1 else 0
              x1 = int(obs[i][0])
              y1 = int(obs[i][1])
              x2 = int(obs[j][0])
              y2 = int(obs[j][1])
              line(screen, x1, y1, x2, y2, green)

        for i in range(len(vertexArr)):
            for j in range(len(vertexArr)):
                    
    
                if(i not in mapping):
                    continue
                if(j not in mapping):
                    continue

                if parts[mapping.index(i)] == 1:
                    pygame.draw.circle(screen, (255, 0, 0), (int(vertexArr[i].x), int(vertexArr[i].y)), 3, 0) 
                elif parts[mapping.index(i)] == 0:
                    pygame.draw.circle(screen, (0, 255, 0), (int(vertexArr[i].x), int(vertexArr[i].y)), 3, 0) 
                elif parts[mapping.index(i)] == 2:
                    pygame.draw.circle(screen, (0, 0, 255), (int(vertexArr[i].x), int(vertexArr[i].y)), 3, 0)
                else:
                    pygame.draw.circle(screen, (255, 255, 255), (int(vertexArr[i].x), int(vertexArr[i].y)), 3, 0)
                
                if(rcdtgrid[i][j] == 1000000007 or parts[mapping.index(i)] != parts[mapping.index(j)]):
                    continue
                if not flag:
                    print mapping.index(i)

                line(screen, int(vertexArr[i].x), int(vertexArr[i].y), int(vertexArr[j].x), int(vertexArr[j].y), colors[parts[mapping.index(i)]])
        flag = 1
        # Update the screen
        pygame.display.update()
            
        # Event Handling:
        events = pygame.event.get( )
        for e in events:
            if( e.type == QUIT ):
                done = True
                break
            elif (e.type == KEYDOWN):
                if( e.key == K_ESCAPE ):
                    done = True
                    break
                if( e.key == K_f ):
                    pygame.display.toggle_fullscreen()
                  
    return

if __name__=="__main__":
    if len(sys.argv) == 7:
      file_name_map = sys.argv[1]
      file_name_obs = sys.argv[2]
      tx = float(sys.argv[3])
      ty = float(sys.argv[4])
      zoom = float(sys.argv[5])
      num_tasks = int(sys.argv[6])
      main(file_name_map, file_name_obs, [tx, ty], zoom, num_tasks)
      exit()
    
    print
    print("  Usage: filename translate-x translate-y zoom")
    print("Example: python test.py data/dude.dat 100 -200 1")
    print("         python test.py data/nazca_monkey.dat 400 300 4.5")  