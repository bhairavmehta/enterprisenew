#
# Description: load with ONNXRuntime to verify if a given frozen Tensorflow model is valid, and if so,
# dump the nodes for the model
#

import tensorflow as tf
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

    pb_file_name = "model.pb"

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
            pb_file_name = arg

    with tf.Session() as sess:
        print(f"Reading {pb_file_name}:")
        with tf.io.gfile.GFile(pb_file_name,'rb') as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
            sess.graph.as_default()

            tf.import_graph_def(graph_def, name='')

            graph_nodes = [n for n in graph_def.node]
            print(f"Nodes (total = {len(graph_nodes)}):")
            for t in graph_nodes:
                print(f"  {t.name}")

main()