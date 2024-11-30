import tensorflow as tf
from tensorflow import keras
from keras import layers, regularizers
from keras import backend as K
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier

from scipy.stats import randint
import keras_tuner as kt
# from sklearn.inspection import permutation_importance

def make_corr_heatmap(df):
  corr = df.corr()
  fig, ax = plt.subplots(figsize=(12,9))
  sns.heatmap(corr, annot=True)
  ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
  plt.show()

def read_file_csv(file_name):
  dfs = pd.DataFrame(pd.read_csv(file_name))
  return dfs

def plot_loss(history,name):
  plt.plot(history.history['loss'], label='loss')
  plt.plot(history.history['accuracy'], label='accuracy')
  if 'val_loss' in history.history.keys():
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
  DF = pd.DataFrame(history.history)
  DF.to_csv(f"History/{name}.csv")
  plt.xlabel('Epoch')
  plt.ylabel('Error')
  plt.legend()
  plt.grid(True)
  plt.show()

input_column_names_train = []

def parseData(train_file_path="",test_file_path="",output_column_names=[],plot=False,describe=False):
  global input_column_names_train
  train = read_file_csv(train_file_path)
  test = read_file_csv(test_file_path)

  if describe:
    print("-"*50,"Train","-"*50)
    print(train.dtypes)
    print(train.isna().sum())
    print(train.head())
    print(train.describe())
    print("-"*50,"Test","-"*50)
    print(test.dtypes)
    print(test.isna().sum())
    print(test.head())
    print(test.describe())
  
  Test_Index, Test_Catagories = test["ID"].values , np.unique(train[output_column_names])

  unimportant_columns = ["ID","Preferred Element"]

  train.drop(columns = unimportant_columns, inplace=True)
  test.drop(columns = unimportant_columns, inplace=True)

  train.dropna(inplace=True)
  train.dropna(inplace=True)

  input_column_names_train = [col for col in train.keys() if col not in output_column_names]
  input_column_names_test = input_column_names_train

  print(input_column_names_test)

  for key in input_column_names_train:
    jobs = train[key].values.tolist()
    if type(jobs[0]) != str:
      continue

    jobs = list(set(jobs))
    print("-"*10,key,"-"*10)
    print(jobs)
    for i,job in enumerate(jobs):
        train.replace(to_replace=job, value=i, inplace = True)
        test.replace(to_replace=job, value=i, inplace = True)

  out_train = train[output_column_names]
  
  # train = train.fillna(train.mean())
  # test = test.fillna(test.mean())

  # plotting
  if plot: # very slow so good luck approx 5 min per image... its better to directly save and not show
    sns.pairplot(train, diag_kind='kde')
    plt.show()
    sns.pairplot(test, diag_kind='kde')
    plt.show()
    make_corr_heatmap(train)
    make_corr_heatmap(test)
  if describe:
    print("-"*50,"Train","-"*50)
    print(train.dtypes)
    print(train.head())
    print(train.describe())
    print("-"*50,"Test","-"*50)
    print(test.dtypes)
    print(test.head())
    print(test.describe())

  scaler_X = MinMaxScaler()

  clean_dataset_length = len(train)

  train_split, val_split = train[:int(clean_dataset_length*0.8)] , train[int(clean_dataset_length*0.8):]
  out_train_split , out_val_split = out_train[:int(clean_dataset_length*0.8)], out_train[int(clean_dataset_length*0.8):]

  input_train_split = train_split[input_column_names_train].values
  output_train_split = pd.get_dummies(out_train_split,dtype=int).values
  input_val_split = val_split[input_column_names_train].values
  output_val_split = pd.get_dummies(out_val_split,dtype=int).values

  INP = test[input_column_names_test].values

  Unscaled_train_val_test_split = (input_train_split,output_train_split,input_val_split,output_val_split,INP)

  X_train_scaled = scaler_X.fit_transform(input_train_split)
  X_val_scaled = scaler_X.transform(input_val_split)
  X_inp_scaled = scaler_X.transform(INP)

  Scaled_train_val_test_split = (X_train_scaled,X_val_scaled,X_inp_scaled)

  Scalars = (scaler_X)
  return Unscaled_train_val_test_split, Scaled_train_val_test_split, Scalars, Test_Index, Test_Catagories


