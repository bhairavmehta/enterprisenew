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
                '''

                sh '''
                    apt-get install -y virtualenv python3 python3-pip
                    pip3 install virtualenvwrapper
                    mkdir ~/github_projects
                    echo "# Python Virtualenv Settings" >> ~/.bashrc
                    echo export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3 >> ~/.bashrc
                    echo export WORKON_HOME=\$HOME/.virtualenvs >> ~/.bashrc
                    echo export PROJECT_HOME=\$HOME/github_projects >> ~/.bashrc
                    source ~/.bashrc
                    ls
                    cd thebox/services
                    pip3 install -r requirements.txt
                    python3 workaround.py
                    ./build_dist.sh
                '''

                sh '''
                    cd ../docker
                    make
                '''
            }
        }
    }
}
