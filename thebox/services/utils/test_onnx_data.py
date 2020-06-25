# Example code to dump ONNX model meta-data
# To add a new cell, type '#%%'
# To add a new markdown cell, type '#%% [markdown]'
#%%
import onnxruntime
import numpy as np

#%%
onnx_model_file = os.path.join(os.getcwd(), 'model.onnx')
session = onnxruntime.InferenceSession(onnx_model_file, None)

#%%
# Verify the input/output of the model
print("Input(s):")
for (i, inp) in enumerate(session.get_inputs()):
    print(f"Input #{i} name  :{inp.name}")
    print(f"Input #{i} shape :{inp.shape}")
    print(f"Input #{i} type  :{inp.type}")

print("Output:")
for (i, outp) in enumerate(session.get_outputs()):
    print(f"Input #{i} name  :{outp.name}")
    print(f"Input #{i} shape :{outp.shape}")
    print(f"Input #{i} type  :{outp.type}")

#%%
def type_map(typename:str):
    if typename == "tensor(float)":
        return np.float32
    else:
        raise NotImplemented(f"TypeName: {typename}")

input_dict = {}
for inp in session.get_inputs():
    input_dict[inp.name] = np.random.random([1, inp.shape[1]]).astype(type_map(inp.type))

output_name = session.get_outputs()[0].name

#%%
result = session.run(
    [output_name], 
    input_dict
    )

#%%
result[0][0][0]


#%%
score_threshold = 0.4
scorer = lambda x: 1 if x > score_threshold else 0
labels = { 1: "work", 0: "play"}
labels[scorer(result[0])]
