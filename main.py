import gurobipy as gp
from gurobipy import GRB
from gurobipy import quicksum, Model

# Se abre el archivo "costos.csv"
with open("costos.csv", "r") as costos:
    data = costos.readlines()
    # Se crean listas con cada uno de los parámetros del archivo
    c_i = list()
    for i in data[0].split(","):
        c_i.append(int(i.strip()))
    F_i = list()
    for i in data[1].split(","):
        F_i.append(int(i.strip()))
    h_k = list()
    for k in data[2].split(","):
        h_k.append(int(k.strip()))
    C = int(data[3].strip())

# Se obtienen los conjuntos y el parámetro M con la cantidad de parámetros según enunciado
N = range(len(c_i))
M = int(len(c_i)/2)
K = range(len(h_k))

# N = range(1, len(c_i) + 1)
# K = range(1, len(h_k) + 1)

# Se abre el archivo "ofertas.csv"
with open("ofertas.csv", "r") as ofertas:
    data = ofertas.readlines()
    # Se guardan las ofertas en una lista
    O_i = list()
    for i in data[0].split(","):
        O_i.append(int(i.strip()))

# Se abre el archivo "demandas.csv"
with open("demandas.csv", "r") as demandas:
    data = demandas.readlines()
    # Se guarda el conjunto L dado que es la cantidad de filas de "demandas.csv"
    L = range(len(data))
    # Se guarda el conjunto T que corresponde a las columnas de "demandas.csv"
    T = range(len(data[0].split(",")))
    # Se guarda d_l_t en una lista para que al buscar d_l_t[x][y] x corresponda al índice l e y al índice t
    d_l_t = list()
    for l in data:
        fila = list()
        for t in l.split(","):
            fila.append(int(t.strip()))
        d_l_t.append(fila)

# Se abre el archivo "bodegas.csv"
with open("bodegas.csv", "r") as bodegas:
    data = bodegas.readlines()
    # Se guardan las capacidades y stock inicial de cada bodega en listas
    Q_k = list()
    s_k_0 = list()
    for k in data[0].split(","):
        Q_k.append(int(k.strip()))
    for k in data[1].split(","):
        s_k_0.append(int(k.strip()))

# Se abre el archivo "distancias1.csv"
with open("distancias1.csv", "r") as distancias1:
    data = distancias1.readlines()
    # Se guardará d1_i_k en una lista de listas tal que el primer índice corresponda a i y el segundo a k
    d1_i_k = list()
    for i in data:
        fila = list()
        for k in i.split(","):
            fila.append(int(k.strip()))
        d1_i_k.append(fila)
    
# Se abre el archivo "distancias2.csv"
with open("distancias2.csv", "r") as distancias2:
    data = distancias2.readlines()
    # Se guardará d2_i_l en una lista de listas tal que el primer índice corresponda a i y el segundo a l
    d2_i_l = list()
    for i in data:
        fila = list()
        for l in i.split(","):
            fila.append(int(l.strip()))
        d2_i_l.append(fila)

# Se abre el archivo "distancias3.csv"
with open("distancias3.csv", "r") as distancias3:
    data = distancias3.readlines()
    # Se guardará d3_k_l en una lista de listas tal que el primer índice corresponda a k y el segundo a l
    d3_k_l = list()
    for k in data:
        fila = list()
        for l in k.split(","):
            fila.append(int(l.strip()))
        d3_k_l.append(fila)
          
model = Model()

# Variables
X_i_t = model.addVars(N, T, vtype = GRB.INTEGER, name = "X_i_t")
Z_i = model.addVars(N, vtype = GRB.BINARY, name = "Z_i")
s_k_t = model.addVars(K, T, vtype = GRB.INTEGER, name = "s_k_t")
y_i_k_t = model.addVars(N, K, T, vtype = GRB.INTEGER, name = "y_i_k_t")
w_i_l_t = model.addVars(N, L, T, vtype = GRB.INTEGER, name = "w_i_l_t")
v_k_l_t = model.addVars(K, L, T, vtype = GRB.INTEGER, name = "v_k_l_t")

## Resrticciones
model.addConstr(quicksum(Z_i[i] for i in N) == M)
model.addConstrs(X_i_t[i, t] <= O_i[i] * Z_i[i] for i in N for t in T)
model.addConstrs(s_k_t[k, t] <= Q_k[k] for k in K for t in T)
model.addConstrs(quicksum(y_i_k_t[i, k, t] for k in K) + quicksum(w_i_l_t[i, l, t] for l in L) == X_i_t[i, t] for t in T for i in N)
model.addConstrs(quicksum(w_i_l_t[i, l, t] for i in N) + quicksum(v_k_l_t[k, l, t] for k in K) == d_l_t[l][t] for t in T for l in L)
model.addConstrs(s_k_t[k, t] == s_k_t[k, t - 1] + quicksum(y_i_k_t[i, k, t] for i in N) - quicksum(v_k_l_t[k, l, t] for l in L) for t in range(1, T[-1]) for k in K)
# Naturaleza de las variables
model.addConstrs((X_i_t[i, t] >= 0) for i in N for t in T)
model.addConstrs((s_k_t[k, t] >= 0) for k in K for t in T)
model.addConstrs((y_i_k_t[i, k, t] >= 0) for i in N for k in K for t in T)
model.addConstrs((w_i_l_t[i, l, t] >= 0) for i in N for l in L for t in T)
model.addConstrs((v_k_l_t[k, l, t] >= 0) for k in K for l in L for t in T)

# Función objetivo
f_objetivo = quicksum(c_i[i] * X_i_t[i, t] for i in N for t in T) + quicksum(F_i[i] * Z_i[i] for i in N) + quicksum(h_k[k] * s_k_t[k, t] for t in T for k in K) \
    + C * quicksum((quicksum(d1_i_k[i,k] * y_i_k_t[i, k, t] for i in N for k in K) + quicksum(d2_i_l[i, l] * w_i_l_t[i, l, t] for i in N for l in L) + quicksum(v_k_l_t[k, l, t] * d3_k_l[k, l] for k in K for l in L)) for t in T)

model.update()
model.setObjective(f_objetivo, GRB.MINIMIZE)
model.optimize()


# Añadir procesamiento de datos
if model.status == GRB.OPTIMAL:
    print(model.objVal)

