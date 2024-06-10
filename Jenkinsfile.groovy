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
                        sh 'rm -rf reminder_bot'
                        sh 'git clone --depth=1 https://github.com/MaxGoryunov/tg-reminber-bot.git'
                        sh 'rm -rf reminder_bot/.git*'
                    } else {
                        bat 'powershell -Command "Get-ChildItem -Path .\\* -Recurse | Remove-Item -Force -Recurse"'
                        bat 'git clone --depth=1 https://github.com/MaxGoryunov/tg-reminber-bot.git'
                        bat 'powershell Remove-Item reminder_bot/.git* -Recurse -Force'
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
                            sh 'cp $ENV ./reminder_bot/.env'
                            sh 'cp $REDS ./reminder_bot/credentials.json'
                            sh 'cp $TOKEN ./reminder_bot/token.json'
                        } else {
                            bat 'powershell Copy-Item %ENV% -Destination ./reminder_bot/.env'
                            bat 'powershell Copy-Item %CREDS% -Destination ./reminder_bot/credentials.json'
                            bat 'powershell Copy-Item %TOKEN% -Destination ./reminder_bot/token.json'
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
                        sh 'cd reminder_bot && docker-compose up -d --build'
                    } else {
                        bat 'cd reminder_bot && docker-compose up -d --build'
                    }
                }
                echo '===============docker container is running successfully==================='
            }
        }
    }