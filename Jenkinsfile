pipeline {
    agent {
        docker {
            reuseNode false
            image 'caufieldjh/kg-idg:4'
        }
    }
    triggers{
        cron('H H 1 1-12 *')
    }
    environment {
        BUILDSTARTDATE = sh(script: "echo `date +%Y%m%d`", returnStdout: true).trim()
        S3PROJECTDIR = 'kg-idg' // no trailing slash

        // Distribution ID for the AWS CloudFront for this bucket
        // used solely for invalidations
        AWS_CLOUDFRONT_DISTRIBUTION_ID = 'EUVSWXZQBXCFP'

        MERGEDKGNAME_BASE = "KG-IDG"
        MERGEDKGNAME_GENERIC = "merged-kg"
    }
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    stages {
        // Very first: pause for a minute to give a chance to
        // cancel and clean the workspace before use.
        stage('Ready and clean') {
            steps {
                // Give us a minute to cancel if we want.
                sleep time: 30, unit: 'SECONDS'
            }
        }

        stage('Initialize') {
            steps {
                // print some info
                dir('./gitrepo') {
                    sh 'env > env.txt'
                    sh 'echo $BRANCH_NAME > branch.txt'
                    sh 'echo "$BRANCH_NAME"'
                    sh 'cat env.txt'
                    sh 'cat branch.txt'
                    sh "echo $BUILDSTARTDATE > dow.txt"
                    sh "echo $BUILDSTARTDATE"
                    sh "echo $MERGEDKGNAME_BASE"
                    sh "echo $MERGEDKGNAME_GENERIC"
                    sh "python3.9 --version"
                    sh "id"
                    sh "whoami" // this should be jenkinsuser
                    // if the above fails, then the docker host didn't start the docker
                    // container as a user that this image knows about. This will
                    // likely cause lots of problems (like trying to write to $HOME
                    // directory that doesn't exist, etc), so we should fail here and
                    // have the user fix this

                }
            }
        }

        stage('Build kg_idg') {
            steps {
                dir('./gitrepo') {
                    git(
                            url: 'https://github.com/Knowledge-Graph-Hub/kg-idg',
                            branch: env.BRANCH_NAME
                    )
                    sh '/usr/bin/python3.9 -m venv venv'
                    sh '. venv/bin/activate'
                    // Start up the database platforms
                    // Starting may fail if resources aren't adequately available
                    // So just in case, we try to run the command a few times
                    sh 'for i in {1..5}; do sudo /etc/init.d/postgresql start && break || sleep 60; done'
                    sh 'for i in {1..5}; do sudo /etc/init.d/mysql start && break || sleep 60; done'
                    sh 'sudo /etc/init.d/postgresql status'
                    echo 'PostgreSQL server status:'
                    sh 'pg_isready -h localhost -p 5432'
                    sh 'sudo /etc/init.d/mysql status'
                    // Now move on to the actual install + reqs
                    sh './venv/bin/pip install .'
                    sh './venv/bin/pip install awscli boto3 s3cmd'

                    // Temporary - install ensmallen on its own
                    //sh './venv/bin/pip install ensmallen'
                }
            }
        }

        stage('Download') {
            steps {
                dir('./gitrepo') {
                    script {
                        
                        // Verify that the project directory is defined, or it will make a mess
                        // when it uploads everything to the wrong directory
                        if (S3PROJECTDIR.replaceAll("\\s","") == '') {
                            error("Project name contains only whitespace. Will not continue.")
                        }

                        def run_py_dl = sh(
                            script: '. venv/bin/activate && python3.9 run.py download', returnStatus: true
                        )
                        if (run_py_dl == 0) {
                            if (env.BRANCH_NAME != 'master') { // upload raw to s3 if we're on correct branch
                                echo "Will not push if not on correct branch."
                            } else {
                                withCredentials([file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG')]) {
                                    sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG --acl-public --mime-type=plain/text --cf-invalidate put -r data/raw s3://kg-hub-public-data/$S3PROJECTDIR/'
                                }
                            }
                        }  else { // 'run.py download' failed - let's try to download last good copy of raw/ from s3 to data/
                            currentBuild.result = "UNSTABLE"
                            withCredentials([file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG')]) {
                                sh 'rm -fr data/raw || true;'
                                sh 'mkdir -p data/raw || true'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG --acl-public --mime-type=plain/text get -r s3://kg-hub-public-data/$S3PROJECTDIR/raw/ data/raw/'
                            }
                        }
                    }
                }
            }
        }

        stage('Transform') {
            steps {
                dir('./gitrepo') {
		            sh '. venv/bin/activate && env && python3.9 run.py transform'
                }
            }
        }

        stage('Merge') {
            steps {
                dir('./gitrepo') {
                    sh '. venv/bin/activate && python3.9 run.py merge -y merge.yaml'
                    sh 'cp merged_graph_stats.yaml merged_graph_stats_$BUILDSTARTDATE.yaml'
		    sh 'mv merged_graph_stats_$BUILDSTARTDATE.yaml data/merged/'
                    sh 'cd data/merged/ && tar -czvf merged-kg.tar.gz merged-kg_nodes.tsv merged-kg_edges.tsv merged_graph_stats_$BUILDSTARTDATE.yaml'
                    sh 'cd ../..'
                }
            }
        }

        //stage('Make blazegraph journal'){
        //    steps {
        //        dir('./gitrepo/blazegraph') {
        //                git(
        //                        url: 'https://github.com/balhoff/blazegraph-runner.git',
        //                        branch: 'master'
        //                )
        //                sh 'HOME=`pwd` && sbt stage' // set HOME here to prevent sbt from trying to make dir .cache in /
        //                sh 'ls -lhd ../data/merged/${MERGEDKGNAME_BASE}.nt.gz'
        //                sh 'pigz -f -d ../data/merged/${MERGEDKGNAME_BASE}.nt.gz'
        //                sh 'export JAVA_OPTS=-Xmx128G && ./target/universal/stage/bin/blazegraph-runner load --informat=ntriples --journal=../data/merged/${MERGEDKGNAME_BASE}.jnl --use-ontology-graph=true ../data/merged/${MERGEDKGNAME_BASE}.nt'
        //                sh 'pigz -f ../data/merged/${MERGEDKGNAME_BASE}.jnl'
        //                sh 'pigz -f ../data/merged/${MERGEDKGNAME_BASE}.nt'
        //                sh 'ls -lhd ../data/merged/${MERGEDKGNAME_BASE}.jnl.gz'                       
        //        }
        //    }
        //}

        stage('Publish') {
            steps {
                dir('./gitrepo') {
                    script {

                        // make sure we aren't going to clobber existing data
                        withCredentials([file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG')]) {
                            REMOTE_BUILD_DIR_CONTENTS = sh (
                                script: '. venv/bin/activate && s3cmd -c $S3CMD_CFG ls s3://kg-hub-public-data/$S3PROJECTDIR/$BUILDSTARTDATE/',
                                returnStdout: true
                            ).trim()
                            echo "REMOTE_BUILD_DIR_CONTENTS (THIS SHOULD BE EMPTY): '${REMOTE_BUILD_DIR_CONTENTS}'"
                            if("${REMOTE_BUILD_DIR_CONTENTS}" != ''){
                                echo "Will not overwrite existing remote S3 directory: $S3PROJECTDIR/$BUILDSTARTDATE"
                                sh 'exit 1'
                            } else {
                                echo "remote directory $S3PROJECTDIR/$BUILDSTARTDATE is empty, proceeding"
                            }
                        }

                        if (env.BRANCH_NAME != 'master') {
                            echo "Will not push if not on correct branch."
                        } else {
                            withCredentials([
					            file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG'),
					            file(credentialsId: 'aws_kg_hub_push_json', variable: 'AWS_JSON'),
					            string(credentialsId: 'aws_kg_hub_access_key', variable: 'AWS_ACCESS_KEY_ID'),
					            string(credentialsId: 'aws_kg_hub_secret_key', variable: 'AWS_SECRET_ACCESS_KEY')]) {
                                           
                                //
                                // make $BUILDSTARTDATE/ directory and sync to s3 bucket
                                //
                                sh 'mkdir $BUILDSTARTDATE/'
                                //sh 'cp -p data/merged/${MERGEDKGNAME_BASE}.nt.gz $BUILDSTARTDATE/${MERGEDKGNAME_BASE}.nt.gz'
                                sh 'cp -p data/merged/merged-kg.tar.gz $BUILDSTARTDATE/${MERGEDKGNAME_BASE}.tar.gz'
                                //sh 'cp -p data/merged/${MERGEDKGNAME_BASE}.jnl.gz $BUILDSTARTDATE/${MERGEDKGNAME_BASE}.jnl.gz'
                                // transformed data
                                sh 'rm -fr data/transformed/.gitkeep'
                                sh 'cp -pr data/transformed $BUILDSTARTDATE/'
                                sh 'cp -pr data/raw $BUILDSTARTDATE/'
                                sh 'cp Jenkinsfile $BUILDSTARTDATE/'

                                // copy that NEAT config, too
                                // but update its buildname internally first
                                sh """ sed -i '/      - path:/ s/BUILDNAME/$BUILDSTARTDATE/' neat.yaml """
                                sh """ sed -i '/  s3_bucket_dir:/ s/kg-idg/$S3PROJECTDIR\\/$BUILDSTARTDATE\\/graph_ml/' neat.yaml """
                                sh 'cp neat.yaml $BUILDSTARTDATE/'

                                // stats dir
                                sh 'mkdir $BUILDSTARTDATE/stats/'
                                sh 'cp -p *_stats.yaml $BUILDSTARTDATE/stats/'
                                sh 'cp templates/README.build $BUILDSTARTDATE/README'

                                // build the index, then upload to remote
                                sh '. venv/bin/activate && multi_indexer -v --directory $BUILDSTARTDATE --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/$BUILDSTARTDATE -x -u'

                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $BUILDSTARTDATE s3://kg-hub-public-data/$S3PROJECTDIR/'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG rm -r s3://kg-hub-public-data/$S3PROJECTDIR/current/'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $BUILDSTARTDATE/* s3://kg-hub-public-data/$S3PROJECTDIR/current/'

                                // make index for project dir
                                sh '. venv/bin/activate && multi_indexer -v --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/ -b kg-hub-public-data -r $S3PROJECTDIR -x'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate ./index.html s3://kg-hub-public-data/$S3PROJECTDIR/'

                                // Invalidate the CDN now that the new files are up.
                                sh 'echo "[preview]" > ./awscli_config.txt && echo "cloudfront=true" >> ./awscli_config.txt'
                                sh '. venv/bin/activate && AWS_CONFIG_FILE=./awscli_config.txt python3.9 ./venv/bin/aws cloudfront create-invalidation --distribution-id $AWS_CLOUDFRONT_DISTRIBUTION_ID --paths "/*"'

                                // Should now appear at:
                                // https://kg-hub.berkeleybop.io/[artifact name]
                            }

                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'In always'
            echo 'Cleaning workspace...'
            cleanWs()
        }
        success {
            echo 'I succeeded!'
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }
}
