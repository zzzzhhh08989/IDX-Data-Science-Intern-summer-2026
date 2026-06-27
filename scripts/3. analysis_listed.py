#add latest dfyyyymm
#add to frames


# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import pandas as pd
import numpy as np
import datetime

import csv
import calendar



df20222023 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing20220101_20231231.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202401 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202401.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202402 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202402.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202403 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202403.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202404 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202404.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202405 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202405.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202406 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202406.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202407 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202407.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202408 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202408.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202409 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202409.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202410 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202410.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202411 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202411.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202412 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202412.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202501 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202501.csv", encoding = "ISO-8859-1") # df is Pandas dataframe
df202502 = pd.read_csv("/Users/idxexchange/Desktop/crmls/CRMLSListing202502.csv", encoding = "ISO-8859-1") # df is Pandas dataframe

frames=[df20222023,df202401,df202402,df202403,df202404,df202405, df202406, df202407, df202408, df202409, df202410, df202411, df202412, df202501, df202502]
combine=pd.concat(frames)

main=combine.copy()

main= main[main.PropertyType=='Residential']
#main= main[main.PropertySubType=='SingleFamilyResidence']



###########

newlistings=main.copy()
newlistings.to_csv('/Users/idxexchange/Desktop/crmls/newlistings.csv', index=False)



