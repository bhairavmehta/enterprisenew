import getopt
import os
import sys
from typing import List
from flask import Flask
from thebox.common.config import Config
from dataclasses import dataclass
from flask_restful_swagger import swagger
from flask_restful import Api, Resource
from flask_cors import CORS


@dataclass
class APIResource(object):
    api_class: object
    path: str
    service_instance: object


def create_app(app_name, resources: List[APIResource]) -> Flask:
    """ Helper routine to create a rest API out of
        a flask-resultful Resource class
    """
    app = Flask(app_name)
    CORS(app)
    # Create Swagger Wrapper
    # Note:
    #  To debug the API in swagger:
    #     docker run -d -p 1080:8080 swaggerapi/swagger-ui:v2.2.9
    #     go to: http://localhost:1080/
    #     put in: http://127.0.0.1:5000/api/spec.json
    api = swagger.docs(Api(app), apiVersion='0.1')

    for res in resources:
        api.add_resource(
            res.api_class,
            res.path,
            resource_class_kwargs={'svc': res.service_instance}
        )

    return app
