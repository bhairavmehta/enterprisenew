pipeline {
    agent any

    environment {
        USER = 'ivan'
        IP   = '192.168.1.11'
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

                        ssh -A ${USER}@${IP} ls

                        ssh ${USER}@${IP} mkdir -p  C:/Temp/images
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