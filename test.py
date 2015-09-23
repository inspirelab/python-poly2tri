#!/usr/bin/env python2.6

import sys
from time import clock

from p2t import *

# PyGame Constants
import pygame
from pygame.gfxdraw import trigon, line
from pygame.locals import *
from pygame import Color
import time
from graph import Graph
from math import sqrt

head_hole = [[325, 437],[320, 423], [329, 413], [332, 423]]
chest_hole = [[320.72342,480],[338.90617,465.96863],[347.99754,480.61584],
              [329.8148,510.41534], [339.91632,480.11077],[334.86556,478.09046]]

obstacle1 = [[211, 222],[218,226],[217,230],[210,229]]
obstacle2 = [[245,195],[253,197],[250,204],[243,204]]
obstacle3 = [[248,244],[277,250],[273,256],[248,252]]
obstacle4 = [[273,196],[266,224],[279,227],[285,206]]
obstacle = []
obstacle.append(obstacle1)
obstacle.append(obstacle2)
obstacle.append(obstacle3)
obstacle.append(obstacle4)


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

def main(file_name, translate, zoom):
    
    SCREEN_SIZE = 800,600
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE,0,8)
    pygame.display.set_caption('poly2tri demo')
    
    pygame.mouse.set_visible(True)
    
    black = Color(0,0,0)
    red = Color(255, 0, 0)
    green = Color(255, 255, 255)
    yellow = Color(255, 255, 0)
    
    screen.fill(black)
    
    points = load_points(file_name)
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
    if file_name == "data/dude.dat":
        hole = []  
        for p in head_hole:
            p[0] = p[0]*zoom + translate[0]
            p[1] = p[1]*zoom + translate[1]
            hole.append(Point(p[0],p[1]))
        # Add a hole
        cdt.add_hole(hole)
        hole = []  
        for p in chest_hole:
            p[0] = p[0]*zoom + translate[0]
            p[1] = p[1]*zoom + translate[1]
            hole.append(Point(p[0],p[1]))
        # Add a hole
        cdt.add_hole(hole)
        # Add an interior Steiner point
        x = 361*zoom + translate[0]
        y = 381*zoom + translate[1]
        cdt.add_point(Point(x, y))

    # xarr = [323, 372, 334, 424, 342, 352, 100, 567]
    # yarr = [395, 410, 645, 546, 620, 534, 370, 387]

    xarr = [229, 236, 214, 285, 256, 265]
    yarr = [193, 224, 246, 190, 260, 214]

    if file_name == "data/test.dat":
        for i in range(len(xarr)):
            x = xarr[i]*zoom + translate[0]
            y = yarr[i]*zoom + translate[1]
            xarr[i] = x
            yarr[i] = y
            cdt.add_point(Point(x, y))

    if file_name == "data/map.dat":
        for i in range(len(xarr)):
            x = xarr[i]*zoom + translate[0]
            y = yarr[i]*zoom + translate[1]
            xarr[i] = x
            yarr[i] = y
            cdt.add_point(Point(x, y))

    hole_arr = []

    if file_name == "data/map.dat": 
        for obs_hole in obstacle:
        	hole = []
        	for p in obs_hole:
	            p[0] = p[0]*zoom + translate[0]
	            p[1] = p[1]*zoom + translate[1]
	            hole.append(Point(p[0],p[1]))
	        cdt.add_hole(hole)
	        hole_arr.extend(hole)
         
    ##
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
    rcdtgrid = g.GraphReduction()
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
        if file_name == "data/dude.dat":
            for i in range(len(head_hole)):
              j = i+1 if i < len(head_hole) - 1 else 0
              x1 = int(head_hole[i][0])
              y1 = int(head_hole[i][1])
              x2 = int(head_hole[j][0])
              y2 = int(head_hole[j][1])
              line(screen, x1, y1, x2, y2, green)
            for i in range(len(chest_hole)):
              j = i+1 if i < len(chest_hole) - 1 else 0
              x1 = int(chest_hole[i][0])
              y1 = int(chest_hole[i][1])
              x2 = int(chest_hole[j][0])
              y2 = int(chest_hole[j][1])
              line(screen, x1, y1, x2, y2, green)

        if file_name == "data/map.dat":
        	for obs in obstacle:
	            for i in range(len(obs)):
	              j = i+1 if i < len(obs) - 1 else 0
	              x1 = int(obs[i][0])
	              y1 = int(obs[i][1])
	              x2 = int(obs[j][0])
	              y2 = int(obs[j][1])
	              line(screen, x1, y1, x2, y2, green)

        for i in range(len(vertexArr)):
        	for j in range(len(vertexArr)):
        		if(rcdtgrid[i][j] == 1000000007):
        			continue
        		line(screen, int(vertexArr[i].x), int(vertexArr[i].y), int(vertexArr[j].x), int(vertexArr[j].y), yellow)
              
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
    if len(sys.argv) == 5:
      file_name = sys.argv[1]
      tx = float(sys.argv[2])
      ty = float(sys.argv[3])
      zoom = float(sys.argv[4])
      main(file_name, [tx, ty], zoom)
      exit()
    
    print
    print("  Usage: filename translate-x translate-y zoom")
    print("Example: python test.py data/dude.dat 100 -200 1")
    print("         python test.py data/nazca_monkey.dat 400 300 4.5")  

