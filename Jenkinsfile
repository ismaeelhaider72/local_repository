pipeline {
    agent { any } 
    stages {
        stage('testing') {
            steps {
                sh '''
                    echo "Multiline shell steps works too"
                    ls -lah
                '''
            }
        }
    }
}
