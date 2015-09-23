import numpy
import heapq
import metis
import networkx as nx

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
		print self.cost_matrix
		print self.path_matrix
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
			
			if (cur1 != start):
				break;
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

		for j in range(len(self.guard)):
			guardFlag[self.guard[j]] = True
			
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

		for i in range(self.sz):
			for j in range(self.sz):
				if (redG.grid[i][j] != self.INF):
					mapping.append(i)
					break


		adjList = []
		for i in range(len(mapping)):
			arrayi = []
			for j in range(self.sz):
				if (redG.grid[i][j] != self.INF):
					el = mapping.index(j) + 1
					arrayi.append((el, redG.grid[i][j]))
			adjList.append(tuple(arrayi))
		print adjList
		# G = metis.adjlist_to_metis(adjList)
		G = adjList
		(edgecuts, parts) = metis.part_graph(G, 3)
		colors = ['red','blue','green']
		print parts
		# for i, p in enumerate(parts):
		# 	G.node[i]['color'] = colors[p]
		# nx.write_dot(G, 'example.dot')
		print redG.grid
		return redG.grid



