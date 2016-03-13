# pulsar4xgalaxy

Proof of Concept of a galaxy creation algorithm with customizable clustering

## Short description
The galaxy is divided into clusters, all nodes (i.e. systems) belongs to a cluster
The clusters are divided into different levels.
- All clusters of the same level has the same amount of nodes
- After all nodes has been created, the script loops over all nodes and determines how many links there should be from each node.
- When choosing the destination of the edge (JP link) it uses a (customizable) cumulative probability distribution which is common for all nodes in clusters of the same level.
- The distribution determines how probable it is that the connection is
    1. A local connection within the same cluster
    2. A connection to a cluster of level 0
    3. A connection to a cluster of level 1, etc.

- **Examples**:
    - `[0.7, 0.8, 1]` - 70% prob. for a local connection, 10% prob for a lvl0 cluster connection, 20% prob for a lvl1 cluster connection
    - `[0.8, 0.8, 1]` - 80% local, 0% to level0, 20% to level1
    - `[0.5, 0.6, 0.7, 1]` - 50% local, 10% lvl0, 10% lvl1, 30%lvl2
    - *Note that the last number has to be 1.*

- The algorithm uses the same "dormant" jump point concept as Aurora does, i.e. it doesn't check whether the target node has any "available" edges before creating the edge to the node.
  The result of this is that the average number of links will be higher than what you'd expect from looking at the function that gives the number of edges for the nodes

**Cluster definition:**

From `graphgen.py`: 

    g = Galaxy(
            {
                0: {'n': 1, 'nodes_per_cluster': 20, 'cum_prob': [1]},
                1: {'n': 3, 'nodes_per_cluster': 10, 'cum_prob': [0.70, 0.90, 1]},
                2: {'n': 6, 'nodes_per_cluster': 10, 'cum_prob': [0.70, 0.80, 0.90, 1]},
                3: {'n': 6, 'nodes_per_cluster': 10, 'cum_prob': [0.50, 0.50, 0.75, 1]},
                4: {'n': 6, 'nodes_per_cluster': 10, 'cum_prob': [0.50, 0.50, 0.50, 0.75, 1]},
            }
        )

Each entry in the dictionary describes one cluster level.

 - `n` - Number of clusters of this level
 - `nodes_per_cluster` - Number of nodes per cluster
 - `cum_prob` - Cumulative probability of which cluster level links from this cluster level should be directed to (as described above)

## Requirements
You need to have installed GraphViz and pydot to run this script.

## Output

Output: A test.dot and a test.png file visualizing the generated galaxy

## Future work

- Use some kind of distribution to determine number of nodes pr cluster (it's a static value now) Bell-curve perhaps?
- Add a check that determines if there's any unconnected nodes. If there is, either remove those nodes or run the algorithm over again.
- Use the proper method of calculating number of links out of a system. The current one doesn't take star size into account
