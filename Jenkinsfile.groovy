pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Download git repo') {
            steps {
                echo '===============downloading git repo==================='
                script {
                    if (isUnix()) {
                        sh 'rm -rf tg-reminber-bot'
                        sh 'git clone --depth=1 https://github.com/MaxGoryunov/tg-reminber-bot.git'
                        sh 'rm -rf tg-reminber-bot/.git*'
                    } else {
                        bat 'powershell -Command "Get-ChildItem -Path .\\* -Recurse | Remove-Item -Force -Recurse"'
                        bat 'git clone  https://github.com/MaxGoryunov/tg-reminber-bot.git'
                        bat 'powershell Remove-Item tg-reminber-bot/.git* -Recurse -Force'
                    }
                }
                echo '===============git repo downloaded==================='
            }
        }
        stage('Getting creds and env variables') {
            steps {
                echo '===============getting env variables==================='
                withCredentials([file(credentialsId: 'ENV', variable: 'ENV'), file(credentialsId: 'CREDS', variable: 'CREDS'), file(credentialsId: 'TOKEN', variable: 'TOKEN')]) {
                    script {
                        if (isUnix()) {
                            sh 'cp $ENV ./tg-reminber-bot/.env'
                            sh 'cp $REDS ./tg-reminber-bot/credentials.json'
                            sh 'cp $TOKEN ./tg-reminber-bot/token.json'
                        } else {
                            bat 'powershell Copy-Item %ENV% -Destination ./tg-reminber-bot/.env'
                            bat 'powershell Copy-Item %CREDS% -Destination ./tg-reminber-bot/credentials.json'
                            bat 'powershell Copy-Item %TOKEN% -Destination ./tg-reminber-bot/token.json'
                        }
                    }
                }
                echo '===============got creds and env variables==================='
            }
        }
    }
    post {
        success {
            echo '===============run docker==================='
                script {
                    if (isUnix()) {
                        sh 'cd tg-reminber-bot && docker-compose up -d --build'
                    } else {
                        bat 'cd tg-reminber-bot && docker-compose up -d --build'
                    }
                }
                echo '===============docker container is running successfully==================='
            }
        }
    }