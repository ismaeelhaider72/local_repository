pipeline {
    agent any
    parameters {
        string(name: "STACK_NAME")
        string(name: "HOME_DIRECTORY")
        string(name: "username")
    } 
    stages {
        stage('testing') {
            steps {
                sh '''
                    echo "Multiline shell steps works too"
                    ls -lah
                    pip3 install -r requirements.txt
                    export STACK_NAME=$params.STACK_NAME
                    export HOME_DIRECTORY=$params.HOME_DIRECTORY
                    export username=$params.username
                    echo $STACK_NAME
                    echo $HOME_DIRECTORY 
                    echo $username 
                    echo $params.STACK_NAME
                    echo $params.HOME_DIRECTORY
                    echo $params.username
                    python3 main.py
                '''
            }
        }
    }
}
