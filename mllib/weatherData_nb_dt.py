#requires numpy to be installed to work
#sudo easy_install numpy==1.4.1
#The below code has to be entered in ipython interactively
rawdata=[
['sunny',85,85,'FALSE',0],
['sunny',80,90,'TRUE',0],
['overcast',83,86,'FALSE',1],
['rainy',70,96,'FALSE',1],
['rainy',68,80,'FALSE',1],
['rainy',65,70,'TRUE',0],
['overcast',64,65,'TRUE',1],
['sunny',72,95,'FALSE',0],
['sunny',69,70,'FALSE',1],
['rainy',75,80,'FALSE',1],
['sunny',75,70,'TRUE',1],
['overcast',72,90,'TRUE',1],
['overcast',81,75,'FALSE',1],
['rainy',71,91,'TRUE',0]
]

from pyspark.sql import SQLContext,Row
sqlContext = SQLContext(sc)

data_df=sqlContext.createDataFrame(rawdata,
   ['outlook','temp','humid','windy','play'])

#transform categoricals into indicator variables
out2index={'sunny':[1,0,0],'overcast':[0,1,0],'rainy':[0,0,1]}

from pyspark.mllib.regression import LabeledPoint

#make RDD of labeled vectors
def newrow(dfrow):
    outrow = list(out2index.get((dfrow[0])))  #get dictionary entry for outlook
    outrow.append(dfrow[1])   #temp
    outrow.append(dfrow[2])   #humidity
    if dfrow[3]=='TRUE':      #windy
        outrow.append(1)
    else:
        outrow.append(0)
    return (LabeledPoint(dfrow[4],outrow))

datax_rdd=data_df.map(newrow)

from pyspark.mllib.classification import NaiveBayes

my_nbmodel = NaiveBayes.train(datax_rdd)

#Some info on model 
print my_nbmodel

#some checks,get some of training data and test it:
datax_col=datax_rdd.collect()   #if datax_rdd was big, use sample or take

#predictions for features in datax_col
trainset_pred =[]
for x in datax_col:
    trainset_pred.append(my_nbmodel.predict(x.features))

print trainset_pred

#to see class conditionals
#you might have to install scipy
#import scipy
#print 'Class Cond Probabilities, ie p(attr|class= 0 or 1) '
#print scipy.exp(my_nbmodel.theta)
#print scipy.exp(my_nbmodel.pi)

import numpy as np
#get a confusion matrix
#the row is the true class label 0 or 1, columns are predicted label
#
nb_cf_mat=np.zeros([2,2])  #num of classes
for pnt in datax_col:
    predctn = my_nbmodel.predict(np.array(pnt.features))
    nb_cf_mat[pnt.label][predctn]+=1

#calculating error percentage
corrcnt=0 #number of correctly classified records
for i in range(2):
    corrcnt+=nb_cf_mat[i][i]
#number of correctly classified examples/ total number of examples
nb_per_corr=corrcnt/nb_cf_mat.sum()
print 'Naive Bayes: Conf.Mat. and Per Corr'
print nb_cf_mat
print nb_per_corr #0.857142857143

#---------------Decision Tree------------------------------#
from pyspark.mllib.tree import DecisionTree
dt_model = DecisionTree.trainClassifier(datax_rdd,2,{},impurity='entropy',maxDepth=3,maxBins=32, minInstancesPerNode=2)

#{} could be categorical feature list,
# To do regression, have no numclasses,and use trainRegression function

print dt_model.toDebugString()
#notice number of nodes are the predict (leaf nodes) and the ifs from the output of the above statement

#-----Performing evaluation of trained model, similar to the naive bayes case----#

#some checks,get some of training data and test it:
datax_col=datax_rdd.collect()   #if datax_rdd was big, use sample or take

#redo the conf. matrix code (it would be more efficient to pass a model)
dt_cf_mat=np.zeros([2,2])  #num of classes
for pnt in datax_col:
    predctn = dt_model.predict(np.array(pnt.features))
    dt_cf_mat[pnt.label][predctn]+=1
corrcnt=0
for i in range(2): 
    corrcnt+=dt_cf_mat[i][i]
dt_per_corr=corrcnt/dt_cf_mat.sum()

print 'Decision Tree: Conf.Mat. and Per Corr'
print dt_cf_mat
print dt_per_corr
