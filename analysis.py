import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import SelectKBest,chi2
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

from sklearn.linear_model import LinearRegression, SGDClassifier, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.model_selection import GridSearchCV

import warnings
from sklearn.exceptions import ConvergenceWarning

def warn(*args, **kwargs): pass
warnings.warn = warn

class DataCleaning():
  def __init__(self,df):
    self.df = df
    self.cols = df.columns
    self.getLabelMaps()

  def getCols(self,condition):
    return self.df.columns[np.where(condition(self.df))]

  def getLabelMaps(self):
    label_maps = {}
    columns_to_change = self.getCols(lambda x: x.dtypes == 'object')
    for cols in columns_to_change:
      unique_elems = self.df[cols].unique()
      label_maps[cols] = dict(zip(unique_elems,range(0,len(unique_elems))))
      label_maps[cols+"_inv"] = dict(zip(range(0,len(unique_elems)),unique_elems))
    self.label_maps = label_maps
    return label_maps

  def updateDatasetLabelMap(self):
    for cols in self.label_maps:
      if "_inv" in cols: continue
      for unique in self.label_maps[cols]:
        self.df[cols].replace(unique,self.label_maps[cols][unique],inplace=True)

  def updateDatasetLabelMapInv(self):
    for cols in self.label_maps:
      if "_inv" in cols: continue
      for unique in self.label_maps[cols+"_inv"]:
        self.df[cols].replace(unique,self.label_maps[cols+"_inv"][unique],inplace=True)

  def getCorrelationMatrix(self,columns=None):
    return self.df[columns].corr() if type(columns) != "NoneType" else self.df.corr()

class DataProcessing():
  def __init__(self):
    self.tsne = TSNE
    self.pca = PCA
    self.scaler = MinMaxScaler
    self.dim = 2

  def applyTSNE(self,data):
    tsne = self.tsne(n_components=self.dim)
    return tsne,tsne.fit_transform(data)

  def applyPCA(self,data):
    pca = self.pca(n_components=self.dim)
    return pca,pca.fit_transform(data)

  def normalize(self,data):
    scale = self.scaler()
    return scale,scale.fit_transform(data)

  def apply_processing(self,datatype,norm,d):
    self.dim = d
    norm = 0 if norm == "unscaled" else 1
    if datatype=='raw':
        return self.normalize if norm else (lambda x: (-1,x))
    elif datatype=='pca':
      return (lambda x: self.applyPCA(self.normalize(x)[1]) )if norm else self.applyPCA
    elif datatype=='tsne':
      return (lambda x: self.applyTSNE(self.normalize(x)[1])) if norm else self.applyTSNE
    else:
      raise "DataType incompatiable"

class ModelTesting():
  def __init__(self):
    self.models = [
        "Linear Regression",
        "Logistic Regression",
        "SGD Classifier",
        "Decision Tree",
        "Random Forest",
        "MLP",
        "Gaussian Naive Bayes"
    ]
    self.metrics = [
        'accuracy',
        'precision',
        'recall',
        'f1-score'
    ]

    self.models_to_compare = [
      LinearRegression,
      LogisticRegression,
      SGDClassifier,
      DecisionTreeClassifier,
      RandomForestClassifier,
      MLPClassifier,
      GaussianNB
    ]
  def setData(self, data, Y, dataTypes, normalizations):
    self.data = data
    self.target = Y
    self.rows = dataTypes
    self.cols = normalizations

  def train_model(self,model,x_train,x_test,y_train,y_test):
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    y_pred = np.where(y_pred > 0.5, 1, 0)

    out = {
        'accuracy':accuracy_score(y_test,y_pred),
        'precision':precision_score(y_test,y_pred),
        'recall':recall_score(y_test,y_pred),
        'f1-score':f1_score(y_test,y_pred),
        'model': model
    }
    return out

  def train_all_models(self,NUM_TRAIN=1):
    results = {}
    results_table = np.zeros((len(self.models)*len(self.rows)*len(self.cols),4+len(self.metrics)),dtype='object')
    column_names = ["Model Name",'model',"data type","normalization"] + self.metrics

    i = 0
    for datatype_index, datatype in enumerate(self.rows): # for all data types
      results[datatype] = {}
      for norm_index, norm in enumerate(self.cols): # for all normalizations
        results[datatype][norm] = {}
        for mod_index, mod in enumerate(self.models_to_compare): # for all models to compare
          res = {}
          for num_train in range(0,NUM_TRAIN): # run every model NUM_TRAIN times and take the average of each metric
            model = mod() # creates a new instantce of model
            out_res = self.train_model( model, *train_test_split(self.data[datatype_index][norm_index], self.target, test_size=0.33))
            # average the results by added the scaled output to res
            for key in out_res:
              if key!="model":
                out_res[key] = out_res[key]/NUM_TRAIN
            res = out_res if num_train == 0 else {i:res[i]+out_res[i] for i in res.keys() if i != "model"}
            res['model'] = out_res['model']

          results[datatype][norm][self.models[mod_index]] = res # add to hash map
          # add to table
          results_table[i,0] = self.models[mod_index]
          results_table[i,1] = res['model']
          results_table[i,2] = datatype
          results_table[i,3] = norm
          k = 0
          for metric in self.metrics:
            results_table[i,4+k] = results[datatype][norm][self.models[mod_index]][metric]
            k+=1
          i+=1

    self.results = results # store result in hash map
    self.results_table = pd.DataFrame(results_table,columns = column_names) # store result in table for visulization

