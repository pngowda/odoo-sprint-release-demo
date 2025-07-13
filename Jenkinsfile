// Multibrnach Jenkins Pipeline for Odoo module CI/CD
// This pipeline performs linting, formatting, static security scanning, test coverage, building, and multi-environment deployment for Odoo custom modules.

pipeline {
    agent {
        docker {
            image 'oddo-build-container:1.0.0' // Use custom Docker image with all build dependencies
        }
    }

    environment {
        MODULES = "t29_custom_1 t29_custom_2 t29_custom_3" // List of Odoo custom modules to process
        // Target hostname for connecting to Odoo servers in different environments
        ODOO_HOST_DEV = credentials('odoo-dev-host')
        ODOO_HOST_STAGING = credentials('odoo-staging-host')
        ODOO_HOST_PROD = credentials('odoo-prod-host')
        // Git credentials for automated pushes if needed
        GIT_CREDENTIALS_ID = 'faceless-account-git-credentials-id'
    }

    options {
        disableConcurrentBuilds() // Prevent concurrent builds on the same job
        timestamps() // Add timestamps to console output
        timeout(time: 60, unit: 'MINUTES') // Set max build duration to 60 minutes
    }

    stages {
        stage('Checkout') {
            steps { 
                checkout scm 
            }
        }

        stage('Python Lint, Format & Security') {
            steps {
                // Lint, format, and run static security analysis for Python source code
                sh '''
                    flake8 ${MODULES// /,} | tee flake8-report.txt || true // Python linting, output report
                    black --check ${MODULES// /,} | tee black-report.txt || true // Check Python formatting, output report
                    black ${MODULES// /,} > black-formatting.txt 2>&1 || true // Apply auto-formatting, track changes
                    bandit -r ${MODULES// /,} | tee bandit-report.txt || true // Python security scan, output report
                '''
                archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true // Archive lint/format/security reports
            }
        }

        stage('Shell Lint & Format') {
            steps {
                // Lint and format all shell scripts in the module directories
                sh '''
                    find ${MODULES// /,} -name "*.sh" -exec shellcheck {} + | tee shellcheck-report.txt || true // Shell linting
                    find ${MODULES// /,} -name "*.sh" -exec shfmt -d -i 4 -ci {} + | tee shfmt-report.txt || true // Shell formatting check (diff mode)
                    find ${MODULES// /,} -name "*.sh" -exec shfmt -w -i 4 -ci {} + // Apply shell formatting
                '''
                archiveArtifacts artifacts: '*.txt', allowEmptyArchive: true // Archive shell lint/format reports
            }
        }

        stage('Trivy Scan') {
            steps {
                // Trivy scans the project directory for security vulnerabilities in OS packages,
                // application dependencies, configuration files, and secrets.
                // --exit-code 0: always succeed (does not fail the build on findings, reports are archived)
                // --no-progress: disables progress bar for cleaner CI logs
                sh '''
                    trivy fs --exit-code 0 --no-progress . | tee trivy-report.txt
                '''
                archiveArtifacts artifacts: 'trivy-report.txt', allowEmptyArchive: true // Archive Trivy security report
            }
        }

        stage('Auto Commit Formatting Changes') {
            steps {
                // Automatically commit and push any code changes resulting from lint/format steps
                sh '''
                    git config user.name "jenkins-bot"
                    git config user.email "jenkins@example.com"
                    git add .
                    git diff --cached --quiet || git commit -m "Auto-format Python and Shell scripts [skip ci]"
                    // Push committed formatting changes back to remote (use CI credentials)
                    git push https://${GIT_CREDENTIALS_ID}@$(git remote get-url origin | sed -e "s#https://##")
                '''
            }
        }

        stage('Test & Coverage') {
            steps {
                // Run Odoo module tests with coverage tracking enabled
                sh '''
                    coverage run --source=${MODULES// /,} ./odoo-bin --addons-path=addons,custom_addons --test-enable -i ${MODULES}
                    coverage report // Print coverage summary
                    coverage html // Generate HTML coverage report
                '''
                archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true // Archive HTML coverage reports
            }
        }

        stage('Build') {
            steps {
                script {
                    def gitHash = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    // Build a unique artifact name for traceability
                    env.ARTIFACT_NAME = "release_${env.BRANCH_NAME}_${env.BUILD_NUMBER}_${gitHash}.tar.gz"
                    // Create the tarball package
                    sh "tar czf ${env.ARTIFACT_NAME} ${MODULES}"
                    archiveArtifacts artifacts: "${env.ARTIFACT_NAME}", fingerprint: true
                }
            }
        }

        stage('Upload to Artifactory') {
            steps {
                script {
                    def server = Artifactory.server('my-artifactory-server-id')

                    // Create Artifactory upload spec for your artifact
                    def uploadSpec = """{
                        "files": [
                            {
                                "pattern": "${env.ARTIFACT_NAME}",
                                "target": "odoo-releases/${env.BRANCH_NAME}/",
                                "props": "build.number=${env.BUILD_NUMBER};git.commit=${gitHash};branch.name=${env.BRANCH_NAME};build.url=${env.BUILD_URL}"
                            }
                        ]
                    }"""

                    // Upload artifact and capture build info
                    def buildInfo = server.upload(uploadSpec)

                    // Publish build info to Artifactory for traceability
                    server.publishBuildInfo(buildInfo)
                }
            }
        }

        stage('Deploy to Dev') {
            when { branch 'development' } // Only run this stage on 'development' branch
            steps {
                script {
                    // Dev deployment steps: upload, backup, extract, restart Odoo
                    def target_host = env.ODOO_HOST_DEV
                    sh "scp release.tar.gz ${target_host}:/tmp/"
                    sh "ssh ${target_host} 'cp -r /odoo/custom_addons /odoo/custom_addons_backup_$(date +%F_%T)'" // Backup current addons
                    sh "ssh ${target_host} 'tar xzf /tmp/release.tar.gz -C /odoo/custom_addons/'" // Extract new addons
                    sh "ssh ${target_host} 'sudo systemctl restart odoo'" // Restart Odoo server
                }
            }
        }

        stage('Integration Tests on Dev') {
            when { branch 'development' } // Only run this stage on 'development' branch
            steps {
                // Place holder to run automated Integration and Regression tests.
                // Invoke your Integration test suite here
            }
            archiveArtifacts artifacts: '**/integration-test-report/**', allowEmptyArchive: true
        }

        stage('Deploy to Staging') {
            when { branch 'staging' } // Only run this stage on 'staging' branch
            steps {
                script {
                    // Staging deployment steps: upload, backup, extract, restart Odoo
                    def target_host = env.ODOO_HOST_STAGING
                    sh "scp release.tar.gz ${target_host}:/tmp/"
                    sh "ssh ${target_host} 'cp -r /odoo/custom_addons /odoo/custom_addons_backup_$(date +%F_%T)'"
                    sh "ssh ${target_host} 'tar xzf /tmp/release.tar.gz -C /odoo/custom_addons/'"
                    sh "ssh ${target_host} 'sudo systemctl restart odoo'"
                }
            }
        }

        stage('UAT-Load-Performace Tests') {
            when { branch 'staging' } // Only run this stage on 'staging' branch
            steps {
                script {
                    // Place holder to run automated UAT tests, Load and Performace tests
                    // Invoke your UAT test suite here
                    // Invoke your Load/Performace test suite here
                }
                archiveArtifacts artifacts: '**/uat-test-report/**', allowEmptyArchive: true
                archiveArtifacts artifacts: '**/load-test-report/**', allowEmptyArchive: true
            }
        }

        stage('Approval for Production Deployment') {
            when { branch 'main' } // Only run approval on 'main' branch (production)
            steps {
                script {
                    // Reads product owners (deployment approvers) from a YAML config file
                    def productOwners = readYaml file: 'devops/config/release_managers.yaml'
                    def ownerEmails = []
                    def ownerUserIds = []
                    productOwners['eligible_owners'].each {
                        ownerEmails.add(it.email)
                        ownerUserIds.add(it.user_id)
                    }

                    // Send approval notification email to product owners with a link to Jenkins input step
                    emailext mimeType: 'text/html',
                    subject: "[Odoo Deployment Approval] Production Release ${env.BUILD_NUMBER}",
                    to: ownerEmails.join(', '),
                    body: """
                        <html>
                        <p>Dear Product Owners,<br><br>
                            A production deployment for Odoo is pending approval.<br>
                            Please <b>review and approve or reject</b> by clicking
                            <a href="${env.BUILD_URL}input">this link</a>.<br><br>
                            Build: <b>${env.JOB_NAME} #${env.BUILD_NUMBER}</b><br>
                            Initiated by: ${env.BUILD_USER_ID}<br>
                            <br>
                            Best regards,<br>
                            DevOps Team
                        </p>
                        </html>
                    """

                    // Jenkins UI prompt for approval, restricted to product owners listed in the YAML config
                    def approval = input(
                        id: 'prodApproval',
                        message: 'Production deployment requires product owner approval. Proceed?',
                        submitterParameter: 'submitter',
                        submitter: ownerUserIds.join(','),
                        parameters: [
                            choice(name: 'approval', choices: ['Yes', 'No'], description: 'Choose "Yes" to approve production deployment')
                        ]
                    )
                    echo "Production deployment approved by: " + approval['submitter']
                    if (!((approval instanceof Map && approval['approval'] == 'Yes') || (approval instanceof String && approval == 'Yes'))) {
                        error("Production deployment was NOT approved.") // Abort if not approved
                    }
                }
            }
        }

        stage('Deploy to Production') {
            when { branch 'main' } // Only deploy to production on 'main' branch
            steps {
                script {
                    // Production deployment steps: upload, backup, extract, restart Odoo
                    def target_host = env.ODOO_HOST_PROD
                    sh "scp release.tar.gz ${target_host}:/tmp/"
                    sh "ssh ${target_host} 'cp -r /odoo/custom_addons /odoo/custom_addons_backup_$(date +%F_%T)'"
                    sh "ssh ${target_host} 'tar xzf /tmp/release.tar.gz -C /odoo/custom_addons/'"
                    sh "ssh ${target_host} 'sudo systemctl restart odoo'"
                }
            }
        }

        stage('Post-Deployment Health Check') {
            when {
                // Run health check after deployments to any environment
                // Could also be tracked via some Observability tool
                anyOf {
                    branch 'development'
                    branch 'staging'
                    branch 'main'
                }
            }
            steps {
                script {
                    // Determine target host and perform application health check via HTTP endpoint
                    def target_host = (env.BRANCH_NAME == 'main') ? env.ODOO_HOST_PROD :
                                      (env.BRANCH_NAME == 'staging') ? env.ODOO_HOST_STAGING :
                                      env.ODOO_HOST_DEV
                    sh "ssh ${target_host} 'curl -f http://localhost:8069/healthcheck || exit 1'"
                }
            }
        }

        stage('Notify') {
            when {
                // Notify after deployments to any environment
                anyOf {
                    branch 'development'
                    branch 'staging'
                    branch 'main'
                }
            }
            steps {
                script {
                    // Set environment name for notifications
                    def envName = (env.BRANCH_NAME == 'main') ? 'PROD' :
                                  (env.BRANCH_NAME == 'staging') ? 'STAGING' : 'DEV'
                    currentBuild.result = currentBuild.result ?: 'SUCCESS'
                    def emoji = (currentBuild.result == 'SUCCESS') ? ':rocket:' : ':x:'
                    def message = "Odoo deployment to ${envName} " + (currentBuild.result == 'SUCCESS' ? "successful" : "FAILED") + " ${emoji}"
                    // Send Slack notification to stake holders(could also be a teams channel notification)
                    sh """
                    curl -X POST -H 'Content-type: application/json' --data '{"text":"${message}"}' $SLACK_WEBHOOK
                    """
                    // Send email notification to dev team
                    mail to: 'dev-team@example.com',
                        subject: "[${envName}][${currentBuild.result}] Odoo Pipeline",
                        body: "Odoo deployment to ${envName} ${currentBuild.result.toLowerCase() == 'success' ? 'succeeded' : 'failed'}. ${currentBuild.result == 'SUCCESS' ? '' : 'Please check Jenkins logs.'}"
                }
            }
        }
    }

    post {
        failure {
            script {
                // On failure, restore custom_addons from the latest backup and restart Odoo
                def target_host = (env.BRANCH_NAME == 'main') ? env.ODOO_HOST_PROD :
                                  (env.BRANCH_NAME == 'staging') ? env.ODOO_HOST_STAGING :
                                  env.ODOO_HOST_DEV
                sh "ssh ${target_host} 'if ls /odoo/custom_addons_backup_* 1> /dev/null 2>&1; then cp -r \$(ls -td /odoo/custom_addons_backup_* | head -1)/* /odoo/custom_addons/; sudo systemctl restart odoo; fi'"
            }
        }
    }
}