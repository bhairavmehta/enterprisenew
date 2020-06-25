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
                    make
                '''
            }
        }
    }
}


