pipeline{
    agent any
    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = "ornate-opus-460612-h1"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages{
        stage('Cloning github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins ...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/shahab460/MLOPS-PROJECT-1.git']])
                }
            }
        }

        stage('Setting up virtual environment and installing dependencies'){
            steps{
                script{
                    echo 'Setting up virtual environment and installing dependencies ...'
                    sh '''
                    python -m venv "${VENV_DIR}"
                    . "${VENV_DIR}/bin/activate"
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }

        stage('Run Training Pipeline'){
            steps{
                script{
                    echo 'Running training pipeline...'
                    sh '''
                    . "${VENV_DIR}/bin/activate"
                    python pipeline/training_pipeline.py
                    '''
                }
            }
        }

        stage('Building and pushing Docker image to GCR'){
            steps{
                script{
                    withCredentials([file(credentialsId : 'gcp-key', variable : 'GOOGLE_APPLICATION_CREDENTIALS')]){
                        script{
                            echo "Building and publishing Docker image to GCR ..."
                            sh '''
                            export PATH=$PATH:${GCLOUD_PATH}

                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                            gcloud config set project ${GCP_PROJECT}

                            gcloud auth configure-docker --quiet

                            docker build -t gcr.io/${GCP_PROJECT}/ml-project:latest .

                            docker push gcr.io/${GCP_PROJECT}/ml-project:latest
                            '''
                        }
                    }
                }
            }
        }
    }
}