test_data_path = "Dataset/Kaggle_test.csv"
train_data_path = "Dataset/train.csv"
output_column_names = ["House"]

Unscaled_train_val_test_split, Scaled_train_val_test_split, Scalars, Test_Index, Test_Catagories = parseData(
                                                                                    train_file_path = train_data_path,
                                                                                    test_file_path = test_data_path,
                                                                                    output_column_names = output_column_names,
                                                                                    describe = False,
                                                                                    plot=False
                                                                                )

X_train,Y_train,X_val,Y_val,X_test = Unscaled_train_val_test_split
X_train_scaled,X_val_scaled,X_test_scaled = Scaled_train_val_test_split
# print(X_train.shape, Y_train.shape, X_val.shape , Y_val.shape , X_test.shape )


def classifier():
  Y_reg_train  = tf.argmax(Y_train, axis=1).numpy()
  Y_reg_val = tf.argmax(Y_val, axis=1).numpy()

  param_dist = {'n_estimators': randint(50,1000),
                'max_depth': randint(1,50)}

  regr = RandomForestClassifier()

  rand_search = RandomizedSearchCV(regr, 
                                  param_distributions = param_dist, 
                                  n_iter=15, 
                                  cv=4)
  
  rand_search.fit(X_train, Y_reg_train)

  best_rf = rand_search.best_estimator_
  print(rand_search.best_params_)

  y_pred = best_rf.predict(X_val)
  accuracy = accuracy_score(Y_reg_val, y_pred)
  print("Accuracy:", accuracy)
  
  cm = confusion_matrix(Y_reg_val, y_pred)
  ConfusionMatrixDisplay(confusion_matrix=cm).plot()
  
  plt.show()
  # {'max_depth': 40, 'n_estimators': 306}
  # Accuracy: 0.2691292875989446
  return best_rf

def SVM_model():
  Y_reg_train  = tf.argmax(Y_train, axis=1).numpy()
  Y_reg_val = tf.argmax(Y_val, axis=1).numpy()

  svm_classifier = SVC(kernel='linear', C=0.5)
  svm_classifier.fit(X_train, Y_reg_train)

  y_pred = svm_classifier.predict(X_val)
  accuracy = accuracy_score(Y_reg_val, y_pred)
  print("Accuracy:", accuracy)  

  # Make predictions
  y_pred = svm_classifier.predict(X_test)
  return y_pred

def gradient_boosting():
  Y_reg_train  = tf.argmax(Y_train, axis=1).numpy()
  Y_reg_val = tf.argmax(Y_val, axis=1).numpy()

  gb_classifier = GradientBoostingClassifier(n_estimators=500)
  gb_classifier.fit(X_train, Y_reg_train)

  y_pred = gb_classifier.predict(X_val)
  accuracy = accuracy_score(Y_reg_val, y_pred)
  print("Accuracy:", accuracy)  

  # Make predictions
  y_pred = gb_classifier.predict(X_test)
  return y_pred

def make_model(inp,out):
  model = keras.Sequential()
  model.add(layers.InputLayer(inp,))
  model.add(layers.Dense(64, activation="relu"))
  model.add(layers.Dense(32, activation="relu"))
  model.add(layers.Dense(16, activation="relu"))
  model.add(layers.Dense(out, activation="softmax"))
  model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=['accuracy'])
  return model

def make_model_scce(inp,out):
  model = keras.Sequential()
  model.add(layers.InputLayer(inp,))
  model.add(layers.BatchNormalization())
  model.add(layers.Dense(16, activation="relu"))
  model.add(layers.BatchNormalization())
  model.add(layers.Dense(12, activation="relu"))
  model.add(layers.Dense(16, activation="relu"))
  model.add(layers.BatchNormalization())
  model.add(layers.Dense(out, activation="softmax"))
  model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=['accuracy'])
  return model

def run_DL():
  accuracy_limit = 0
  while accuracy_limit < 0.25:
    model = make_model(len(X_train_scaled[0]),len(Y_train[0]))
    # model = make_model_scce(len(X_train_scaled[0]),len(Y_train[0]))
    Y_train_int = tf.argmax(Y_train, axis=1)
    Y_val_int = tf.argmax(Y_val, axis=1)

    history = model.fit(X_train_scaled,Y_train, validation_data=(X_val_scaled,Y_val), epochs=10, batch_size=32, use_multiprocessing=True, verbose=0)
    accuracy_limit = history.history["val_accuracy"][-1]
    print(accuracy_limit)

  model.save("Models/test1")
  plot_loss(history,"history1")
  # model = keras.models.load_model("Models/test3")
  Preds = model.predict(X_test_scaled)
  return Preds, model

