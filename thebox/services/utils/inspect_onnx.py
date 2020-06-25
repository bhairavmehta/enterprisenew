#
# Description: load with ONNXRuntime to verify if a given ONNX model is valid, and if so,
# dump the input/output for the model
#

import onnxruntime as ort
import getopt
import sys

def printhelp():
    help = """
Usage:
    python inspect_onnx.py -f <filename.onnx>
"""
    print(help)


def main():
    """Try to parse using ONNXRuntime and dump some informations of the model
    """

    onnx_file_name = "model.onnx"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["file="])
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit()
        elif opt in ("-f", "--file"): # e.g. localhost:9092
            onnx_file_name = arg


    print(f"Reading {onnx_file_name}:")
    sess = ort.InferenceSession(onnx_file_name)
    
    print("Input:")
    for (i, inp) in enumerate(sess.get_inputs()):
        print(f"  #{i} name  : {inp.name}")
        print(f"  #{i} shape : {inp.shape}")
        print(f"  #{i} type  : {inp.type}")

    print("Output:")
    for (i, outp) in enumerate(sess.get_outputs()):
        print(f"  #{i} name  : {outp.name}")
        print(f"  #{i} shape : {outp.shape}")
        print(f"  #{i} type  : {outp.type}")


main()