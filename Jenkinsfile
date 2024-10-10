pipeline {
       agent any

       stages {
           stage('Clone Repository') {
               steps {
                   git url: 'https://github.com/MaxGoryunov/tg-reminber-bot.git', branch: 'main'
               }
           }
           stage('Build and Run Application') {
               steps {
                   echo 'we are here'
               }
           }
       }
   }