def keras_tuner_search_optimizer():
  def build_model(hp):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.InputLayer(input_shape=(12,)))

    hp_input_BN = hp.Choice("input_BN", values=[0,1])
    hp_acti = hp.Choice("activation",values=['relu','tanh','sigmoid'])
    hp_opti = hp.Choice("optimizer",values=['adam','adagrad','adadelta'])
    hp_layer1 = hp.Int('layer1',min_value=0,max_value=32,step=4)
    hp_BN1 = hp.Choice('BN1',values=[0,1])
    hp_layer2 = hp.Int('layer2',min_value=0,max_value=32,step=4)
    hp_BN2 = hp.Choice('BN2',values=[0,1])
    hp_layer3 = hp.Int('layer3',min_value=0,max_value=32,step=4)
    hp_BN3 = hp.Choice('BN3',values=[0,1])
    hp_lr = hp.Choice('learning_rate',values=[1e-3,1e-4])

    if hp_input_BN:
      model.add(layers.BatchNormalization())
    if hp_layer1 != 0:
      model.add(layers.Dense(units=hp_layer1,activation=hp_acti))
      if hp_BN1:
        model.add(layers.BatchNormalization())
    if hp_layer2 != 0:
      model.add(layers.Dense(units=hp_layer2,activation=hp_acti))
      if hp_BN2:
        model.add(layers.BatchNormalization())
    if hp_layer3 != 0:
      model.add(layers.Dense(units=hp_layer3,activation=hp_acti))
      if hp_BN3:
        model.add(layers.BatchNormalization())

    model.add(layers.Dense(units=4,activation='softmax'))

    if hp_opti == 'adam':
      optimizer = tf.keras.optimizers.Adam(learning_rate=hp_lr)
    elif hp_opti == 'adagrad':
      optimizer = tf.keras.optimizers.Adagrad(learning_rate=hp_lr)
    else :
      optimizer = tf.keras.optimizers.Adadelta(learning_rate=hp_lr)

    model.compile(optimizer = optimizer, loss = 'categorical_crossentropy', metrics=["accuracy"])
    model.summary()
    return model

  DIRECTORY = 'Test'
  PROJECT_NAME = 'd0'
  tune_model = kt.BayesianOptimization(build_model,
                                      objective='val_accuracy',
                                      max_trials = 200,
                                      directory=DIRECTORY,
                                      project_name=PROJECT_NAME)
  
  stop_early = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=5)
  
  tune_model.search(X_train_scaled, Y_train,
                    validation_data=(X_val_scaled,Y_val),
                    epochs=25, batch_size=32,
                    use_multiprocessing=True,
                    callbacks=[stop_early],
                    )

  best_hp = tune_model.get_best_hyperparameters(num_trials=1)[0]
  model_best = tune_model.get_best_models(num_models=1)[0]
  out = model_best.evaluate(X_val_scaled,Y_val) 

  print("best model",out)

  model = tune_model.hypermodel.build(best_hp)
  history = model.fit(X_train_scaled, Y_train,
                      validation_data=(X_val_scaled,Y_val),
                      epochs=25, batch_size=32,
                      callbacks=[stop_early]
                      )
  model.summary()
  plot_loss(history,"KT")
  return model, model_best


y_pred, model= run_DL()
# model, model_best = keras_tuner_search_optimizer()
# y_pred = model_best.predict(X_test_scaled)
# model.save()
print(y_pred)
y_pred = tf.argmax(y_pred, axis=1).numpy()
print(y_pred,y_pred.shape)

# best_rf = classifier()
# y_pred = best_rf.predict(X_test)
# print(y_pred)

# y_pred = gradient_boosting()

output_df = pd.DataFrame({"ID":Test_Index,"House":Test_Catagories[y_pred]})
print(output_df)

sns.countplot(x="House",data=output_df)
plt.show()
output_df.to_csv("submission.csv",index=False)