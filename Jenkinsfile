pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // ...existing build steps...
                sh 'python setup.py install' // Install the package
            }
        }
        stage('Test') {
            steps {
                // ...existing test steps...
                // Generate the HTML report using the custom script
                sh './scripts/generate-jmeter-report.sh'
            }
        }
        stage('Archive and Publish Report') {
            steps {
                // Archive the HTML report
                archiveArtifacts artifacts: 'reports/results_2_report.html', allowEmptyArchive: true
                
                // Publish the HTML report
                publishHTML(target: [
                    reportName: 'JMeter Test Report',
                    reportDir: 'reports',
                    reportFiles: 'results_2_report.html',
                    alwaysLinkToLastBuild: true,
                    keepAll: true
                ])
            }
        }
    }
    post {
        always {
            // ...existing post steps...
        }
    }
}
