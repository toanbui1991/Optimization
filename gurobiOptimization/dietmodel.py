# -*- coding: utf-8 -*-
"""
Created on Tue May 16 15:36:48 2017

@author: Bui Xuan Toan
"""

from gurobipy import *


def solve(categories, minNutrition, maxNutrition, foods, cost,
          nutritionValues):
    # Model
    m = Model("diet") 

    # Create decision variables for the nutrition information,
    # which we limit via bounds
    nutrition = m.addVars(categories, lb=minNutrition, ub=maxNutrition, name="nutrition")

    # Create decision variables for the foods to buy
    buy = m.addVars(foods, name="buy")

    # The objective is to minimize the costs
    m.setObjective(buy.prod(cost), GRB.MINIMIZE)

    # Nutrition constraints
    m.addConstrs(
        (quicksum(nutritionValues[f,c] * buy[f] for f in foods) == nutrition[c]
         for c in categories), "_")


    def printSolution():
        if m.status == GRB.Status.OPTIMAL:
            print('\nCost: %g' % m.objVal)
            print('\nBuy:')
            buyx = m.getAttr('x', buy)
            nutritionx = m.getAttr('x', nutrition)
            for f in foods:
                if buy[f].x > 0.0001:
                    print('%s %g' % (f, buyx[f]))
            print('\nNutrition:')
            for c in categories:
                print('%s %g' % (c, nutritionx[c]))
        else:
            print('No solution')

    # Solve
    m.optimize()
    printSolution()

    print('\nAdding constraint: at most 6 servings of dairy')
    m.addConstr(buy.sum(['milk','ice cream']) <= 6, "limit_dairy")

    # Solve
    m.optimize()
    printSolution() 

