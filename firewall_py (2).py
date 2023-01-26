# -*- coding: utf-8 -*-
"""Firewall.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IEMysT0WNBH5JgSrV8DXHJa7q6QPXJyO

FIREWALL SECURITY
"""

#load dataset
from google.colab import files
uploaded = files.upload()

import pandas as pd
import io

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
nRowsRead = None

 
df = pd.read_csv(io.BytesIO(uploaded['firewall.csv']))

"""DATA UNDERSTANDING"""

df.shape

df.head(5)

df.info(verbose=False)

df.describe(include='all').round(2).T

#importing libaries for visualisation
import numpy as np
import matplotlib.pyplot as plt
import missingno as msno
import seaborn as sns
import time
import warnings
warnings.filterwarnings('ignore')

"""PREPROCESSING"""

#checking for missing value
total = df.isnull().sum().sort_values(ascending=False)
percent=(df.isnull().sum()/df.isnull().count()*100).sort_values(ascending=False)
missing_data=pd.concat([total,percent],axis=1,keys=['Total','Percent'])
missing_data.head(79)

df.columns=df.columns.str.replace(' ','_')
df.rename(columns = {'Elapsed_Time_(sec)':'Elapsed_Time_sec'}, inplace = True)

#investigation of categorical variables 
df.describe(exclude="number")

sns.histplot(data=df,x=df['Action']);

df.Action.value_counts()

#creating a binary class from a multiclass
df["Class"]="0"
label_cat={"Reject":["deny","drop","reset-both"],
            "Accept":["allow"]
         }

for label in label_cat:
  filter=df["Action"].str.contains('|'.join(label_cat[label]),case=False,regex=True,na=False)
  df.loc[filter, "Class"] = label

df.Class.value_counts()

df=df.drop(['Action'], axis=1)

#df.head()

"""DATA ANALYSIS"""

#global view of numeric variables of the dataset
df.plot(lw=0,marker=".",subplots=True,layout=(3,4),figsize=(20,6),markersize=1)
plt.tight_layout();

#plot histogram to detect outliers
df.hist(bins=20, figsize=(20, 6), layout=(3,4), edgecolor="black")
plt.tight_layout();

sns.pairplot(df, hue='Class');

df.cov()

df.corr().round(5)

sns.heatmap(df.corr(), annot=False, linewidth = 0.30, cmap ='coolwarm')
plt.show()

#visualising the class feature
plt.figure(figsize=(10,5))
df.groupby("Class").size().plot.pie(autopct='%0.1f%%',
explode=(0.1,0.05),title="Class Frequency")
plt.show()

plt.figure(figsize=(8,4))
sns.countplot(data=df,x='Class')
locs, labels = plt.xticks()
plt.setp(labels, rotation = 90)
plt.title('Total Traffic')
plt.ylabel('Traffic');

bp = sns.boxplot(x=df['Class'], y=df['Source_Port'])
bp.set_title('Source Port Distribution');

sns.boxplot(x=df['Class'], y=df['Destination_Port'])
bp.set_title('Destination Port Distribution');

bp = sns.boxplot(x=df['Class'], y=df['NAT_Source_Port'])
bp.set_title('NAT Source Port Distribution');

bp = sns.boxplot(x=df['Class'], y=df['NAT_Destination_Port'])
bp.set_title('NAT Destination Port Distribution');

plt.figure(figsize=(8,3))
sns.barplot(data=df, x='Class', y = 'Source_Port')
plt.xticks(rotation=90)
plt.title('Access for Source Port')
plt.xlabel('Access')
plt.ylabel('Source Port');

plt.figure(figsize=(8,3))
sns.barplot(data=df, x='Class', y = 'Destination_Port')
plt.xticks(rotation=90)
plt.title('Access for Destination Port')
plt.xlabel('Access')
plt.ylabel('Destination Port');

#Investigating the ports, by categorising them, to get the top 10 ports
ports_cat = ['Source_Port', 'Destination_Port', 'NAT_Source_Port', 'NAT_Destination_Port']

for f in ports_cat:
    print('port:', f)
    print(df[f].value_counts()[0:10])
    print()
    df[f].value_counts()[0:10].plot(kind='bar')
    plt.title(f)
    plt.show()

