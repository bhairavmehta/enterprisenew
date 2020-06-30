pipeline {
    agent any

    environment {
        USER   = 'ivan'
        IP     = '192.168.1.11'
        TMP    = 'C:\\Temp\\jenkins'
        PROD   = 'C:\\Production'
        IMAGES = 'C:\\Temp\\jenkins\\images\\'
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
                        cd thebox/docker
                        mkdir -p /tmp/images
                        docker save -o /tmp/images/notif.tar amd64/thebox_notification


                        ssh ${USER}@${IP} mkdir ${TMP} || true
                        ssh ${USER}@${IP} mkdir ${PROD} || true

                        scp compose.yml ${USER}@${IP}:${TMP}
                        scp -r /tmp/images ${USER}@${IP}:${TMP}
                        scp -r ../services/src ${USER}@${IP}:${PROD}
                        rm -r /tmp/images

                        ssh ${USER}@${IP} docker load -i ${IMAGES}notif.tar

                        ssh ${USER}@${IP} docker-compose -f ${TMP}\\compose.yml up -d
                        ssh ${USER}@${IP} rm -r ${TMP}
                    '''
                }
            }
        }
    }
}