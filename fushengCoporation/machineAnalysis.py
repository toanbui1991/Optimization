# -*- coding: utf-8 -*-
"""
Created on Wed May 17 21:42:55 2017

@author: User
"""

import os
import xlrd
import pandas as pd
import matplotlib as plt

print(os.getcwd())
os.chdir('D:\\Toan\\1. NCU Master Degree\\Semester 4\\Optimization\\fushengCoporation') #you need \\(2).
print(os.getcwd())


book = xlrd.open_workbook(os.path.join(os.getcwd(), "data", "FushengCorporationData2.xlsx"))
sheet1 = book.sheet_by_index(0) #find sheet want to read.

#reading machines name
machines = []
row = 1 #colum you want to read.
while True:
    try:
        cellVal = sheet1.cell_value(row,0)
        machines.append(cellVal)
        row +=1
    except IndexError:
        break
print(machines) #clear the invalid cell if it has invalid machine.

#reading operations name.
models = []
row = 1
while True:
    try: 
        cellVal = sheet1.cell_value(row, 3)
        models.append(cellVal)
        row += 1
    except IndexError:
        break
print(models)

#read demand.
demands = []
row = 1
while True:
    try:
        cellVal = sheet1.cell_value(row, 5)
        demands.append(cellVal)
        row +=1
    except IndexError:
        break

print(demands)


#creat dataframe.
temp = list(zip(machines, models, demands))
df = pd.DataFrame(temp, columns = ['machines', 'models', 'demands'])
print(df.head(6))

#grouping the data.
groupData = df.groupby('machines').sum()
print(groupData.head(6))

#draw the group data.
groupData.plot.bar()