class Ensamble_model():
  def __init__(self,models_arr,preprocessing_arr):
    self.models_ensemble = models_arr
    self.preprocessing_ensemble = preprocessing_arr
    self.setup = [False]*len(models_arr)

  def predict(self, x_test):
    results = []
    for i in range(len(self.models_ensemble)):
      if self.setup[i]:
        x = self.preprocessing_ensemble[i].transform(x_test)
      else:
        trained_processing_scalar,x = self.preprocessing_ensemble[i](x_test)
        self.preprocessing_ensemble[i] = trained_processing_scalar if trained_processing_scalar != -1 else self.preprocessing_ensemble[i]
        self.setup[i] = trained_processing_scalar != -1
      model = self.models_ensemble[i]
      results.append(model.predict(x))
    results = (np.mean(results,axis=0) > 0.5).astype(int)
    return results

  def evaluate(self, x_test, y_test):
    y_pred = self.predict(x_test)
    out = {
        'accuracy':accuracy_score(y_test,y_pred),
        'precision':precision_score(y_test,y_pred),
        'recall':recall_score(y_test,y_pred),
        'f1-score':f1_score(y_test,y_pred),
    }
    return out

  def fit(self, x_train, y_train):
    for i in range(len(self.models_ensemble)):
      if self.setup[i]:
        x = self.preprocessing_ensemble[i].transform(x_train)
      else:
        trained_processing_scalar,x = self.preprocessing_ensemble[i](x_train)
        self.preprocessing_ensemble[i] = trained_processing_scalar if trained_processing_scalar != -1 else self.preprocessing_ensemble[i]
        self.setup[i] = trained_processing_scalar != -1
      model = self.models_ensemble[i]
      model.fit(x,y_train)
      print(model.score(x_train,y_train))

def chi_based_columns(DC,targetColumn,k=5):
  selector = SelectKBest(chi2, k=k)
  selector.fit(DC.df.drop(targetColumn, axis=1), DC.df[targetColumn])
  significant_features = DC.df.drop(targetColumn, axis=1).columns[selector.get_support()]
  return significant_features

def correlation_matrix_based_columns(DC,targetColumn,THRESHOLD=0.1):
  corr_cols = DC.getCols(lambda x: x.std()!=0)
  cm = DC.getCorrelationMatrix(corr_cols.values)
  plt.figure(figsize=(8,8))
  sns.heatmap(cm)
  plt.show()
  significant_features = corr_cols[THRESHOLD < np.abs(cm[targetColumn])].drop(targetColumn)
  return significant_features

def plotScatterNewFigure(x,y,title,c):
  plt.figure()
  plt.scatter(x,y,c=c)
  plt.title(title)

