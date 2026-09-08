pipeline {
    agent any

    environment {
        APP_NAME = 'aws-guardian'
        BACKEND_IMAGE = 'aws-guardian-backend:latest'
        FRONTEND_IMAGE = 'aws-guardian-frontend:latest'
    }

    stages {
        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Build Containers') {
            steps {
                echo "Building backend and frontend production images..."
                sh '''
                    docker build -t ${BACKEND_IMAGE} ./backend
                    docker build -t ${FRONTEND_IMAGE} ./frontend
                '''
            }
        }

        stage('Deploy Services') {
            steps {
                echo "Deploying AWS Guardian containers via Docker Compose..."
                sh '''
                    # Stop any running instances cleanly
                    docker compose down || true

                    # Launch new backend (port 8000) and frontend (port 80)
                    docker compose up -d --build
                '''
            }
        }

        stage('Health & Sanity Check') {
            steps {
                echo "Validating active services..."
                sh '''
                    sleep 5
                    docker ps --filter name=guardian-
                    curl -f http://127.0.0.1:8000/api/health || exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "AWS Guardian deployment completed successfully."
        }
        failure {
            echo "Deployment failed. Rolling back or checking logs..."
            sh 'docker logs guardian-backend --tail 50 || true'
        }
    }
}