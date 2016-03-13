# pulsar4xgalaxy
POC Python script that generates a galaxy with customizable clustering parameters

Proof of Concept of a galaxy creation algorithm with customizable clustering;

The galaxy is divided into clusters, all nodes (i.e. systems) belongs to a cluster
The clusters are divided into different levels.
- All clusters of the same level has the same amount of nodes
- After all nodes has been created, the script loops over all nodes and determines how many links there should be from the node.
- When choosing the destination of the edge (JP link) it uses a cumulative probability distribution which is common for all nodes in clusters of the same level.
  The distribution determines how probable it is that the connection is
       a) A local connection within the same cluster
       b) The connection is made to a level 0 cluster
       c) level 1 cluster... etc.
  Examples:
         [0.7, 0.8, 1] - 70% chance for a local connection, 10% chance for a connection to a level0 cluster, 20% chance for a connection to a level1 cluster
         [0.8, 0.8, 1] - 80% local, 0% to level0, 20% to level1
         [0.5, 0.6, 0.7, 1] - 50% local, 10% lvl0, 10% lvl1, 30%lvl2
NOTE that for obvious reasons, the last number has to be 1

- The algorithm uses the same "dormant" jump point concept as Aurora does, i.e. it doesn't check whether the target node has any "available" edges before creating the edge to the node.
  The result of this is that the average number of links will be higher than what you'd expect from looking at the function that gives the number of edges for the nodes

You need to have installed GraphViz and pydot to run this script.

Output: A test.dot and a test.png file visualizing the generated galaxy

Things that could be added/improved on:
- Use some kind of distribution to determine number of nodes pr cluster (it's a static value now) Bell-curve perhaps?
- Add a check that determines if there's any unconnected nodes. If there is, either remove those nodes or run the algorithm over again.
- Use the proper method of calculating number of links out of a system. The current one doesn't take star size into account
