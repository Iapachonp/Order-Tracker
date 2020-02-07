%matplotlib inline
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings                                  # modo `no molestar`
warnings.filterwarnings('ignore')
import plotly.graph_objects as go               # plot library
import dash_core_components                      #DASH library

from dateutil.relativedelta import relativedelta # manejo de fechas
from scipy.optimize import minimize              # para minimizar funciones

import statsmodels.formula.api as smf            # estadictica y econometria
import statsmodels.tsa.api as smt
import statsmodels.api as sm
import scipy.stats as scs

from itertools import product                    # alguna funciones utiles
from tqdm import tqdm_notebook




orders=pd.read_csv(r"C:\Users\Ipachon1\OneDrive - Rockwell Automation, Inc\Order_tracker\data\DATA FY18-19\data-fy20.csv" , thousands=',' );

#orders=pd.read_csv(r"C:\Users\Ipachon1\Desktop\Leandro_Analysis_Sep_Data.csv" , thousands=',' );

Bu = pd.read_csv(r"C:\Users\Ipachon1\OneDrive - Rockwell Automation, Inc\Order_tracker\data\Reference-DI-BU.csv");

Di = pd.read_csv(r"C:\Users\Ipachon1\OneDrive - Rockwell Automation, Inc\Order_tracker\data\Reference-DI-BPID.csv");

#Codes = pd.read_csv(r"C:\Users\Ipachon1\OneDrive - Rockwell Automation, Inc\Order_tracker\data\Reference-Order-Type.csv");

#Convert all types into needed types

orders['Shipto Name']=orders['Shipto Name'].astype('category');
orders['SOrg']=orders['SOrg.'].astype('int');
orders['City']=orders['City'].astype('category');
orders['Plnt']=orders['Plnt'].astype('category');
orders['Unit Net']=orders['Unit Net'].astype('float');
orders['Confirmed Qty']= orders['Confirmed Qty'].astype('float');
orders.round({'Unit Net':1})
orders['Confirmed Qty']= orders['Confirmed Qty'].fillna(0);
orders['Confirmed Qty']= orders['Confirmed Qty'].astype('int');
orders['Created on']= pd.to_datetime(pd.Series(orders['Created on']), format="%m/%d/%Y")
orders['SP Customer Type Desc']=orders['SP Customer Type Desc'].astype('category');
orders['Sales_Doc']= orders['Sales Doc.'].astype('str');
orders.drop('Sales Doc.', axis=1,inplace = True);
orders.drop('SOrg.', axis=1,inplace = True);


# Validate Extended Amount vs Confirmed Amount

def Validate_Amount (Pre, Ext, qty):
    if Pre == Ext: 
        return Pre
    elif Pre != Ext and qty == 0: 
        return 0
    else:
        return Ext
    
    
orders['Pre-Amount']= orders['Order quantity']*orders['Unit Net'];
orders['Amount'] = orders[['Pre-Amount','Extended Net','Order quantity']].apply(lambda x: Validate_Amount(*x), axis=1)


#validate which orders are real orders

orders['Validate']=orders['Sales_Doc'].str.startswith("6") 
orders= orders.query('Validate == 1')        


#put all orders in USD 

orders['Curr']=orders['Curr.']
orders.drop('Curr.', axis=1,inplace = True)

conditions = [
    orders['Curr'] == 'COP',
    orders['Curr'] == 'VES',
    orders['Curr'] == 'USD']
choices = [0.000311213,0.000292677 , 1]
orders['currr'] = np.select(conditions, choices, default=1)
orders['currr'] = orders['currr'].astype('float')
orders['Amount'] = orders['Amount']*orders['currr']
orders.drop('currr', axis=1,inplace = True)
#orders.drop('Curr', axis=1,inplace = True)

# replacing blank spaces with '_'  

orders.columns =[column.replace(" ", "_") for column in orders.columns] 

#Get Only Dsitributors information
#orders.query('SP_Customer_Type_Desc == "RA Authorized Distr"', inplace = True)

#Get rid off venezuela orders
orders= orders.query('SOrg != 3021')

#Drop some useless columns
orders.drop(['Description', 'Material',
       'Shipto_Country', 'Confirmed_Qty', 'Unit_Net',
       'Extended_Net', 'Plnt', 'Pre-Amount'], axis=1,inplace = True); # you could add "Validate"

#reindex 
orders = orders.reset_index(drop=True)

#rename and transform some columns cattegories 
orders.rename(columns={'Sold-to_pt' : 'BPID'}, inplace= True)
orders.BPID = orders.BPID.astype('str')
orders.BPID = (orders.BPID.apply(lambda x: x if x.isnumeric() else 0)).astype('float')

Di.BPID = Di.BPID.astype('float')
orders['Product_hierarchy'] = orders['Product_hierarchy'].str[:3]

# merge all the tables in one adding Dsitributor global names, BU names and code names
Result= pd.merge(orders,Di, left_on = 'BPID' , right_on='BPID')
Result= pd.merge(Result,Bu, left_on = 'Product_hierarchy' , right_on='BU')
#Result= pd.merge(Result,Codes, left_on = 'SaTy' , right_on='SaTy')


# fiscal year divition 

Result['FY']= Result.YR_MTH.apply(lambda x: 18 if x<201810 and x>201709 else 19 if x<201910 and x>201809 else 20)

#Real Amount + or -

#Result['Real_Amount'] = Result['Amount'] * Result['Mult']


# write to an excel file

Result.to_excel(r"C:\Users\Ipachon1\OneDrive - Rockwell Automation, Inc\Order_tracker\data\Converted Data\outputdata_Linked.xlsx" )
