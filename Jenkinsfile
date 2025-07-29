pipeline {
    agent any

    environment {
        SCRIPT = 'generate_configs.py'
        CONFIG_FILE = 'gdevices.yaml'
        PATH = "${HOME}/.local/bin:${env.PATH}"
        PYTHONPATH = "${HOME}/.local/lib/python3.10/site-packages"
    }

    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                    if ! command -v pip3 > /dev/null; then
                        echo "[INFO] pip not found. Installing..."
                        wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py
                        python3 get-pip.py --user
                    fi
                    ~/.local/bin/pip3 install --user pyyaml
                '''
            }
        }

        stage('Check Config File') {
            steps {
                sh '''
                    echo "[INFO] Checking for config file: ${CONFIG_FILE}"
                    if [ ! -f "${CONFIG_FILE}" ]; then
                        echo "[ERROR] ${CONFIG_FILE} not found."
                        exit 1
                    fi

                    echo "[INFO] Printing contents of ${CONFIG_FILE} for debug:"
                    cat "${CONFIG_FILE}"
                '''
            }
        }

        stage('Run Generate Config Script') {
            steps {
                sh '''
                    echo "[INFO] Running Python script: ${SCRIPT}"
                    python3 "${SCRIPT}"
                '''
            }
        }
    }

    post {
        failure {
            echo '[ERROR] Pipeline failed. Please check the logs above for more details.'
        }
        success {
            echo '[INFO] Pipeline completed successfully.'
        }
    }
}
