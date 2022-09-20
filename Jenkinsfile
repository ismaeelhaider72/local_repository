pipeline {
    agent any
    stages {
        stage('testing') {
            steps {
                sh '''
                    echo "Multiline shell steps works too"
                    ls -lah
                    pip3 install -r requirements.txt
                    python3 main.py
                '''
            }
        }
    }
}
