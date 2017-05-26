# -*- coding: utf-8 -*-
"""
Created on Fri May 26 21:47:56 2017

@author: User
"""

from gurobipy import *

# tested with Python 3.5.2 & Gurobi 7.0.1

mines = range(3+1) #you have 4 mines
years = range(4+1) #you have 5 years

Royalties = [5e6, 4e6, 4e6, 5e6] #roalities years
ExtractLimit = [2e6, 2.5e6, 1.3e6, 3e6] #extraction limit for years
OreQuality  = [1, .7, 1.5, .5] #ore quality for mines
BlendedQuality = [0.9, 0.8, 1.2, 0.6, 1.0] #quality target for years
discount = [(1/(1+1/10.0)) ** year for year in years] #this is the formulation for accumulate.
#discount 10 percent each year

mines_limit = 3
sell_price = 10


model = Model('Mining')

out = model.addVars(mines, years, name="output")
quan = model.addVars(years, name="quantity")
work = model.addVars(mines, years, vtype=GRB.BINARY, name="working")
open = model.addVars(mines, years, vtype=GRB.BINARY, name="open")


# At most three mines open each year
model.addConstrs((work.sum('*',year) <= mines_limit for year in years), "AtMost3Mines")

# Maintain Quality
model.addConstrs(
    (quicksum(OreQuality[mine]*out[mine, year] for mine in mines) == BlendedQuality[year]*quan[year]
     	for year in years), "Quality")

# Quantity produced equals output
model.addConstrs((out.sum('*',year) == quan[year] for year in years), "OutQty")

# Restrict ExtractLimit
#Modeled as described in the HP Williams book
model.addConstrs(
    (out[mine, year] <= ExtractLimit[mine]*work[mine, year]    for mine, year in out), "ExtractLimit")


# Mine Working => Mine Open
#Modeled as described in the HP Williams book
model.addConstrs((work[mine, year] <= open[mine, year] for mine, year in open), "WorkingOpen") 

# Mine Open in Year+1 => Mine was also open in Year
#Modeled as described in the HP Williams book
model.addConstrs(
    (open[mine, year+1] <= open[mine, year]
     for mine, year in open if year < years[-1]), "SubsequentOpen")

# Maximize Profit
obj = quicksum(sell_price*discount[year]*quan[year] for year in years) \
      - quicksum(Royalties[mine] * discount[year] * open[mine, year]
                 for mine, year in open)
model.setObjective(obj, GRB.MAXIMIZE)


model.optimize()
for v in model.getVars():
    if v.X != 0:
        print("%s %f" % (v.Varname, v.X))
        
model.write("mining-output.sol")        