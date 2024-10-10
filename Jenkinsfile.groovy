pipeline {
       agent any

       stages {
           stage('Clone Repository') {
               echo 'downloading git repo'
               steps {
                   git url: 'https://github.com/MaxGoryunov/tg-reminber-bot.git', branch: 'main'
               }
               echo 'downloaded repo'
           }
           stage('Build and Run Application') {
               steps {
                   script {
                       docker.image('your-docker-image').run('-d -p 8080:8080') // Assuming your Docker image can be run with this command
                   }
               }
           }
       }
   }