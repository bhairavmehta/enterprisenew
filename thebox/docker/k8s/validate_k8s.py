from jsonschema import validate, ValidationError
import json
import getopt
import sys
import os

""" This tool validate Kubernetes deployment json files against the 
    provided Kubernetes spec schema.
   
    For jsonschema validation library, see:
       https://github.com/Julian/jsonschema
    For Kubernetes schema, see:
       https://github.com/garethr/kubernetes-json-schema
"""


def printhelp():
    print("Usage:")
    print(
        "   python validate_k8s.py -j [k8s_json_file_to_validate] -s [schema_root_path]")
    print("The k8s_json_file_to_validate should have one json object per-line.")
    print("The schema root path is from following url:")
    print("  https://github.com/garethr/kubernetes-json-schema")


json_file = 'thebox.json.tmp'
schema_folder = '~/github/kubernetes-json-schema/v.1.13.5-standalone'

# Parse argments
try:
    opts, args = getopt.getopt(sys.argv[1:], "hj:s:", ["json=", "schema="])
except getopt.GetoptError:
    printhelp()
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        printhelp()
        sys.exit()
    elif opt in ("-j", "--json"):
        json_file = arg
    elif opt in ("-s", "--schema"):
        schema_folder = arg

# Print arguments
print("Running validations with parameters:")
print(f"  json: {json_file}")
print(f"  schema: {schema_folder}")

# list of supported schema types
k8s_schemas = {
    "Deployment": "deployment.json",
    "Service": "service.json",
    "PersistentVolume": "persistentvolume.json",
    "PersistentVolumeClaim": "persistentvolumeclaim.json"
}

# do actual validation:
with open(json_file, 'r') as f:
    for idx, line in enumerate(f):

        # schema validation
        json_obj = json.loads(line)
        metadata = json_obj.get('metadata', None)
        name = None if metadata is None else metadata.get('name', None)
        kind = json_obj['kind']
        validate_file = os.path.join(schema_folder, k8s_schemas[kind])
        print(f"Validating {name} with {validate_file} ...")
        with open(validate_file, 'r') as fv:
            fv_content = json.loads(fv.read())
        try:
            validate(instance=json_obj, schema=fv_content)
        except ValidationError as e:
            print(f"Validation failed for line '{idx}' with name '{name}':")
            print(f"{json_obj}")
            print(f"")
            print(f"Error:")
            print(f"{e}")
            exit(1)

        # other validations
        if "${" in line:
            print(f"Validation failed for line '{idx}' with name '{name}':")
            print(f"{json_obj}")
            print("Some variables were not expanded")
            exit(1)

print("All validations done successfully.")
