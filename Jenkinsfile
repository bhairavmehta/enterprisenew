pipeline {
    agent any

    environment {
        USER        = 'ivan'
        IP          = '172.20.10.2'
        TMP         = 'C:\\Temp\\thebox'
        PROD        = 'C:\\Production'
        IMAGES      = 'C:\\Temp\\thebox\\images\\'
        MODEL_PATH  = 'C:\\Users\\Ivan\\Desktop\\Work\\Bhairav-Mehta' // Path to keystrokes.onnx model
        CREDENTIALS = '	99d151bc-aedf-401d-8c55-09732143f08b'
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
                    cd ../services
                    docker build -t thebox/demo .
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
                sshagent(credentials : ["${env.CREDENTIALS}"]) {
                    sh '''
                        mkdir -p ~/.ssh
                        touch ~/.ssh/known_hosts
                        ssh-keyscan -H ${IP} >> ~/.ssh/known_hosts

                        cd thebox/docker
                        mkdir -p /tmp/images
                        docker save -o /tmp/images/notif.tar amd64/thebox_notification
                        docker save -o /tmp/images/inf.tar amd64/thebox_inference
                        docker save -o /tmp/images/orch.tar amd64/thebox_orchestrator
                        docker save -o /tmp/images/kafka.tar amd64/thebox_kafka
                        docker save -o /tmp/images/zookeeper.tar amd64/thebox_zookeeper
                        docker save -o /tmp/images/demo.tar thebox/demo

                        ssh ${USER}@${IP} mkdir ${TMP} || true
                        ssh ${USER}@${IP} mkdir ${PROD} || true

                        scp compose.yml ${USER}@${IP}:${TMP}
                        scp -r /tmp/images ${USER}@${IP}:${TMP}
                        scp -r ../services/src ${USER}@${IP}:${PROD}
                        rm -r /tmp/images

                        ssh ${USER}@${IP} docker run -dit --restart always --name onnx_server -p 8082:80 -v "${MODEL_PATH}":/usr/local/apache2/htdocs/ httpd:2.4 || true

                        ssh ${USER}@${IP} docker load -i ${IMAGES}notif.tar
                        ssh ${USER}@${IP} docker load -i ${IMAGES}inf.tar
                        ssh ${USER}@${IP} docker load -i ${IMAGES}orch.tar
                        ssh ${USER}@${IP} docker load -i ${IMAGES}kafka.tar
                        ssh ${USER}@${IP} docker load -i ${IMAGES}zookeeper.tar
                        ssh ${USER}@${IP} docker load -i ${IMAGES}demo.tar

                        ssh ${USER}@${IP} docker-compose -f ${TMP}/compose.yml up -d
                        ssh ${USER}@${IP} rm -r ${IMAGES}

                        ssh ${USER}@${IP} curl -X PUT --header "Content-Type: application/json" --header "Accept: application/json" -d @C:\\Production\\src\\thebox_testapp\\keyStrokes\\ksScenario.json "http://127.0.0.1:10002/scenario"
                        ssh ${USER}@${IP} docker exec thebox_demo_1 python3.6 main.py --frontend_ip 0.0.0.0 --pubsub_endpoint kafka-pubsub:9092
                    '''
                }
            }
        }
    }
}