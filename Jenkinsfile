pipeline {
    agent any
    parameters {
        string(name: "STACK_NAME", defaultValue: "Transunion-SFTP", trim: true)
        string(name: "HOME_DIRECTORY", defaultValue: "dealeron-sftp-1", trim: true)
        string(name: "username", defaultValue: "gmariduena4", trim: true, description: "Sample string parameter")
    } 
    stages {
        stage('testing') {
            steps {
                sh """
                    echo "this is 14th change"
                    echo "Multiline shell steps works too"
                    ls -lah
                    pip3 install -r requirements.txt
                    export STACK_NAME=$params.STACK_NAME
                    export HOME_DIRECTORY=$params.HOME_DIRECTORY
                    export username=$params.username
                    python3 main.py
                """
            }
        }
    }
}
