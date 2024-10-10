pipeline {
       agent any
    //    {
    //        docker { image 'docker:latest' } 
    //    }
       stages {
           stage('Clone Repository') {
               steps {
                   git url: 'https://github.com/MaxGoryunov/tg-reminber-bot.git', branch: 'main'
               }
           }
           stage('Build and Run Docker Container') {
               steps {
                   script {
                       bat 'ls'
                       bat 'docker build -t rpi-app .'
                       bat 'docker run --network="host" -d --name rpi-run-app rpi-app'
                   }
               }
           }
       }
   }