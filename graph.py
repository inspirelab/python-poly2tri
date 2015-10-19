import numpy
import heapq
import metis
import networkx as nx
import random
import copy

class Graph:
	sz = 0
	grid = numpy.zeros((sz,sz), dtype=numpy.int)
	INF = 1000000007
	guard = []

	def __init__(self, n):
		self.sz = n
		self.grid = numpy.zeros((n, n), dtype=numpy.int)
		self.grid.fill(self.INF)

	def addEdge(self, i, j, dist):
		self.grid[i][j] = dist
		self.grid[j][i] = dist

	def removeEdge(self, i, j):
		self.grid[i][j] = self.INF
		self.grid[j][i] = self.INF

	def FloydWarshall(self):
		size = self.sz
		self.cost_matrix = numpy.zeros((size, size), dtype=numpy.int)
		self.path_matrix = numpy.zeros((size, size), dtype=numpy.int)
		self.cost_matrix.fill(self.INF)
		self.path_matrix.fill(-1)
		for i in range(size):
			for j in range(size):
				if(self.grid[i][j] != self.INF):
					self.cost_matrix[i][j] = self.grid[i][j]
					self.path_matrix[i][j] = i
		for k in range(size):
			for i in range(size):
				for j in range(size):
					if(self.cost_matrix[i][j] > self.cost_matrix[i][k] + self.cost_matrix[k][j]):
						self.cost_matrix[i][j] = self.cost_matrix[i][k] + self.cost_matrix[k][j]
						self.path_matrix[i][j] = self.path_matrix[k][j]
		# print self.cost_matrix
		# print self.path_matrix
		return (self.cost_matrix, self.path_matrix)

	def AddPathToGraph( self, start, end, gr, vertexList, guardFlag, guardCount):
		cur1 = self.path_matrix[start][end]
		cur2 = end
		while True:
			if guardFlag[cur2] :
				guardFlag[cur2] = False
				guardCount = guardCount - 1 

			vertexList.append(cur2)
			gr.addEdge(cur1, cur2, self.cost_matrix[cur1][cur2])
			
			cur2 = cur1
			cur1 = self.path_matrix[start][cur2]
			
			if (cur2 == start):
				break
		return guardCount
	def GraphReduction(self):
		smallest = self.INF
		mini = -1
		minj = -1
		redG = Graph(self.sz)
		vertexList = []
		prq = [] 

		guardFlag = numpy.zeros(self.sz, dtype=numpy.bool)
		guardFlag.fill(False)

		print self.guard
		for j in range(len(self.guard)):
			guardFlag[self.guard[j]] = True

		realGuardFlag = copy.copy(guardFlag)

		guardCount = len(self.guard)
		print "look" + str(guardCount)
		for i in range(len(self.guard)):
			for j in range(i+1, len(self.guard)):
				if (smallest > self.cost_matrix[i][j]):
					smallest = self.cost_matrix[i][j]
					mini = i
					minj = j
		guardCount = self.AddPathToGraph(mini, minj, redG, vertexList, guardFlag, guardCount)
		# print "LOOK HERE"
		# print self.guard
		prevsize = 0
		while guardCount != 0:
			for i in range(prevsize, len(vertexList)):
				for j in range(len(self.guard)):
					if (guardFlag[self.guard[j]]):
						heapq.heappush(prq, (self.cost_matrix[vertexList[i]][self.guard[j]],vertexList[i],self.guard[j]))
			
			prevsize = len(vertexList)
			el = heapq.heappop(prq)
			if (guardFlag[el[2]]):
				guardCount = self.AddPathToGraph(el[1], el[2], redG, vertexList, guardFlag, guardCount)

		mapping = []
		is_boundary = []
		for i in range(self.sz):
			for j in range(self.sz):
				if (redG.grid[i][j] != self.INF):
					if realGuardFlag[i] == False:
						is_boundary.append(True)
					else:
						is_boundary.append(False)
					mapping.append(i)
					break

		redGrid = numpy.zeros((len(mapping),len(mapping)), dtype=numpy.int)

		for i in range(len(mapping)):
			for j in range(len(mapping)):
				redGrid[i][j] = redG.grid[mapping[i]][mapping[j]]

		gvtxlist = []
		# for i in range(100):
			# gvtxlist.append(random.randint(0, 10))
		gvtxlist = self.getPartitions(redGrid, is_boundary, 3)
		print gvtxlist

		return (redG.grid, gvtxlist, mapping)

	def getPartitions(self, redG, is_boundary, num):
		pqlist = []
		boundarypushed = []
		gvtxlist = []
		visited = []

		for j in range(len(redG)):
			if is_boundary[j]:
				visited.append(True)
			else:
				visited.append(False)

		for i in range(num):
			pqlist.append([])
			boundarypushed.append(copy.copy(is_boundary))
			gvtxlist.append([])
		# startpt = range(len(redG))
		startpt = []
		print redG

		for i in range(len(is_boundary)):
			if len(startpt) == num:
				break
			if is_boundary[i]:
				continue
			startpt.append(i)
		print is_boundary

		# random.shuffle(startpt)
		for i in range(num):
			heapq.heappush(pqlist[i], (0, startpt[i],-1))
		print startpt
		while False in visited:
			cost = 0
			top  = 0
			# print visited
			for i in range(num):
				flag = False
				while True:
					if len(pqlist[i]) == 0:
						break
					print "partition", i
					cost, top, Boundary = heapq.heappop(pqlist[i])
					if visited[top] == False:
						flag = True
						if Boundary != -1:
							gvtxlist[i].append(Boundary)
						break
					else:
						if boundarypushed[i][top]:
							boundarypushed[i][top] = False
							for j in range(len(redG)):
								if redG[top][j] == self.INF or (visited[j] and not boundarypushed[i][j]):
									continue
								heapq.heappush(pqlist[i], (redG[top][j], j, top))
				if flag == True:
					if is_boundary[top] == False:
						gvtxlist[i].append(top)
					visited[top] = True
					for j in range(len(redG)):
						if redG[top][j] == self.INF or (visited[j] and not boundarypushed[i][j]):
							continue
						heapq.heappush(pqlist[i], (redG[top][j], j,-1))
						print redG[top][j], j, top

		parts = []
		for i in range(len(redG)):
			parts.append(-1)
		for i in range(num):
			for j in range(len(gvtxlist[i])):
				parts[gvtxlist[i][j]] = i

		return parts
