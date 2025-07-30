pipeline {
    agent any

    environment {
        PATH = "${HOME}/.local/bin:${env.PATH}"
        PYTHONPATH = "${HOME}/.local/lib/python3.10/site-packages"
    }

    stages {
        stage('Install Requirements') {
            steps {
                sh '''
                    # Ensure pip is available
                    if ! command -v pip3 > /dev/null; then
                        wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py
                        python3 get-pip.py --user
                    fi

                    # Install dependencies
                    pip3 install --user netmiko jinja2 pyyaml
                '''
            }
        }

        stage('Generate and Push Configs') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'cisco-ssh-creds', usernameVariable: 'CISCO_USER', passwordVariable: 'CISCO_PASS')]) {
                    sh '''
                        echo "[INFO] Running configuration script..."
                        python3 generate_configs.py
                    '''
                }
            }
        }

        stage('Archive Rendered Configs') {
            steps {
                archiveArtifacts artifacts: 'rendered_configs/*.cfg', allowEmptyArchive: true
            }
        }
    }
}
