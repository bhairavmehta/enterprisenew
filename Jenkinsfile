pipeline {
    agent any

    environment {
        USER = 'ivan'
        IP   = '192.168.1.11'
        TMP  = 'C:\\Temp\\images'
        PROD = 'C:\\Production'
    }

    stages {
        stage('Build') {
            steps {
                sh ''
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
                        ssh ${USER}@${IP} mkdir -p ${TMP}
                        cd thebox/docker
                        mkdir -p /tmp/images
                        docker save -o /tmp/images/notif.tar amd64/thebox_notification
                        docker save -o /tmp/images/inf.tar amd64/thebox_inference
                        docker save -o /tmp/images/orch.tar amd64/thebox_orchestrator
                        docker save -o /tmp/images/kafka.tar amd64/thebox_kafka
                        docker save -o /tmp/images/zookeeper.tar amd64/thebox_zookeeper
                        docker save -o /tmp/images/couchdb.tar couchdb

                        ssh ${USER}@${IP} mkdir -p ${TMP}
                        ssh ${USER}@${IP} mkdir -p ${PROD}

                        scp compose.yml ${USER}@${IP}:${TMP}
                        scp -r /tmp/images ${USER}@${IP}:${TMP}
                        scp -r ../services/src ${USER}@${IP}:${PROD}

                        ssh ${USER}@${IP} docker load -i ${TMP}\\notif.tar
                        ssh ${USER}@${IP} docker load -i ${TMP}\\inf.tar
                        ssh ${USER}@${IP} docker load -i ${TMP}\\orch.tar
                        ssh ${USER}@${IP} docker load -i ${TMP}\\kafka.tar
                        ssh ${USER}@${IP} docker load -i ${TMP}\\zookeeper.tar
                        ssh ${USER}@${IP} docker load -i ${TMP}\\couchdb.tar

                        ssh ${USER}@${IP} rm -r ${TMP}

                        ssh ${USER}@${IP} docker-compose -f ${TMP}\\compose.yml up -d
                    '''
                }
            }
        }
    }
}