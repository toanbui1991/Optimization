# -*- coding: utf-8 -*-
"""
Created on Wed May 24 16:18:31 2017

@author: User
"""

from gurobipy import *

# tested with Python 3.5.2 & Gurobi 7.0.1

time_periods = ["January", "February", "March", "April", "May", "June"]

oils = ["VEG1", "VEG2", "OIL1", "OIL2", "OIL3"]

prices = tupledict({
	('January', 'VEG1'): 110,
	('January', 'VEG2'): 120,
	('January', 'OIL1'): 130,
	('January', 'OIL2'): 110,
	('January', 'OIL3'): 115,
	('February', 'VEG1'): 130,
	('February', 'VEG2'): 130,
	('February', 'OIL1'): 110,
	('February', 'OIL2'): 90,
	('February', 'OIL3'): 115,
	('March', 'VEG1'): 110,
	('March', 'VEG2'): 140,
	('March', 'OIL1'): 130,
	('March', 'OIL2'): 100,
	('March', 'OIL3'): 95,
	('April', 'VEG1'): 120,
	('April', 'VEG2'): 110,
	('April', 'OIL1'): 120,
	('April', 'OIL2'): 120,
	('April', 'OIL3'): 125,
	('May', 'VEG1'): 100,
	('May', 'VEG2'): 120,
	('May', 'OIL1'): 150,
	('May', 'OIL2'): 110,
	('May', 'OIL3'): 105,
	('June', 'VEG1'): 90,
	('June', 'VEG2'): 100,
	('June', 'OIL1'): 140,
	('June', 'OIL2'): 80,
	('June', 'OIL3'): 135
})


hardness = {"VEG1": 8.8, "VEG2": 6.1, "OIL1": 2.0, "OIL2": 4.2, "OIL3": 5.0}

price = 150
IStore = 500
vegCapa = 200
oilCapa = 250

hardness_lb = 3
hardness_ub = 6
store_pricing = 5
min_oil_used = 20


model = Model('Food Manufacture II')
# Quantity of food produced in each period
food = model.addVars(time_periods, name="Food")
# Quantity bought of each product in each period
buy = model.addVars(time_periods, oils, name = "Buy")
# Quantity used of each product  in each period
use = model.addVars(time_periods, oils, name = "Use")
# Quantity stored of each product  in each period
store = model.addVars(time_periods, oils, name = "Store")
# binary variables =1, if use>0
d = model.addVars(time_periods, oils, vtype=GRB.BINARY, name = "d")

#Initial Balance
model.addConstrs((IStore + buy[time_periods[0], oil] ==
     use[time_periods[0], oil] + store[time_periods[0], oil] for oil in oils), "Initial_Balance")

# Balance
model.addConstrs(
    (store[time_periods[time_periods.index(time_period)-1], oil] + buy[time_period, oil] ==
     	use[time_period, oil] + store[time_period, oil] for oil in oils for time_period in time_periods 
     	if time_period != time_periods[0]), "Balance")

#End Balance
model.addConstrs((store[time_periods[-1], oil] == IStore for oil in oils),
                 "End_Balance")

# Capacity1 & Capacity2
model.addConstrs(
    (quicksum(use[time_period, oil] for oil in oils if "VEG" in oil) <= vegCapa
     	for time_period in time_periods), "Capacity_Veg")
model.addConstrs(
    (quicksum(use[time_period, oil] for oil in oils if "OIL" in oil) <= oilCapa
     	for time_period in time_periods), "Capacity_Oil")

# Hardness
model.addConstrs(
    (quicksum(hardness[oil] * use[time_period, oil] for oil in oils)
     	>= hardness_lb * food[time_period] for time_period in time_periods), "Hardness_lower")
model.addConstrs(
    (quicksum(hardness[oil] * use[time_period, oil] for oil in oils)
     	<= hardness_ub * food[time_period] for time_period in time_periods), "Hardness_upper")

# Conserve
model.addConstrs((use.sum(time_period) == food[time_period]
                  for time_period in time_periods), "Conserve")

# Cond 1 (force condition: d=1 -> use>0)
#note: d.sum(time_period) = d.sum(time_period, '*') that means  you fix each period and
#sum over all oils.
model.addConstrs((d.sum(time_period) <= 3 for time_period in time_periods),"Cond1")


# Cond 2
##### Pure MIP formulation
#Note: you have already know how to use for and if in gurobi.
#if you use a oil then it should be larger than a miminum number.
model.addConstrs(
	(use[time_period, oil] - min_oil_used * d[time_period, oil] >= 0
	 	for time_period in time_periods for oil in oils), "Cond2")
#but it can not go over the capacity.
model.addConstrs(
	(use[time_period, oil] - vegCapa * d[time_period, oil] <= 0
	 	for time_period in time_periods
	 	for oil in oils if "VEG" in oil), "Cond2a")
#but it can not go over the capacity.
model.addConstrs(
	(use[time_period, oil] - oilCapa * d[time_period, oil] <= 0
	 	for time_period in time_periods
	 	for oil in oils if "OIL" in oil), "Cond2a")

# Cond 3 If Veg1 or Veg2 are used then Oil3 must also be used in this month
##### Pure MIP formulation
model.addConstrs((d[time_period, "VEG1"] <= d[time_period, "OIL3"] for time_period in time_periods),"Cond3a")
model.addConstrs((d[time_period, "VEG2"] <= d[time_period, "OIL3"] for time_period in time_periods), "Cond3b")


# Objective
#Note: price=constance,
#food[] quantity of product produce in each period (just one product).
#buy{('period', 'oil'): quantity}
#prices{('timeperiod', 'oil') : price}
#do you understand the prod() method? yes i do
#store{('period', 'oil'): quantity} 

obj = price*food.sum() - buy.prod(prices) - store_pricing*store.sum()
model.setObjective(obj, GRB.MAXIMIZE) # maximize profit


# x = m.addVars([(1,2), (1,3), (2,3)])
#  coeff = dict([((1,2), 2.0), ((1,3), 2.1), ((2,3), 3.3)])
#  expr = x.prod(coeff) # LinExpr: 2.0 x[1,2] + 2.1 x[1,3] + 3.3 x[2,3]
#  expr = x.prod(coeff, '*', 3) # LinExpr: 2.1 x[1,3] + 3.3 x[2,3]

model.optimize()
for v in model.getVars():
    if v.X != 0:
        print("%s %f" % (v.Varname, v.X))
        
model.write("food-manufacture-ii-output.sol")

       