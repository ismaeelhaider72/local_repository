pipeline {
    agent any

    stages {
        stage('Hello') {
            steps {
                echo 'Hello World'
                sh 'ls'
                sh 'pip3 install -r requirements.txt'
            }
        }

    stage('building jekyll') {
        steps {
            script {
                sh script:'''
                    #!/bin/bash
                    export STACK_NAME="Transunion-SFTP"
                    export HOME_DIRECTORY="dealeron-sftp-1"
                    export username=="gmariduena"
                    python3 --version
                    python3.7 main.py
                    '''
            }
        }
    }

    }
}
