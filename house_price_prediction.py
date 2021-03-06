# -*- coding: utf-8 -*-
"""House price prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KYYVdKmnHGllDnFSZeuwa8yP-id8CXVA
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
# %matplotlib inline
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
sns.set(style='whitegrid', palette='muted', font_scale=1.5)
 
rcParams['figure.figsize'] = 10, 5
 
RANDOM_SEED = 42
 
np.random.seed(RANDOM_SEED)

"""# Load the data

Data [House Prices: Advanced Regression Techniques](https://www.kaggle.com/c/house-prices-advanced-regression-techniques)
"""

!wget https://raw.githubusercontent.com/Data-Science-FMI/ml-from-scratch-2019/master/data/house_prices_train.csv

data = pd.read_csv('house_prices_train.csv')

data

data.describe()

cols = ['SalePrice', 'OverallQual', 'GrLivArea', 'GarageCars']
sns.pairplot(data[cols], size = 4);

#GrLivArea: Above grade (ground) living area square feet
var = 'GrLivArea'
df = pd.concat([data['SalePrice'], data[var]], axis=1)
df.plot.scatter(x=var, y='SalePrice', ylim=(0,800000), s=32);

"""### Data Pre-processing"""

data.isna().sum()

print(data['Alley'].isna().sum())
print(data['FireplaceQu'].isna().sum())
print(data['PoolQC'].isna().sum())
print(data['Fence'].isna().sum())
print(data['MiscFeature'].isna().sum())

data.shape

data.drop(['Id'], axis=1, inplace=True)

data.shape

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

X = pd.DataFrame(data)
data = DataFrameImputer().fit_transform(X)

data.isna().sum()

LE = LabelEncoder()
CateList = data.select_dtypes(include="object").columns
print(CateList)

data.head()

for i in CateList:
    data[i] = LE.fit_transform(data[i])
data.head()

df = data.iloc[:,:-1]
mm = MinMaxScaler()
df[:]= mm.fit_transform(df[:])

data.head()

data.shape

"""### Model Creation"""

X = df.values
y = data['SalePrice'].values

X_shape = X.shape
X_type  = type(X)
y_shape = y.shape
y_type  = type(y)

print(f'X: Type-{X_type}, Shape-{X_shape}')
print(f'y: Type-{y_type}, Shape-{y_shape}')

#Splitting our data into Training and Testing data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

print(X_train.shape, X_test.shape)
print(y_train.shape, y_test.shape)

#The predict function that returns the hypothesis 
def predict(X, weights):
    y_pred = np.dot(X, weights)
    assert (y_pred.shape==(X.shape[0],1))
    return y_pred

#Defining mean_squared_error function that returns loss\cost function value at that given training example
#loss function : when you are only considering a single traning example
#cost function : when you are considering the entire batch/mini-batch 
def mean_squared_error(y_true, y_pred): 
    loss = (1/(2*y_true.shape[0])*np.sum(y_true-y_pred)**2)
    return loss

#Defining our gradient (the gradient matrix is initialized to 0)
def gradient(X, y_true, y_pred):
    grad = np.zeros((len(X[1]),1))
    diff = y_pred-y_true
    
    for i in range(len(X[1])):
      grad[i][0] = (2/X.shape[0])*np.sum(np.dot(X[:,i],(diff)))
    return grad

#Defining our gradient descent function (initializing our weights to random numbers ??? can also be initialized to 0)
def gradient_descent(X, y, learning_rate=0.001, max_iterations=100):

    weights = np.random.rand(len(X[1]),1)
    losses  = []
  
    y_true = y.reshape(-1,1)
    for i in range(max_iterations):
        y_pred = predict(X,weights)
        losses.append(mean_squared_error(y_true,y_pred))
        grad = gradient(X,y_true,y_pred)

        for i in range(len(X[1])):
          weights[i][0] = weights[i][0] - learning_rate*grad[i][0]
    
    return weights, losses

#Let's see the optimal weights that our model has learnt on our training data
optimal_weights, losses = gradient_descent(X_train, y_train, 0.001, 200)

print("Root mean-squared error:", losses[-1]**(1/2))

#As you can see, our losses are continuously decreasing for each successive iteration, meaning our gradient descent it working fine
for i in range(len(losses)):
  print(losses[i]**(1/2))

#predictions on training data:
train_pred = predict(X_train, optimal_weights)
train_pred

y_train

from sklearn.metrics import r2_score
r2_score(y_train, train_pred)

#Testing the model on testing set
test_pred = predict(X_test, optimal_weights)
test_pred

r2_score(y_test, test_pred)

# Plotting loss curve
plt.plot([i for i in range(len(losses))], losses)
plt.title("Loss curve")
plt.xlabel("Iterations")
plt.ylabel("Loss")
plt.show()

#comparing with sklearn model
model = LinearRegression().fit(X_train, y_train)
pred = model.predict(X_train)
r2_score(y_train, pred)

pred2 = model.predict(X_test)
r2_score(y_test, pred2)