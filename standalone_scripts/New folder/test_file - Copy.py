# save as test_gurobi.py and run:  python test_gurobi.py
import gurobipy as gp
from gurobipy import GRB

def main():
    print("gurobipy version:", gp.__version__)

    try:
        # Build a tiny LP:  maximize x + y
        # s.t. x + 2y <= 4,  x <= 3,  x,y >= 0
        m = gp.Model("smoketest")

        # Optional: write a solver log to inspect license info
        m.Params.LogFile = "gurobi_smoketest.log"

        x = m.addVar(lb=0.0, name="x")
        y = m.addVar(lb=0.0, name="y")

        m.addConstr(x + 2*y <= 4, name="c1")
        m.addConstr(x <= 3,       name="c2")

        m.setObjective(x + y, GRB.MAXIMIZE)

        m.optimize()

        if m.Status == GRB.OPTIMAL:
            print("\nStatus: OPTIMAL")
            print("Obj value:", m.ObjVal)
            print("x =", x.X, " y =", y.X)
        else:
            print("\nStatus code:", m.Status, "(not OPTIMAL)")
            # If needed, write the model for debugging:
            m.write("smoketest.lp")

    except gp.GurobiError as e:
        print("\nGurobiError:", e.errno, str(e))
    except Exception as e:
        print("\nGeneral error:", str(e))

if __name__ == "__main__":
    main()
