pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh '''
                    apt-get -y install apt-transport-https \
                         ca-certificates \
                         curl \
                         gnupg2 \
                         software-properties-common && \
                    curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg > /tmp/dkey; apt-key add /tmp/dkey && \
                    add-apt-repository \
                       "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
                       $(lsb_release -cs) \
                       stable" && \
                    apt-get update && \
                    apt-get -y install docker-ce

                    curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    chmod +x /usr/local/bin/docker-compose
                '''

                sh '''
                    apt-get install -y virtualenv python3 python3-pip
                    pip3 install virtualenvwrapper

                    mkdir -p ~/github_projects
                    rm ~/.bashrc
                    touch ~/.bashrc

                    echo "# Python Virtualenv Settings" >> ~/.bashrc
                    echo export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3 >> ~/.bashrc
                    echo export WORKON_HOME=~/.virtualenvs >> ~/.bashrc
                    echo export PROJECT_HOME=~/github_projects >> ~/.bashrc
                    echo source /usr/local/bin/virtualenvwrapper.sh >> ~/.bashrc
                    source ~/.bashrc

                    mkvirtualenv thebox_dev -p ${VIRTUALENVWRAPPER_PYTHON} || true
                    workon thebox_dev || true

                    apt-get install -y dos2unix
                    cd thebox/services
                    dos2unix build_dist.sh
                    pip install -r requirements.txt

                    cd ../docker
                    make
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    cd thebox/docker
                    docker-compose -f compose.yml up -d
                    docker run -d -p 1080:8080 --name swagger --restart always swaggerapi/swagger-ui:v2.2.9 || true
                    cd ../services
                    source ~/.bashrc
                    workon thebox_dev || true
                    export PYTHONPATH=`pwd`/src
                    cd src/thebox_testapp/keyStrokes
                    python3 ksNotify_app.py -s localhost:10001

                '''
            }
        }
    }
}