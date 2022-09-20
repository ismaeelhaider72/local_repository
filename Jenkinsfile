pipeline {
    agent any
    stages {
        stage('testing') {
            steps {
                sh '''
                    echo "Multiline shell steps works too"
                    ls -lah
                    pip3 install -r requirements.txt
                    export STACK_NAME="Transunion-SFTP"
                    export HOME_DIRECTORY="dealeron-sftp-1"
                    export username="gmariduena1"
                    python3 main.py
                '''
            }
        }
    }
}
