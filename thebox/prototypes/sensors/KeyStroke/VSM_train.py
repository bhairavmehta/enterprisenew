
 
import pandas as pd
import numpy as np
from sklearn import model_selection, preprocessing, linear_model, naive_bayes, metrics, svm
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn import decomposition, ensemble

#import onnxruntime as rt

 
# this is a very toy example, do not try this at home unless you want to understand the usage differences

corpus=pd.read_csv(r"C:\temp\\training.csv",encoding='latin-1')
corpus['text'] = [entry.lower() for entry in corpus['text']]

#instantiate CountVectorizer()

train_x, valid_x, train_y, valid_y = model_selection.train_test_split(corpus['text'], corpus['label'], test_size=0.10)

# label encode the target variable 
encoder = preprocessing.LabelEncoder()
train_y = encoder.fit_transform(train_y)
valid_y = encoder.fit_transform(valid_y)
#print(valid_x.shape)
#Feature engineering
# create a count vectorizer object 
count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}')
count_vect.fit(corpus['text'])
print(count_vect.vocabulary_)
print(count_vect.get_feature_names())
fi=open( 'c:\\temp\\vocabulary.pkl','wb')
pickle.dump(count_vect.get_feature_names(), fi)
# transform the training and validation data using count vectorizer object
xtrain_count =  count_vect.transform(train_x)
xvalid_count =  count_vect.transform(valid_x)
cv=CountVectorizer()

# word level tf-idf
tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', max_features=5000)
tfidf_vect.fit(corpus['text'])

xtrain_tfidf1 =  tfidf_vect.transform(train_x)
xvalid_tfidf1 =  tfidf_vect.transform(valid_x)
xtrain_tfidf = xtrain_tfidf1.toarray()
xvalid_tfidf =xvalid_tfidf1.toarray()

svm=svm.SVC(kernel='rbf', C=10.0, gamma=0.1, random_state=1)

classifier=svm.fit(xtrain_tfidf, train_y)
predictions=classifier.predict(xvalid_tfidf)
accuracy=metrics.accuracy_score(predictions, valid_y)



print("SVM, accuracy: ", accuracy)

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

initial_type = [('float_input', FloatTensorType([1,295]))]
onx = convert_sklearn(classifier, initial_types=initial_type)

with open("c:\\temp\\svm_5.onnx.tmp", "wb") as f:
    f.write(onx.SerializeToString())

print("done")
print(xvalid_tfidf[0])
import onnx
model = onnx.load("c:\\temp\\svm_5.onnx.tmp")
#print(model)

sess = rt.InferenceSession("c:\\temp\\svm_5.onnx.tmp")
input_name = sess.get_inputs()[0].name
label_name = sess.get_outputs()[0].name
print(input_name)
print(label_name)

pred_onx = sess.run([label_name], {input_name: xvalid_tfidf[0].astype(np.float32)})[0]

print(pred_onx == valid_y[0])