def hyperparameter_tuning(top_models:pd.DataFrame, N: int):
  models = [ # define all models
    LinearRegression, LogisticRegression, SGDClassifier,
    DecisionTreeClassifier, RandomForestClassifier,
    MLPClassifier, GaussianNB
  ]
  parameters = [ # define parametr space fo reach of the models
      {},
      {'C':[0.001,0.01,0.1,1,10,100], "solver":['lbfgs', "liblinear", 'newton-cg', 'newton-cholesky', 'sag', 'saga']},
      {'loss':['hinge', 'log_loss', 'modified_huber', 'squared_hinge', 'perceptron', 'squared_error', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive']},
      {'criterion':['gini','entropy'],'max_depth':[4,5,6,7,8,9,10,11,12,15,20,30,40,50,70,90,120,150]},
      {'bootstrap': [True, False],'max_depth': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, None],'max_features': ['auto', 'sqrt'],'min_samples_leaf':[1, 2, 4],
      'min_samples_split': [2, 5, 10],'n_estimators': [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000]},
      {'hidden_layer_sizes': [(10),(20),(10,10),(10,20),(20,10),(20,20)],'activation': ['tanh', 'relu'],'solver': ['sgd', 'adam'],'alpha': [0.0001, 0.05],'learning_rate': ['constant','adaptive']},
      {'var_smoothing': np.logspace(0,-9, num=100)}
  ]
  # create a neo model to store the results in
  updated_table = top_models.iloc[:N].copy(deep=True)

  for model_choosen in range(0,N): # take the top N models
    # get basic values
    model_index = MT.models.index(top_models['Model Name'][model_choosen])
    model = models[model_index]()
    model_params = parameters[model_index]
    model_data_row = MT.rows.index(top_models['data type'][model_choosen])
    model_data_col = MT.cols.index(top_models['normalization'][model_choosen])

    print(model_data_row,model_data_col)

    # perform grid search on the models based on the cached data
    x_train, x_test, y_train, y_test = train_test_split(MT.data[model_data_row][model_data_col], MT.target, test_size=0.33)
    grid_search = GridSearchCV(estimator=model, param_grid=model_params, n_jobs=-1,cv=10,scoring='accuracy')
    with warnings.catch_warnings():
      warnings.simplefilter('ignore', category=ConvergenceWarning)
      grid_search.fit(x_train, y_train)
    print("Best Hyperparameters: ", grid_search.best_params_)

    # Evaluate the model on the test set
    best_model = models[model_index]()
    best_model.set_params(**grid_search.best_params_)
    new_result = MT.train_model(best_model, x_train, x_test, y_train, y_test)

    #update table only if the new model is better
    if new_result['accuracy'] > updated_table.iloc[model_choosen]['accuracy']:
      print("Found better model")
      for key in new_result.keys():
        updated_table.iloc[model_choosen][key] = new_result[key]
    print()
  return updated_table



IBM_HR_analytics_dataset = pd.read_csv("WA_Fn-UseC_-HR-Employee-Attrition.csv")
print(IBM_HR_analytics_dataset.head())
print(IBM_HR_analytics_dataset.isna().sum())
print(IBM_HR_analytics_dataset.dtypes)

DC = DataCleaning(IBM_HR_analytics_dataset)
DC.getLabelMaps()
DC.updateDatasetLabelMap()

print(DC.df.head())
print(DC.df.describe())
print(DC.df.std())


targetColumn = 'Attrition'
significant_features = correlation_matrix_based_columns(DC,targetColumn,0.15)
Y = DC.df[targetColumn].copy()
X = DC.df[significant_features.values].copy()
print(Y.shape, X.shape)

plt.figure()
avg_vals = []
for job_inv in DC.df['JobInvolvement'].unique():
  temp = DC.df.loc[DC.df["JobInvolvement"] == job_inv]
  avg_vals = np.mean( temp['PercentSalaryHike'] )
plt.bar(DC.df['JobInvolvement'].unique(),avg_vals)
plt.title("Job Involvement vs Average Percent Salary Hike")
plt.show()

plt.figure()
plt.scatter(DC.df['YearsWithCurrManager'],DC.df['PercentSalaryHike'])
plt.title("YearsWithCurrManager vs PercentSalaryHike")
plt.show()

DC.df.groupby(['Attrition']).mean().plot(kind='pie', y='OverTime', autopct='%1.0f%%')
plt.title("Mean OverTime vs Attrition")
plt.show()

sns.countplot(x='Attrition', data=DC.df)
plt.show()

sns.countplot(x='Attrition', hue='Department', data=DC.df)
plt.show()

sns.countplot(x='Attrition', hue='JobRole', data=DC.df)
plt.show()

sns.boxplot(x='Attrition', y='Age', hue='Gender', data=DC.df)
plt.show()


DC.updateDatasetLabelMapInv()
print(DC.df.head(10))


DP = DataProcessing()
_,X_raw = DP.apply_processing('raw','unscaled',2)(X.values)
pca,pca_components = DP.apply_processing('pca','unscaled',2)(X.values)
tsne, tsne_components = DP.apply_processing('tsne','unscaled',2)(X.values)

_, X_norm = DP.apply_processing('raw','scaled',2)(X.values)
pca_norm, pca_norm_components = DP.apply_processing('pca','scaled',2)(X.values)
tsne_norm, tsne_norm_components = DP.apply_processing('tsne','scaled',2)(X.values)

data = [ # rows are raw, pca, tsne and columns are unscaled and scaled data
    [X_raw              , X_norm],
    [pca_components  , pca_norm_components],
    [tsne_components , tsne_norm_components]
]

plotScatterNewFigure(pca_components[:,0],pca_components[:,1],"PCA",Y)
plotScatterNewFigure(tsne_components[:,0],tsne_components[:,1],"t-SNE",Y)
plotScatterNewFigure(pca_norm_components[:,0],pca_norm_components[:,1],"PCA normalize data",Y)
plotScatterNewFigure(tsne_norm_components[:,0],tsne_norm_components[:,1],"t-SNE normalize data",Y)
plt.show()


MT = ModelTesting()
MT.setData(data, Y, ['raw','pca',"tsne"], ['unscaled','scaled'])
MT.train_all_models(10)
MT.results_table.sort_values(by=['accuracy'],ascending=False,ignore_index=True, inplace=True)\

print("Top 3 models")
print(MT.results_table.head(3))

updated_table = hyperparameter_tuning(MT,MT.results_table,2) # each MLP models will take 5-6 mins

print(updated_table)

processing_func = [DP.apply_processing(updated_table['data type'][i], updated_table['normalization'][i], 2) for i in range(len(updated_table))]

EM = Ensamble_model(updated_table['model'].values, processing_func)

EM.evaluate(X_raw,Y.values)

# Ensamble model can also be trained like this if necessary
# EM.fit(X_raw,Y.values)
# EM.evaluate(X_raw,Y.values)

"""# Prediction model performance visualization
* Feature extraction methods
 - Chi^2 test
 - Correlation based
* Data processing methods
 - unscaled data
 - scaled data
 - unscaled pca
 - scaled pca
 - unscled tsne
 - scled tsne
* Predicting models
 - Linear Regression
 - Logistic Regression
 - SGD Classifier
 - Decision Tree
 - Random Forest
 - MLP
 - Gaussian Naive Bayes
 - Ensamble Models
* Hyperparameter tuning
"""

DC.updateDatasetLabelMap()
cols1 = chi_based_columns(DC,targetColumn,k=5)
cols2 = correlation_matrix_based_columns(DC,targetColumn,THRESHOLD=0.15)
DC.updateDatasetLabelMapInv()

print("Columns based on Chi square:", *cols1)
print("Columns based on Correlation:", *cols2)

print("Best Models based on all combination of models and data processing")
MT.results_table.head(20)

for model in MT.models: # for all the models
  model_table = MT.results_table.loc[MT.results_table['Model Name'] == model].drop('Model Name',axis=1)
  fig, axs = plt.subplots(2,2,figsize=(8,8))
  fig.suptitle(model + " results between data types", fontsize=16)
  for ind,metric in enumerate(MT.metrics):  # for all the metrics
    for i,norm in enumerate(model_table['normalization'].unique()):  # for all normalizations
      val_norm = []
      for datatype in model_table['data type'].unique():  # for all data types
        cond1 = model_table['normalization'] == norm
        temp = model_table.loc[cond1]
        cond2 = model_table['data type'] == datatype
        temp = temp.loc[cond2]
        val_norm.append(temp[metric].values[0])
      x_axis = np.arange(len(model_table['data type'].unique()))
      axs[int(ind/2),ind%2].bar(x_axis +(0.2)*(-1)**i , val_norm, 0.4, label = norm)  # plot the comparitive bar chart
    axs[int(ind/2),ind%2].set_ylim([min(val_norm)-0.05,max(val_norm)+0.05 if max(val_norm) + 0.05 < 1 else 1])
    axs[int(ind/2),ind%2].set_xticks(x_axis, model_table['data type'].unique())
    axs[int(ind/2),ind%2].title.set_text(metric)
    axs[int(ind/2),ind%2].legend()
  plt.show()

mean_acc = MT.results_table.groupby('Model Name')['accuracy'].mean()
mean_acc['Ensamble'] = EM.evaluate(X_raw,Y.values)['accuracy']
mean_acc.plot(kind='bar', ylabel='Avg Accuracy', title='Average accuracy vs models', ylim = [mean_acc.min()-0.1,1] )
plt.show()