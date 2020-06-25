pipeline {
    agent {
        docker {
            image 'node'
            args '-u root'
        }
    }
    stages {
        stage('Build') {
            steps {
                sh '''
                    echo \"Hello from \$SHELL\"
                    apt-get update
                    apt-get install -y docker-compose
                    apt-get install -y \\
                        apt-transport-https \\
                        ca-certificates \\
                        curl \\
                        gnupg-agent \\
                        software-properties-common
                    add-apt-repository ppa:ubuntu-sdk-team/ppa
                    apt-get update
                    apt-get install -y docker-ce
                '''

                sh '''
                    apt-get install -y virtualenv python3 python3-pip
                    pip3 install virtualenvwrapper
                    mkdir ~/github_projects
                    echo "# Python Virtualenv Settings" >> ~/.bashrc
                    echo export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3 >> ~/.bashrc
                    echo export WORKON_HOME=\$HOME/.virtualenvs >> ~/.bashrc
                    echo export PROJECT_HOME=\$HOME/github_projects >> ~/.bashrc
                    echo alias python=python3 >> ~/.bashrc
                    source ~/.bashrc
                    apt-get install -y dos2unix
                    cd thebox/services
                    dos2unix build_dist.sh

                    pip3 install wheel
                    python3 setup.py bdist_wheel

                    cd ../docker
                    make
                '''

            }
        }
    }
}
