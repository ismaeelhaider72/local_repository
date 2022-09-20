pipeline {
    agent any

    stages {
        stage('Hello') {
            steps {
                echo 'Hello World'
                sh 'ls'
                sh 'pip3 install boto3'
                sh 'python3 main.py'
            }
        }
    }
}
