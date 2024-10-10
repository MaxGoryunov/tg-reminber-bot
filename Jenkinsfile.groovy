pipeline {
       agent any

       stages {
           stage('Clone Repository') {
               steps {
                   git url: 'https://github.com/your-username/your-repo.git', branch: 'main'
               }
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