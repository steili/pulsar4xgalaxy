# Proof of Concept of a galaxy creation algorithm with customizable clustering;
#
# The galaxy is divided into clusters, all nodes (i.e. systems) belongs to a cluster
# The clusters are divided into different levels.
# - All clusters of the same level has the same amount of nodes
# - After all nodes has been created, the script loops over all nodes and determines how many links there should be from the node.
# - When choosing the destination of the edge (JP link) it uses a cumulative probability distribution which is common for all nodes in clusters of the same level.
#   The distribution determines how probable it is that the connection is
#        a) A local connection within the same cluster
#        b) The connection is made to a level 0 cluster
#        c) level 1 cluster... etc.
#   Examples:
#          [0.7, 0.8, 1] - 70% chance for a local connection, 10% chance for a connection to a level0 cluster, 20% chance for a connection to a level1 cluster
#          [0.8, 0.8, 1] - 80% local, 0% to level0, 20% to level1
#          [0.5, 0.6, 0.7, 1] - 50% local, 10% lvl0, 10% lvl1, 30%lvl2
# NOTE that for obvious reasons, the last number has to be 1
#
# - The algorithm uses the same "dormant" jump point concept as Aurora does, i.e. it doesn't check whether the target node has any "available" edges before creating the edge to the node.
#   The result of this is that the average number of links will be higher than what you'd expect from looking at the function that gives the number of edges for the nodes
#
# You need to have installed GraphViz and pydot to run this script.
#
# Output: A test.dot and a test.png file visualizing the generated galaxy
#
# Things that could be added/improved on:
# - Use some kind of distribution to determine number of nodes pr cluster (it's a static value now) Bell-curve perhaps?
# - Add a check that determines if there's any unconnected nodes. If there is, either remove those nodes or run the algorithm over again.
# - Use the proper method of calculating number of links out of a system. The current one doesn't take star size into account

from collections import defaultdict
from itertools import chain
import random
import pydot
import subprocess

fdp_path = r'c:\Program Files (x86)\Graphviz2.38\bin\fdp.exe'

class Node:
    def __init__(self, n, cluster, galaxy):
        self.n = n
        self.cluster = cluster
        self.galaxy = galaxy
        self.edges = set()

    def create_edges(self):
        n_edges = self.get_number_of_edges()
        remaining_edges = n_edges - len(self.edges)
        if remaining_edges > 0:
            for _ in range(remaining_edges):
                edge = self.galaxy.get_edge_for_node(from_node=self)
                edge.edges.add(self)
                self.edges.add(edge)

    @staticmethod
    def get_number_of_edges():
        if random.random() < 0.1:
            return 1
        if random.random() < 0.4:
            return 2
        for i in range(3, 10):
            if random.random() < 0.7:
                return i
        return 10 # For simplicity sake, use a hard limit of 10 edges

    def __repr__(self):
        return u'Node {} in cluster {}'.format(self.n, self.cluster)


class Cluster:
    def __init__(self, n, lvl, n_nodes, probs):
        self.n = n
        self.lvl = lvl
        self.n_nodes = n_nodes
        self.probs = probs
        self.nodes = []

    def __repr__(self):
        return u'C{}_LVL{}'.format(self.n, self.lvl)

class Galaxy:
    def __init__(self, clusters_by_lvl):
        self.clusters = defaultdict(list)
        self.max_lvl = max(clusters_by_lvl.keys())
        self.nodes = []
        self.create_clusters(clusters_by_lvl)

    def create_clusters(self, clusters_by_lvl):
        n = 0
        for lvl, details in clusters_by_lvl.items():
            for _ in range(details['n']):
                self.clusters[lvl].append(Cluster(n, lvl, details['nodes_per_cluster'], details['cum_prob']))
                n += 1

    def create_nodes(self):
        n = 0
        for cluster in chain(*self.clusters.values()):
            for i in range(cluster.n_nodes):
                cluster.nodes.append(Node(n, cluster, self))
                n+= 1
            self.nodes.extend(cluster.nodes)

    def create_edges(self):
        for n in self.nodes:
            n.create_edges()

    def get_edge_for_node(self, from_node):
        p0 = random.random()
        cum_probs_iter = iter(from_node.cluster.probs)
        candidates = []

        if p0 < next(cum_probs_iter):
            # Check for a self-connection first - filter out the origin node.
            candidates = [node for node in from_node.cluster.nodes if node != from_node]

        else:
            for cluster_lvl, p in enumerate(cum_probs_iter):
                if p0 < p:
                    # Filter out the nodes from the from_node's cluster (it only has to be done for clusters at the same level as the from_node's cluster)
                    clusters = [c for c in self.clusters[cluster_lvl] if c != from_node.cluster]
                    for c in clusters:
                        candidates.extend(c.nodes)
                    break

        assert(len(candidates) > 0)
        return random.choice(candidates)

    def build_graph(self):
        pass


if __name__ == '__main__':
    # cum_prob is the cumulative probability distribution of which cluster edges connect to. They should be ordered like this:
    #   - First value is the prob of a self connection
    #   - Next value is prob of a connection to the lvl0 cluster
    #   - Next is lvl1 cluster etc.
    # The last value has to be 1 obviously
    # If there's only 1 cluster in a level, make sure that the prob to connect to another cluster at the same lvl is 0
    g = Galaxy(
        {
            0: {'n': 1, 'nodes_per_cluster': 20, 'cum_prob': [1]},
            1: {'n': 6, 'nodes_per_cluster': 10, 'cum_prob': [0.70, 0.90, 1]},
        }
    )
    g.create_nodes()
    g.create_edges()
    graph = pydot.Dot(graph_type='graph')
    for cluster in chain(*g.clusters.values()):
        graph_cluster = pydot.Cluster(repr(cluster))
        for node in cluster.nodes:
            graph_cluster.add_node(pydot.Node(str(node.n)))
        graph.add_subgraph(graph_cluster)

    for node in g.nodes:
        for e in node.edges:
            graph.add_edge(pydot.Edge(str(node.n), str(e.n)))
            e.edges.remove(node)

    graph.write('test.dot', format='raw')
    subprocess.call(r'"{}" -Tpng test.dot -o "test.png"'.format(fdp_path))
