# -*- coding: utf-8 -*-
"""
Created on Tue May 16 15:04:39 2017

@author: Bui Xuan Toan
"""
import os
import xlrd

curdir = os.getcwd()
print(curdir)
curdir = os.chdir("D:/Toan/1. NCU Master Degree/Semester 4/Optimization\gurobiOptimization")
#print(curdir)
'''
get the book and sheet to read the data.
'''
book = xlrd.open_workbook(os.path.join(os.getcwd(), "data", "diet.xls"))
#print(book)
sh = book.sheet_by_name("Categories")

'''
readin the data.
categories is a list of nutritions.
minNutrition is a dictionary minNutrition{'nutrition': minValue}
maxNutritionis a dictionary minNutrition{'nutrition': maxValue}
'''
categories = []
minNutrition = {}
maxNutrition = {}
i = 1
while True:
    try:
        c = sh.cell_value(i, 0)
        categories.append(c)
        minNutrition[c] = sh.cell_value(i,1)
        maxNutrition[c] = sh.cell_value(i,2)
        i = i + 1
    except IndexError:
        break
    
#print(categories)
#print(minNutrition)
#print(maxNutrition)

'''
read the data.
foods is a list of food.
cost is a dictionary{'food': cost}
'''
sh = book.sheet_by_name("Foods")
foods = []
cost = {}
i = 1
while True:
    try:
        f = sh.cell_value(i, 0)
        foods.append(f)
        cost[f] = sh.cell_value(i,1)
        i = i + 1
    except IndexError:
        break
    
#print(foods)
#print(cost)

'''
reading the Nutrition  data.
nutritionValues is a dictionary nutritionValues{('food', 'category'): value}
'''
sh = book.sheet_by_name("Nutrition")
nutritionValues = {}
i = 1
for food in foods:
    j = 1
    for cat in categories:
        nutritionValues[food,cat] = sh.cell_value(i,j)
        j += 1
    i += 1

'''
improt dietmodel and solve the problem.
'''
import dietmodel
dietmodel.solve(categories, minNutrition, maxNutrition,
                foods, cost, nutritionValues)