# -*- coding: utf-8 -*-
"""
Sentiment Classification in BERT
"""

#installing transformers
!pip install transformers

#importing important libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import torch
import transformers as ppb

#reading dataset
data=pd.read_csv('https://github.com/clairett/pytorch-sentiment-classification/raw/master/data/SST2/train.tsv', delimiter='\t', header=None)

#creating a batch of 2000 data from dataset
batch_1=data[:2000]

#checking dataset
batch_1.head(3)

print(batch_1[0][1])

#counting number of positive(1) and negative(0) in output column
batch_1[1].value_counts()

"""Loading Pre-trained BERT Model"""

#loading DistilBERT:
model_class, tokenizer_class, pretrained_weights = (ppb.DistilBertModel, ppb.DistilBertTokenizer, 'distilbert-base-uncased')

#We can also use Original BERT with below line of code:
#model_class, tokenizer_class, pretrained_weights = (ppb.BertModel, ppb.BertTokenizer, 'bert-base-uncased')

#loading pre-trained tokenizer and pre-trained model of bert with pre-trained weights
tokenizer = tokenizer_class.from_pretrained(pretrained_weights)
model = model_class.from_pretrained(pretrained_weights)

"""Model #1 Preparing(pre-processing) the dataset"""

#Tokenization (it creates list for every sentence and inside the list there are tokens(words))
tokenized = batch_1[0].apply((lambda x: tokenizer.encode(x, add_special_tokens=True)))

#Padding sentence to make them same sized.
max_len = 0
for i in tokenized.values:
    if len(i) > max_len:
        max_len = len(i)
print("Calculated Max. Length is : ",max_len)
padded = np.array([i + [0]*(max_len-len(i)) for i in tokenized.values])

#checking dimensions of dataset
np.array(padded).shape

#creating attention mask of each data , if padding is not = 0 keep 1, if padding is not = 1 keep 0
attention_mask = np.where(padded != 0, 1, 0)
attention_mask.shape

"""Creating Deep Learnig model"""

#creating tensor(datatype) from preprocessed data for input
input_ids = torch.tensor(padded)
attention_mask = torch.tensor(attention_mask)

"""Feature Extraction"""

#disabling gradient computation and calculating last hidden states
with torch.no_grad():
  last_hidden_states = model(input_ids, attention_mask=attention_mask)

"""Explaination of how features are getting extracted
<img src="https://jalammar.github.io/images/distilBERT/bert-output-tensor-selection.png" />
"""

#extracting Feature from the last hidden state
features = last_hidden_states[0][:,0,:].numpy()

#storing labels of the data in a variable "Labels"
labels = batch_1[1]

"""Train/Test Split from Batch_1"""

#splitting training and testing data from features and labels
train_features, test_features, train_labels, test_labels = train_test_split(features, labels)

"""Creating Logistic Regression Model And fitting training data"""

lr= LogisticRegression()
lr.fit(train_features, train_labels) #fitting training data(features and labels)

"""Evaluating The model"""

#finding the score by putting testing data
print("Accuracy : ",((lr.score(test_features, test_labels))*100),"%")

"""# **Extra**

This is the code to predict sentiments with user input string , with the help of above trained model.


Note: This will only works if you have already trained a sentiment analysis model using BERT with name "model".
"""

#Creating Cell for preprocessing and prediction of sentiment from BERT

#taking input and converting into lower case.
input1=input("Enter sentence for sentiment analysis : ").lower()

#importing transformers library and creating model and tokenizer
# import transformers as ppb
# model_class, tokenizer_class, pretrained_weights = (ppb.DistilBertModel, ppb.DistilBertTokenizer, 'distilbert-base-uncased')
# tokenizer = tokenizer_class.from_pretrained(pretrained_weights)

#below line is to create new model with dataset
#model= model_class.from_pretrained(pretrained_weights)

#below line is to tokenize multiple input
# tokenized = batch_1[0].apply((lambda x: tokenizer.encode(x, add_special_tokens=True)))

#tokenizing single input
tokenized1=tokenizer.encode(input1)

#in our model max length of sentence is 59 so we will do padding according to that. The length may change in different model.
max_len1=59

#padding single input
padded1 = np.array(tokenized1 + [0]*(max_len1-len(tokenized1)))

#creating attention mask
attention_mask1 = np.where(padded1 != 0, 1, 0)

#creating tensors
input_ids1 = torch.tensor(padded1)
attention_mask1 = torch.tensor(attention_mask1)

#resizing tensors to the max. length
input_ids1.resize_(1,59)
attention_mask1.resize_(1,59)

#extracting last hidden state from single output
with torch.no_grad():
#model used below is pretrained , if you don't have pretrained model . you have to train a model first.
  last_hidden_states1 = model(input_ids1, attention_mask=attention_mask1)

#extracting feature used to predict output
features1 = last_hidden_states1[0][:,0,:].numpy()

#using pretrained logistic regression model to predict output
output=lr.predict(features1)

print("Output = ",output)
