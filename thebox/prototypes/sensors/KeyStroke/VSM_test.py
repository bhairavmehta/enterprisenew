 
import pandas as pd
import numpy as np
from sklearn import model_selection, preprocessing, linear_model, naive_bayes, metrics, svm
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn import decomposition, ensemble

import pickle

corpus=pd.read_csv(r"C:\temp\\training.csv",encoding='latin-1')
corpus['text'] = [entry.lower() for entry in corpus['text']]

#instantiate CountVectorizer()

train_x, valid_x, train_y, valid_y = model_selection.train_test_split(corpus['text'], corpus['label'], test_size=0.10)

encoder = preprocessing.LabelEncoder()
train_y = encoder.fit_transform(train_y)
valid_y = encoder.fit_transform(valid_y)
fi=open( 'c:\\temp\\vocabulary.pkl','rb')
vocabulary=pickle.load(fi)

count_vect=CountVectorizer(analyzer='word', token_pattern=r'\w{1,}', vocabulary = vocabulary)
print(count_vect.vocabulary)
xvalid_count =  count_vect.transform(valid_x)


fi2=open( 'c:\\temp\\tfidfvocabulary.pkl','rb')
tfidf_vect=pickle.load(fi2) 

#tfidf_vect.vocabulary_=pll
#print(vocabulary_)

filename = 'c:\\temp\\svm_model.sav'
loaded_model = pickle.load(open(filename, 'rb'))
#tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', vocabulary =vocabulary, max_features=5000)

print(tfidf_vect.vocabulary_)
xvalid_tfidf1 =  tfidf_vect.transform(valid_x)
xvalid_tfidf = xvalid_tfidf1.toarray()
print(xvalid_tfidf1 )

predictions=loaded_model.predict(xvalid_tfidf)
accuracy=metrics.accuracy_score(predictions, valid_y)
print(accuracy)