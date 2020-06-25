
def patch_1():
    """ This function patches the swagger lib issue
        where getfullargspec should be used in place of
        getargspec
    """
    from flask_restful_swagger import swagger
    swagger_py = swagger.__file__

    new_content = None
    with open(swagger_py, 'r') as content_file:
        content = content_file.read()
        if ".getargspec(" in content:
            new_content = content.replace(".getargspec(", ".getfullargspec(")
        else:
            print("No patching for swagger is needed.")

    if new_content is not None:
        with open(swagger_py, 'w') as content_file:
            content_file.write(new_content)
            print("Swagger has sucessfully been patched.")


if __name__ == "__main__":
    patch_1()
