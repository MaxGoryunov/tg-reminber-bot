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
                   echo 'we are here'
               }
           }
       }
   }