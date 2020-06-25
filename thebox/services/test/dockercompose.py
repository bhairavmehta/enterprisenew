# Inspired by https://github.com/AndreLouisCaron/pytest-docker/blob/master/src/pytest_docker/__init__.py

import subprocess
import sys
import hashlib
from typing import List


def execute(command, success_codes=(0,)):
    """Run a shell command."""
    try:
        output = subprocess.check_output(
            command, stderr=subprocess.STDOUT, shell=True,
        )
        status = 0
    except subprocess.CalledProcessError as error:
        output = error.output or b''
        status = error.returncode
        command = error.cmd
    output = output.decode('utf-8')
    if status not in success_codes:
        raise Exception(
            'Command %r returned %d: """%s""".' % (command, status, output)
        )
    return output


class DockerComposeExecutor(object):
    def __init__(self, compose_files: List[str], compose_project_name: str):
        self._compose_files = compose_files
        self._compose_project_name = compose_project_name

    def execute(self, subcommand):
        command = "docker-compose"
        for compose_file in self._compose_files:
            command += ' -f "{}"'.format(compose_file)
        command += ' -p "{}" {}'.format(self._compose_project_name, subcommand)
        return execute(command)


def get_temp_compose_file(project_name: str):
    sha = hashlib.sha256()
    sha.update(project_name.encode())
    project_name_hash = sha.hexdigest()[-8:]
    return f"_dc_{project_name_hash}.yml.temp"


def setup_test_containers_with_docker_compose(compose_file_content: str, project_name: str):
    temp_compose_file = get_temp_compose_file(project_name)
    with open(temp_compose_file, 'w', encoding="utf-8") as f:
        f.write(compose_file_content)
    docker_compose = DockerComposeExecutor([temp_compose_file], project_name)
    docker_compose.execute('up --build -d')


def remove_test_containers_with_docker_compose(project_name: str):
    temp_compose_file = get_temp_compose_file(project_name)
    docker_compose = DockerComposeExecutor([temp_compose_file], project_name)
    docker_compose.execute('down -v')
