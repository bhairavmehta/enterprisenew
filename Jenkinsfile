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
                    apt-get update
                    apt-get install docker-compose
                '''

                sh '''
                    apt-get install virtualenv python3 python3-pip
                    -H pip3 install virtualenvwrapper
                    mkdir ~/github_projects
                    echo "# Python Virtualenv Settings" >> ~/.bashrc
                    echo export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.6 >> ~/.bashrc
                    echo export WORKON_HOME=\$HOME/.virtualenvs >> ~/.bashrc
                    echo export PROJECT_HOME=\$HOME/github_projects >> ~/.bashrc
                    echo source /usr/local/bin/virtualenvwrapper.sh >> ~/.bashrc
                    source ~/.bashrc
                    mkvirtualenv thebox_dev -p ${VIRTUALENVWRAPPER_PYTHON}'
                    workon thebox_dev
                '''
                sh '''
                    cd /repo/enterprise.mhhd/thebox/services
                    pip install -r requirements.txt
                    python workaround.py
                '''

                sh '''
                    cd /repo/enterprise.mhhd/thebox/services
                    pip install -r requirements.txt
                    python workaround.py
                    ./build_dist.sh
                '''

                sh '''
                    make
                '''
            }
        }
    }
}


