pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('5f8b634a-148a-4067-b996-07b4b3276fba')
        NVDAPIKEY = credentials('ed62b912-6db4-4d3a-a445-a1799077253e')
        SCANNER_HOME = tool 'sonar-scanner'
        DOCKERHUB_USERNAME = 'idrisniyi94'
        CART_DEPLOYMENT_NAME = 'cart-microservice'
        PRODUCT_DEPLOYMENT_NAME = 'product-microservice'
        IMAGE_TAG = "v.0.0.${env.BUILD_NUMBER}"
        CART_IMAGE_NAME = "${env.DOCKERHUB_USERNAME}/${env.CART_DEPLOYMENT_NAME}:${env.IMAGE_TAG}"
        PRODUCT_IMAGE_NAME = "${env.DOCKERHUB_USERNAME}/${env.PRODUCT_DEPLOYMENT_NAME}:${env.IMAGE_TAG}"
        BRANCH_NAME = "${env.GIT_BRANCH.split('/')[1]}"
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: '*/dev'], [name: '*/staging'], [name: '*/prod']], userRemoteConfigs: [[url: 'https://github.com/stwins60/microservice-demo.git']]])
            }
        }
        stage('Sonarqube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('sonar-server') {
                        sh "${env.SONAR_SCANNER_HOME}/bin/sonar-scanner -Dsonar.projectKey=microservice -Dsonar.projectName=microservice"
                    }
                }
            }
        }
        stage('OWASP') {
            steps {
                dependencyCheck additionalArguments: "--scan ./ --disableYarnAudit --disableNodeAudit --nvdApiKey ${env.NVDAPIKEY}", odcInstallation: 'DP-Check'
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }
        stage('Trivy FS Scan') {
            steps {
                script {
                    sh "trivy fs ."
                }
            }
        }
        stage("Login to DockerHub") {
            steps {
                sh "echo ${env.DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${env.DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                echo "Login Successful"
            }
        }
        stage("Docker Build") {
            steps {
                script {
                    dir('./cart-microservice') {
                        sh "docker build -t ${env.CART_IMAGE_NAME} ."
                        echo "Image built successfully"
                    }
                    dir('./product-microservice') {
                        sh "docker build -t ${env.PRODUCT_IMAGE_NAME} ."
                        echo "Image built successfully"
                    }
                }
            }
        }
        stage("Docker Push") {
            steps {
                script {
                    sh "docker push ${env.CART_IMAGE_NAME}"
                    sh "docker push ${env.PRODUCT_IMAGE_NAME}"
                }
            }
        }
        stage("Deploy") {
            steps {
                script {
                    dir('./k8s') {
                        kubeconfig(credentialsId: '3f12ff7b-93cb-4ea5-bc21-79bcf5fb1925', serverUrl: '') {
                            if (env.BRANCH_NAME == 'dev') {
                                sh "sed -i 's|{{CART_IMAGE_NAME}}|${env.CART_IMAGE_NAME}|g' overlays/dev/cart-microservice-patch.yaml"
                                sh "sed -i 's|{{PRODUCT_IMAGE_NAME}}|${env.PRODUCT_IMAGE_NAME}|g' overlays/dev/product-microservice-patch.yaml"
                                sh "kustomize build overlays/dev | kubectl apply -f -"
                                slackSend channel: '#alerts', color: 'good', message: "Cart and Product Microservices with tag ${env.IMAGE_TAG} deployed to dev"
                            } else if (env.BRANCH_NAME == 'staging') {
                                sh "sed -i 's|{{CART_IMAGE_NAME}}|${env.CART_IMAGE_NAME}|g' overlays/staging/cart-microservice-patch.yaml"
                                sh "sed -i 's|{{PRODUCT_IMAGE_NAME}}|${env.PRODUCT_IMAGE_NAME}|g' overlays/staging/product-microservice-patch.yaml"
                                sh "kustomize build overlays/staging | kubectl apply -f -"
                                slackSend channel: '#alerts', color: 'good', message: "Cart and Product Microservices with tag ${env.IMAGE_TAG} deployed to staging"
                            } else if (env.BRANCH_NAME == 'prod') {
                                sh "sed -i 's|{{CART_IMAGE_NAME}}|${env.CART_IMAGE_NAME}|g' overlays/prod/cart-microservice-patch.yaml"
                                sh "sed -i 's|{{PRODUCT_IMAGE_NAME}}|${env.PRODUCT_IMAGE_NAME}|g' overlays/prod/product-microservice-patch.yaml"
                                sh "kustomize build overlays/prod | kubectl apply -f -"
                                slackSend channel: '#alerts', color: 'good', message: "Cart and Product Microservices with tag ${env.IMAGE_TAG} deployed to prod"
                            }
                            else {
                                echo "No deployment for this branch"
                                slackSend channel: '#alerts', color: 'warning', message: "No deployment for this branch"
                            }
                        }
                    }
                }
            }
        }
    }
    post {
        success {
            slackSend channel: '#alerts', color: 'good', message: "${currentBuild.currentResult}: \nJOB_NAME: ${env.JOB_NAME} \nBUILD_NUMBER: ${env.BUILD_NUMBER} \nBRANCH_NAME: ${env.BRANCH_NAME}. \n More Info ${env.BUILD_URL}"
        }
        failure {
            slackSend channel: '#alerts', color: 'danger', message: "${currentBuild.currentResult}: \nJOB_NAME: ${env.JOB_NAME} \nBUILD_NUMBER: ${env.BUILD_NUMBER} \nBRANCH_NAME: ${env.BRANCH_NAME}. \n More Info ${env.BUILD_URL}"
        }
        aborted {
            slackSend channel: '#alerts', color: 'warning', message: "${currentBuild.currentResult}: \nJOB_NAME: ${env.JOB_NAME} \nBUILD_NUMBER: ${env.BUILD_NUMBER} \nBRANCH_NAME: ${env.BRANCH_NAME}. \n More Info ${env.BUILD_URL}"
        }
    }
}
