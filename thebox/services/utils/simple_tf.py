# Script to create a simple Tensorflow model file used in unit test

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

output_tf_model = '../test/testdata/test_model.pb'

# reference:
#  https://stackoverflow.com/questions/45466020/how-to-export-keras-h5-to-tensorflow-pb
def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
    """
    Freezes the state of a session into a pruned computation graph.

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    pruned so subgraphs that are not necessary to compute the requested
    outputs are removed.
    @param session The TensorFlow session to be frozen.
    @param keep_var_names A list of variable names that should not be frozen,
                          or None to freeze all the variables in the graph.
    @param output_names Names of the relevant graph outputs.
    @param clear_devices Remove the device directives from the graph for better portability.
    @return The frozen graph definition.
    """
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(set(v.op.name for v in tf.compat.v1.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf.compat.v1.global_variables()]
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        frozen_graph = tf.graph_util.convert_variables_to_constants(
            session, input_graph_def, output_names, freeze_var_names)
        return frozen_graph

sess = tf.compat.v1.keras.backend.get_session()
frozen_graph = freeze_session(sess, output_names=[out.op.name for out in model.outputs])

# Finally we serialize and dump the output graph to the filesystem
tf.io.write_graph(frozen_graph, "./", output_tf_model, as_text=False)

# load it with TF to verify the out
assert(os.path.exists(output_tf_model))

print("All done.")