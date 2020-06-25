# Script to create a simple ONNX file used in unit test

import tensorflow as tf
import numpy as np
from tensorflow import keras
import onnxmltools
import os

X = np.array([ [0,0,1], [0,1,1], [1,0,1], [1,1,1] ])
y = np.array([ [0], [1], [1], [0] ])

model = keras.Sequential()
input_layer = keras.layers.Dense(3, input_shape=[X.shape[1]], activation='tanh', name='main')
model.add(input_layer)
output_layer = keras.layers.Dense(1, activation='sigmoid', name='main_output')
model.add(output_layer) 
gd = tf.compat.v1.train.GradientDescentOptimizer(0.05)
model.compile(optimizer=gd, loss='mean_squared_error')
model.fit(X, y, epochs=1000, verbose=0, steps_per_epoch=10)

# see prediction
results = model.predict(X, verbose=0, steps=1)

print(f"truth:   {y}")
print(f"results: {results}")

# save the model
os.environ["TF_KERAS"]="1"
output_onnx_model = '../test/testdata/test_model.onnx'
onnx_model = onnxmltools.convert_keras(model)
onnxmltools.utils.save_model(onnx_model, output_onnx_model)

# load with ONNXRuntime to verify
import onnxruntime as ort

sess = ort.InferenceSession(output_onnx_model)
print("Input:")
for (i, inp) in enumerate(sess.get_inputs()):
    print(f"Input #{i} name  :{inp.name}")
    print(f"Input #{i} shape :{inp.shape}")
    print(f"Input #{i} type  :{inp.type}")
print("Output:")
for (i, outp) in enumerate(sess.get_outputs()):
    print(f"Input #{i} name  :{outp.name}")
    print(f"Input #{i} shape :{outp.shape}")
    print(f"Input #{i} type  :{outp.type}")

print("All done.")