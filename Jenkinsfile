pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh '''
                    echo \"Hello from \$SHELL\"
                    ls /tmp
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
                    apt-get install -y docker-compose
                '''

                sh '''
                    apt-get install -y virtualenv python3 python3-pip
                    pip3 install virtualenvwrapper

                    echo "# Python Virtualenv Settings" >> ~/.bashrc
                    echo export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3 >> ~/.bashrc
                    echo export WORKON_HOME=\$HOME/.virtualenvs >> ~/.bashrc
                    echo export PROJECT_HOME=\$HOME/github_projects >> ~/.bashrc
                    source ~/.bashrc
                    mkvirtualenv thebox_dev -p ${VIRTUALENVWRAPPER_PYTHON}
                    workon thebox_dev

                    pip install -r requirements.txt
                    python workaround.py

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
