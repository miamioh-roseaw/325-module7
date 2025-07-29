pipeline {
       agent any
       stages {
       stage('Render Templates') {
              steps {
            sh 'python3 generate_configs.py'
              }
       }
       }
}
