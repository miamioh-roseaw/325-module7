pipeline {
    agent any

    environment {
        PATH = "${HOME}/.local/bin:${env.PATH}"
        PYTHONPATH = "${HOME}/.local/lib/python3.10/site-packages"
        SCRIPT = "generate_configs.py"
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    if ! command -v pip3 > /dev/null; then
                        echo "[INFO] Installing pip..."
                        wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py
                        python3 get-pip.py --user
                    fi

                    echo "[INFO] Installing required libraries..."
                    ~/.local/bin/pip3 install --user netmiko pyyaml jinja2
                '''
            }
        }

        stage('Run Configuration Script') {
            steps {
                sh '''
                    echo "[INFO] Running configuration script..."
                    python3 ${SCRIPT}
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'rendered_configs/*.cfg', allowEmptyArchive: true
        }
    }
}
