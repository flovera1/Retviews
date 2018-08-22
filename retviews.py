
# coding: utf-8

# In[4]:


'''
data exploration
'''
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt
import datetime
from sklearn.cross_validation import KFold
from sklearn.cross_validation import train_test_split
import time
from sklearn import preprocessing
from scipy.stats import skew
from sklearn.model_selection import train_test_split
from sklearn import linear_model
get_ipython().magic(u'matplotlib inline')


# In[150]:


df1       = pd.read_csv('clothes_puma.csv')
#df1.head(5)
df2 = pd.read_csv('evolutions_puma.csv', sep=';', encoding='utf8', parse_dates=["timestamp"], index_col="timestamp")
df2       = pd.read_csv('evolutions_puma.csv', sep=';', encoding='utf8')
#df2.head(5)
df2       = df2.loc[:, ~df2.columns.str.contains('^Unnamed')] # to get rid of the Unnamed column, thanks to the ";" at the end


df_merged = pd.merge(df1, df2)
#
df_merged.head(5)


# # Missing data

# In[151]:


df_merged['product_id'].replace('None', np.nan, inplace= True)
df_merged['category'].replace('None', np.nan, inplace= True)
df_merged['sub_category'].replace('None', np.nan, inplace= True)
df_merged['main_title'].replace('None', np.nan, inplace= True)
df_merged['colors'].replace('None', np.nan, inplace= True)
df_merged['color'].replace('None', np.nan, inplace= True)
df_merged['timestamp'].replace('None', np.nan, inplace= True)
df_merged['type'].replace('None', np.nan, inplace= True)
df_merged['value'].replace('None', np.nan, inplace= True)
df_merged['size_name'].replace('None', np.nan, inplace= True)


df_merged.isnull().sum()


# In[152]:


df_merged.info()


# In[102]:


#the quantity of missing values is 31.246% of your dataset,
#this means that it is not recommendable to just drop those rows.
#we will try to impute them.


# In[153]:


df_merged.head(5)


# In[104]:


#As we can see from the output, the DataFrame contains a nominal feature (color), an ordinal 
#feature (size) as well as a numerical feature (price) column. In the last column, the class labels are created.


# In[154]:


'''
To use mean values for numeric columns and the most frequent value for non-numeric columns you could do something like 
this. You could further distinguish between integers and floats. I guess it might make sense to use the median for 
integer columns instead.
'''

import pandas as pd
import numpy as np

from sklearn.base import TransformerMixin

class DataFrameImputer(TransformerMixin):

    def __init__(self):
        """Impute missing values.

        Columns of dtype object are imputed with the most frequent value 
        in column.

        Columns of other types are imputed with mean of column.

        """
    def fit(self, X, y=None):

        self.fill = pd.Series([X[c].value_counts().index[0]
            if X[c].dtype == np.dtype('O') else X[c].mean() for c in X],
            index=X.columns)

        return self

    def transform(self, X, y=None):
        return X.fillna(self.fill)
        


# In[106]:


#df_merged = pd.DataFrame(df_merged)
#df_merged = DataFrameImputer().fit_transform(df_merged)


# In[107]:


#df_merged


# In[155]:


#drop the size_name column and the other 2 rows with missing values for value
df_merged = df_merged.drop(columns=['size_name'])


# In[156]:


df_merged.isnull().sum()


# In[110]:


df_merged


# In[157]:


df_merged = DataFrameImputer().fit_transform(df_merged)


# In[158]:


df_merged


# In[159]:


# now we are without missing data
df_merged.isnull().sum()


# # Categorical data (non-numeric data)

# In[160]:


df_merged.dtypes


# In[161]:



df3       = df_merged.groupby("type")
df3.head(20)

# 
df_position       = df3.get_group('position')
df_price          = df3.get_group('price')
df_stock_decrease = df3.get_group('stock_decrease')
df_stock_size     = df3.get_group('stock_size')


# In[162]:



df_stock_decrease.head(5)


# In[163]:


# how does the stock_decrease changes its value through time

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


df_plot1 = pd.DataFrame(df_stock_decrease, columns = ['timestamp', 'value'])

# Set the Date as Index
df_plot1['date'] = pd.to_datetime(df_plot1['timestamp'])

df_plot1.index = df_plot1['date']

del df_plot1['timestamp']
del df_plot1['date']
df_plot1 = df_plot1.astype(float)

df_plot1.plot(figsize=(15, 6))
plt.show()


# In[149]:


'''
df_plot2 = pd.DataFrame(df_position, columns = ['timestamp', 'value'])

# Set the Date as Index
df_plot2['date'] = pd.to_datetime(df_plot2['timestamp'])

df_plot2.index = df_plot2['date']

del df_plot2['timestamp']
del df_plot2['date']
df_plot2 = df_plot2.astype(float)

df_plot2.plot(figsize=(15, 6))
plt.show()
'''


# In[118]:



print(df_stock_decrease.info())
# The columns with object dtype are the possible categorical features in your dataset.


# In[128]:


#fd = df_stock_decrease.select_dtypes(include=['object']).copy()
# The method .copy() is used here so that any changes made in new DataFrame don't get reflected in the original one.


# In[142]:


#print(fd.isnull().values.sum())
#print(fd.isnull().sum())


# In[177]:


df_dummified = pd.get_dummies(df_stock_decrease, columns=["category", "sub_category", "main_title", "colors", "color"], drop_first=True)


# In[178]:


df_dummified.info()
#df_dummified.head()


# In[176]:


import pandas
import numpy
from sklearn.ensemble import ExtraTreesClassifier
array = df_dummified.values
X = array[:,0:454]
Y = array[:,454]


# # Feature selection
# 
