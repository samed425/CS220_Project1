import gurobipy as gp
from gurobipy import GRB


def read_graph(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    num_vertices, num_edges, num_colors = map(int, lines[0].split())
    vertices = list(range(1, num_vertices + 1))
    graph = {v: set() for v in vertices}
    for line in lines[1:num_edges+1]:
        u, v = map(int, line.split())
        graph[u].add(v)
        graph[v].add(u)
    edges = [(u, v) for u in range(1, num_vertices + 1) for v in graph[u] if u < v]

    affinity_edges = []
    for line in lines[num_edges + 1:]:
        x, y = map(int, line.split())
        affinity_edges.append((x, y))
    return vertices, edges, affinity_edges


def chromatic_num(V, E, K):
    model = gp.Model("graph_coloring")
    x = model.addVars(V, K, vtype=GRB.BINARY, name="x")
    y = model.addVars(K, vtype=GRB.BINARY, name="y")
    model.addConstrs((x.sum(i, '*') == 1 for i in V), name="vertex_color_assignment")
    model.addConstrs((x[i, k] + x[j, k] <= y[k] for i, j in E for k in range(K)), name="edge_color_assignment")
    model.setObjective(y.sum('*'), GRB.MINIMIZE)
    model.optimize()
    print(int(model.ObjVal))
    return int(model.ObjVal)

def aff_num(V, E, A, K):
    print(E)
    model = gp.Model("affinity_number")
    length = len(A)
    x = model.addVars(V, K, vtype=GRB.BINARY, name="x")
    z = model.addVars(length, K, vtype=GRB.BINARY, name="z")
    model.addConstrs((x.sum(i, '*') == 1 for i in V), name="vertex_color_assignment")
    model.addConstrs((x[i, k] + x[j, k] <= 1 for i, j in E for k in range(K)), name="edge_color_assignment")

    model.addConstrs(((x[A[i][0], k] * x[A[i][1], k]) == z[i,k] for i in range(length) for k in range(K)), name="aff_edge_satisfied")

    model.setObjective(z.sum('*', '*'), GRB.MAXIMIZE)
    #model.write("myfile.lp")
    model.optimize()
    aff = int(model.ObjVal)
    all_vars = model.getVars()
    values = model.getAttr("X", all_vars)
    names = model.getAttr("VarName", all_vars)

    #model.printAttr('x')
    file = open(r"output.txt", "w+")
    file.write(str(K))
    file.write("\n")
    file.write(str(aff))
    for name, val in zip(names, values):
        if (val > 0 and name[0] == "x"):
            index = name.find(",")
            file.write(f"\n{name[index+1]}")
    file.close()
    return aff


def main(path, K):
    V,E,A = read_graph(path)
    color = chromatic_num(V, E, K)
    aff_num(V, E, A, color)

file_path = ("sample_input/sample_4.txt")  # Replace with the actual path to your graph file
K = 12  # Replace with the desired value of K
main(file_path, K)
