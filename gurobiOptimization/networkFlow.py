# -*- coding: utf-8 -*-
"""
Created on Mon May 22 16:11:21 2017

@author: Bui Xuan Toan
"""

# Solve a multi-commodity flow problem.  Two products ('Pencils' and 'Pens')
# are produced in 2 cities ('Detroit' and 'Denver') and must be sent to
# warehouses in 3 cities ('Boston', 'New York', and 'Seattle') to
# satisfy demand ('inflow[h,i]').
#
# Flows on the transportation network must respect arc capacity constraints
# ('capacity[i,j]'). The objective is to minimize the sum of the arc
# transportation costs ('cost[i,j]').

from gurobipy import *

# Model data

commodities = ['Pencils', 'Pens'] #2 commodity
nodes = ['Detroit', 'Denver', 'Boston', 'New York', 'Seattle'] #5 cities

#Note: 2 plants in Detroit and Denver
#Detroit send to ['Boston', 'NewYork', 'Seattle'] 
#Denver send to ['Boston', 'NewYork', 'Seattle']
#totally we have 3 market.
arcs, capacity = multidict({
  ('Detroit', 'Boston'):   100,
  ('Detroit', 'New York'):  80,
  ('Detroit', 'Seattle'):  120,
  ('Denver',  'Boston'):   120,
  ('Denver',  'New York'): 120,
  ('Denver',  'Seattle'):  120 }) #with multidict arcs is list, capacity is a dict.

#transportation cost betweent plant and markets.
cost = {
  ('Pencils', 'Detroit', 'Boston'):   10,
  ('Pencils', 'Detroit', 'New York'): 20,
  ('Pencils', 'Detroit', 'Seattle'):  60,
  ('Pencils', 'Denver',  'Boston'):   40,
  ('Pencils', 'Denver',  'New York'): 40,
  ('Pencils', 'Denver',  'Seattle'):  30,
  ('Pens',    'Detroit', 'Boston'):   20,
  ('Pens',    'Detroit', 'New York'): 20,
  ('Pens',    'Detroit', 'Seattle'):  80,
  ('Pens',    'Denver',  'Boston'):   60,
  ('Pens',    'Denver',  'New York'): 70,
  ('Pens',    'Denver',  'Seattle'):  30 }

inflow = {
  ('Pencils', 'Detroit'):   50,#plant produce
  ('Pencils', 'Denver'):    60,
  ('Pencils', 'Boston'):   -50,#market demand
  ('Pencils', 'New York'): -50,
  ('Pencils', 'Seattle'):  -10,
  ('Pens',    'Detroit'):   60,
  ('Pens',    'Denver'):    40,
  ('Pens',    'Boston'):   -40,
  ('Pens',    'New York'): -30,
  ('Pens',    'Seattle'):  -30 }

# Create optimization model
m = Model('netflow')

# Create variables
flow = m.addVars(commodities, arcs, obj=cost, name="flow")

# Arc capacity constraints
# Note sum over commodity for each arc[i,j], arc is a list of tuple
m.addConstrs(
    (flow.sum('*',i,j) <= capacity[i,j] for i,j in arcs), "cap")

# Equivalent version using Python looping
# for i,j in arcs:
#   m.addConstr(sum(flow[h,i,j] for h in commodities) <= capacity[i,j],
#               "cap[%s,%s]" % (i, j))


# Flow conservation constraints
#balance constraint for each commodity h for each node j
#Note: inflow[h,j] is the produce or demand for each node.
#Note: I love this cosntraints
m.addConstrs(
    (flow.sum(h,'*',j) + inflow[h,j] == flow.sum(h,j,'*')
    for h in commodities for j in nodes), "node")
# Alternate version:
# m.addConstrs(
#   (quicksum(flow[h,i,j] for i,j in arcs.select('*',j)) + inflow[h,j] ==
#     quicksum(flow[h,j,k] for j,k in arcs.select(j,'*'))
#     for h in commodities for j in nodes), "node")

# Compute optimal solution
m.optimize()

# Print solution
if m.status == GRB.Status.OPTIMAL:
    solution = m.getAttr('x', flow)
    for h in commodities:
        print('\nOptimal flows for %s:' % h)
        for i,j in arcs:
            if solution[h,i,j] > 0:
                print('%s -> %s: %g' % (i, j, solution[h,i,j]))
