pipeline {
    agent any

    environment {
        USER = 'Ivan'
        IP   = '192.168.1.11'
    }

    stages {
        stage('Build') {
            steps {
                sh '''
                    apt-get update
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

                 sh '''

                 '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    cd thebox/docker
                '''
            }
        }

        stage('Deployment') {
            steps {
                sshagent(credentials : ['1ef423a1-271d-493c-a0ab-b4203dc005ee']) {
                    sh '''
                        ssh -A ${USER}@${IP} mkdir -p  C:/Temp/images
                        cd thebox/docker
                        mkdir -p /tmp/images
                        docker save -o /tmp/images/notif.tar amd64/thebox_notification
                        docker save -o /tmp/images/inf.tar amd64/thebox_inference
                        docker save -o /tmp/images/orch.tar amd64/thebox_orchestrator
                        docker save -o /tmp/images/kafka.tar amd64/thebox_kafka
                        docker save -o /tmp/images/zookeeper.tar amd64/thebox_zookeeper
                        docker save -o /tmp/images/couchdb.tar couchdb

                        ssh ${USER}@${IP} mkdir -p  C:/Temp/images
                        ssh ${USER}@${IP} mkdir -p  C:/Production

                        scp compose.yml ${USER}@${IP}:C:/Temp/images
                        scp -r /tmp/images ${USER}@${IP}:C:/Temp/images
                        scp -r ../services/src ${USER}@${IP}:C:/Production

                        ssh ${USER}@${IP} docker load -i C:/Temp/images/notif.tar
                        ssh ${USER}@${IP} docker load -i C:/Temp/images/inf.tar
                        ssh ${USER}@${IP} docker load -i C:/Temp/images/orch.tar
                        ssh ${USER}@${IP} docker load -i C:/Temp/images/kafka.tar
                        ssh ${USER}@${IP} docker load -i C:/Temp/images/zookeeper.tar
                        ssh ${USER}@${IP} docker load -i C:/Temp/images/couchdb.tar

                        ssh ${USER}@${IP} rm -r C:/Temp/images

                        ssh ${USER}@${IP} docker-compose -f C:/Temp/images/compose.yml up -d
                    '''
                }
            }
        }
    }
}