#distribution of the top 10 destination port traffic
var = "Destination_Port"
data = pd.concat([df["Source_Port"],df[var]], axis=1)
plt.figure(figsize=(7,7))
sns.scatterplot(x="Source_Port",y="Destination_Port", data=df, hue = "Class")
locs, labels=plt.xticks()
plt.setp(labels,rotation=90)
plt.legend(bbox_to_anchor=(1.01,1));

#distribution of the top 10 source port traffic
var = "NAT_Destination_Port"
data = pd.concat([df["NAT_Source_Port"],df[var]], axis=1)
plt.figure(figsize=(7,7))
sns.scatterplot(x="NAT_Source_Port",y="NAT_Destination_Port", data=df, hue = "Class")
locs, labels=plt.xticks()
plt.setp(labels,rotation=90)
plt.legend(bbox_to_anchor=(1.01,1));

#transforming class variable to numeric for modelling
df["class"]=df["Class"].astype("category").cat.codes

#df.head()

df=df.drop(['Class'], axis = 1)

#seperating the dataset into X and y data
X = df.values
y = df['class'].values

#delete the survived column from X
X = np.delete(X,-1,axis=-1)

X

y

#split the dataset into 80% training and 20% test
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2, random_state=0)

print(X_train)

print(X_test)

#Random forest classification
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
rfc = RandomForestClassifier(n_estimators = 100, criterion='entropy', random_state = 0)
rfc.fit(X_train, y_train)
rfc.score(X_test,y_test)

y_pred_rfc=rfc.predict(X_test)
print(y_pred_rfc)

rfc.estimators_

plt.figure(figsize=(20,10))
tree.plot_tree(rfc.estimators_[99],filled=True)

#confusion matrix and accuracy score
from sklearn.metrics import confusion_matrix, accuracy_score
cm = confusion_matrix(y_test, y_pred_rfc)
print(cm)
accuracy_score(y_test, y_pred_rfc)

#confusion matrix
from sklearn.metrics import plot_confusion_matrix

plot_confusion_matrix(rfc,X_test,y_test)
plt.show();

from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred_rfc))

#Naive Bayes algorithm
from sklearn.naive_bayes import GaussianNB
nb=GaussianNB()
nb.fit(X_train, y_train)
nb.score(X_test,y_test)

y_pred_nb=nb.predict(X_test)
print(y_pred_nb)

cm = confusion_matrix(y_test, y_pred_nb)
print(cm)
accuracy_score(y_test, y_pred_nb)

plot_confusion_matrix(nb,X_test,y_test)
plt.show();

#prediction probabilities
r_probs = [0 for _ in range(len(y_test))]
rfc_probs = rfc.predict_proba(X_test)
nb_probs = nb.predict_proba(X_test)

#probabilities for the positive outcome is kept
rfc_probs = rfc_probs[:,1]
nb_probs = nb_probs[:,1]

#compute the AUROC values
from sklearn.metrics import roc_curve, roc_auc_score
r_auc = roc_auc_score(y_test, r_probs)
rfc_auc = roc_auc_score(y_test, rfc_probs)
nb_auc = roc_auc_score(y_test, nb_probs)

#display the AUROC scores
print("Random Prediction: AUROC = %.4f" %(r_auc))
print("Random Forest: AUROC = %.4f" %(rfc_auc))
print("Naive Bayes: AUROC = %.4f" %(nb_auc))

#calculate the ROC curve
r_fpr, r_tpr, _ = roc_curve(y_test, r_probs)
rfc_fpr, rfc_tpr, _ = roc_curve(y_test, rfc_probs)
nb_fpr, nb_tpr, _ = roc_curve(y_test, nb_probs)

#plot the ROC Curve
plt.figure(figsize=(10,4))
plt.plot(r_fpr, r_tpr, linestyle='--', label='Random Prediction (AUROC =%0.4f)' %r_auc)
plt.plot(rfc_fpr, rfc_tpr, linestyle='--', label='Random Forest (AUROC =%0.4f)' %rfc_auc)
plt.plot(nb_fpr, nb_tpr, linestyle='--', label='Naive Bayes (AUROC =%0.4f)' %nb_auc)
plt.title('ROC Curve')
plt.xlabel('false positive rate')
plt.ylabel('true positive rate')
plt.legend(loc='lower right')
plt.show();

print(classification_report(y_test, y_pred_nb))