pipeline {
       agent {
           docker { image 'docker:latest' } 
       }
       stages {
           stage('Clone Repository') {
               steps {
                   git url: 'https://github.com/MaxGoryunov/tg-reminber-bot.git', branch: 'main'
               }
           }
           stage('Build and Run Docker Container') {
               steps {
                   script {
                       docker.image('docker:latest').inside {
                        sh 'docker build -t rpi-app .' // Now the 'docker' command should be available
                        }
                       sh 'docker run --network="host" -d --name rpi-run-app rpi-app'
                   }
               }
           }
       }
   }