from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name = 'thebox_inference',
      version = version,
      description = 'Inference Service for The Box',
      author = 'Jerry liang',
      author_email = 'jerrylia@microsoft.com',
      url = None,
      packages = [
            "thebox.common",
            "thebox.common_svc",
            "thebox.db_couchdb",
            "thebox.pubsub_kafka",
            "thebox.messages",
            "thebox.inference"
      ],
      package_dir={"": "src"},
      include_package_data = True,
      zip_safe = False,
      entry_points = {'service':['service = thebox.inference:main']},
      install_requires = [
                          'pyyaml',
                          'dataclasses',
                          'couchdb',
                          'cloudant',
                          'jsonpickle',
                          'confluent-kafka',
                          'numpy'
      ],
      extras_require = {
            "tf": ["tensorflow>=1.14.0,<2.0"],
            "tf_gpu": ["tensorflow-gpu>=1.14.0,<2.0"],
            "ort": ["onnxruntime>=0.5.0"],
            "ort_gpu": ["onnxruntime-gpu>=0.5.0"],
            "ort_gpu_trt": ["onnxruntime-gpu-tensorrt>=0.5.0"]
      }
      )