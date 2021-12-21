pipeline {
    agent {
        docker {
            reuseNode false
            image 'justaddcoffee/ubuntu20-python-3-8-5-dev:8'  // TODO - update to with-dbs docker version of Harry's
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
        // Distribution ID for the AWS CloudFront for this bucket
        // used solely for invalidations
        GCLOUD_PROJECT = 'test-project-covid-19-277821'
        GCLOUD_VM='gpgpgpuwhereareyou'
        GCLOUD_ZONE='us-central1-a'
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
                    sh "python3.8 --version"
                    sh "id"
                    sh "cat /etc/hostname"
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
                    sh '/usr/bin/python3.8 -m venv venv'
                    sh '. venv/bin/activate'
                    // Start up the database platforms
                    sh 'sudo /etc/init.d/postgresql start'
                    sh 'sudo /etc/init.d/mysql start'
                    sh 'sudo /etc/init.d/postgresql status'
                    sh 'sudo /etc/init.d/mysql status'
                    echo 'PostgreSQL server status:'
                    sh 'pg_isready -h localhost -p 5432'
                    // Now move on to the actual install + reqs
                    sh './venv/bin/pip install .'
                    sh './venv/bin/pip install awscli boto3 s3cmd'
                    sh './venv/bin/pip install ensmallen==0.7.0.dev6' // magic version that doesn't require AVX and works on build.bbop.io
                    sh './venv/bin/pip install git+https://github.com/Knowledge-Graph-Hub/NEAT.git'
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
                            script: '. venv/bin/activate && python3.8 run.py download', returnStatus: true
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
                    sh '. venv/bin/activate && env && python3.8 run.py transform'
                }
            }
        }

        stage('Merge') {
            steps {
                dir('./gitrepo') {
                    sh '. venv/bin/activate && python3.8 run.py merge -y merge.yaml'
                    sh 'cp merged_graph_stats.yaml merged_graph_stats_$BUILDSTARTDATE.yaml'
                    sh 'tar -rvfz data/merged/merged-kg.tar.gz merged_graph_stats_$BUILDSTARTDATE.yaml'
                }
            }
        }

        stage('Make blazegraph journal'){
            steps {
                dir('./gitrepo/blazegraph') {
                        git(
                                url: 'https://github.com/balhoff/blazegraph-runner.git',
                                branch: 'master'
                        )
                        sh 'HOME=`pwd` && sbt stage' // set HOME here to prevent sbt from trying to make dir .cache in /
                        sh 'ls -lhd ../data/merged/${MERGEDKGNAME_BASE}.nt.gz'
                        sh 'pigz -f -d ../data/merged/${MERGEDKGNAME_BASE}.nt.gz'
                        sh 'export JAVA_OPTS=-Xmx128G && ./target/universal/stage/bin/blazegraph-runner load --informat=ntriples --journal=../data/merged/${MERGEDKGNAME_BASE}.jnl --use-ontology-graph=true ../data/merged/${MERGEDKGNAME_BASE}.nt'
                        sh 'pigz -f ../data/merged/${MERGEDKGNAME_BASE}.jnl'
                        sh 'pigz -f ../data/merged/${MERGEDKGNAME_BASE}.nt'
                        sh 'ls -lhd ../data/merged/${MERGEDKGNAME_BASE}.jnl.gz'
                }
            }
        }

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

                        // TODO: remove this add_neat_to_jenkins_run_jenkins stuff
                        if (env.BRANCH_NAME != 'master' && env.BRANCH_NAME != 'add_neat_to_jenkins_run_jenkins') {
                            echo "Will not push if not on correct branch."
                        } else {
                            withCredentials([
					            file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG'),
					            file(credentialsId: 'aws_kg_hub_push_json', variable: 'AWS_JSON'),
					            string(credentialsId: 'aws_kg_hub_access_key', variable: 'AWS_ACCESS_KEY_ID'),
					            string(credentialsId: 'aws_kg_hub_secret_key', variable: 'AWS_SECRET_ACCESS_KEY')]) {

                                // TODO: Make this whole chunk of indexing/uploading code its own script

                                //
                                // make $BUILDSTARTDATE/ directory and sync to s3 bucket
                                //
                                sh 'mkdir $BUILDSTARTDATE/'
                                sh 'cp -p data/merged/${MERGEDKGNAME_BASE}.nt.gz $BUILDSTARTDATE/${MERGEDKGNAME_BASE}.nt.gz'
                                sh 'cp -p data/merged/merged-kg.tar.gz $BUILDSTARTDATE/${MERGEDKGNAME_BASE}.tar.gz'
                                 sh 'cp -p data/merged/${MERGEDKGNAME_BASE}.jnl.gz $BUILDSTARTDATE/${MERGEDKGNAME_BASE}.jnl.gz'
                                // transformed data
                                sh 'rm -fr data/transformed/.gitkeep'
                                sh 'cp -pr data/transformed $BUILDSTARTDATE/'
                                sh 'cp -pr data/raw $BUILDSTARTDATE/'
                                sh 'cp Jenkinsfile $BUILDSTARTDATE/'
                                // stats dir
                                sh 'mkdir $BUILDSTARTDATE/stats/'
                                sh 'cp -p *_stats.yaml $BUILDSTARTDATE/stats/'
                                sh 'cp templates/README.build $BUILDSTARTDATE/README'

                                sh '. venv/bin/activate && python3.8 ./multi_indexer.py -v --inject ./directory-index-template.html --directory $BUILDSTARTDATE --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/$BUILDSTARTDATE -x -u'

                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $BUILDSTARTDATE s3://kg-hub-public-data/$S3PROJECTDIR/'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG rm -r s3://kg-hub-public-data/$S3PROJECTDIR/current/'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $BUILDSTARTDATE/* s3://kg-hub-public-data/$S3PROJECTDIR/current/'

                                // make index for project dir
                                sh '. venv/bin/activate && python3.8 ./multi_indexer.py -v --inject ./directory-index-template.html --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/ -b kg-hub-public-data -r $S3PROJECTDIR -x'
                                sh '. venv/bin/activate && s3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate ./index.html s3://kg-hub-public-data/$S3PROJECTDIR/'

                                // Invalidate the CDN now that the new files are up.
                                sh 'echo "[preview]" > ./awscli_config.txt && echo "cloudfront=true" >> ./awscli_config.txt'
                                sh '. venv/bin/activate && AWS_CONFIG_FILE=./awscli_config.txt python3.8 ./venv/bin/aws cloudfront create-invalidation --distribution-id $AWS_CLOUDFRONT_DISTRIBUTION_ID --paths "/*"'

                                // Should now appear at:
                                // https://kg-hub.berkeleybop.io/[artifact name]
                            }

                        }
                    }
                }
            }
        }

        stage('Spin up Gcloud instance') {
            when { anyOf { branch 'main'; branch 'add_neat_to_jenkins_run_jenkins'  } }
            steps {
                dir('./gcloud') {
                    withCredentials([file(credentialsId: 'GCLOUD_CRED_JSON', variable: 'GCLOUD_CRED_JSON')]) {
                        echo 'Trying to start up instance...'
                            // keep trying to start the instance until success
                            //
                            sh '''#!/bin/bash
                                  gcloud auth activate-service-account --key-file=$GCLOUD_CRED_JSON --project $GCLOUD_PROJECT
                                  STATUS=$(gcloud compute instances describe $GCLOUD_VM --zone=$GCLOUD_ZONE --format="yaml(status)")
                                  n=0
                                  until [ "$n" -ge 100 ]
                                  do
                                       echo "instance $GCLOUD_VM $STATUS; trying to start instance..."
                                       gcloud compute instances start $GCLOUD_VM --zone=$GCLOUD_ZONE
                                       STATUS=$(gcloud compute instances describe $GCLOUD_VM --zone=$GCLOUD_ZONE --format="yaml(status)")
                                       [ "$STATUS" != "status: TERMINATED" ] && break
                                       n=$((n+1))
                                       echo "no dice - sleeping for 30 s"
                                       sleep 30
                                  done
                                  if [ "$STATUS" == "status: TERMINATED" ]
                                  then
                                        echo ERROR: Failed to start instance
                                        exit 1
                                  else
                                        echo started instance
                                  fi
                                  gcloud compute instances describe $GCLOUD_VM --zone=$GCLOUD_ZONE --format="yaml(status)"
                            '''
                    }
                }

            }
        }

        stage('Run graph ML tasks in NEAT YAML') {
            // TODO: remove branch add_neat_to_jenkins_run_jenkins
            when { anyOf { branch 'main'; branch 'add_neat_to_jenkins_run_jenkins'  } }
            steps {
                dir('./run_embedding') {
                    script{
                        sh 'env'
                        // copy template NEAT yaml
                        OUTPUT_DIR = "${BUILDSTARTDATE}/graph_ml/" // leave trailing '/'
                        NEAT_YAML = "kg-idg-neat.${BUILDSTARTDATE}.yaml"
                        NEAT_YAML_FULL_PATH = "/tmp/${NEAT_YAML}"
                        NEAT_YAML_FULL_REMOTE_PATH = "/home/jtr4v/NEAT/${OUTPUT_DIR}${NEAT_YAML}"

                        sh "cp -f ../gitrepo/templates/kg-idg-neat.yaml $NEAT_YAML_FULL_PATH"
                        // run neat updateyaml
                        sh ". ../gitrepo/venv/bin/activate && neat updateyaml --input_path $NEAT_YAML_FULL_PATH --keys name,description,output_directory,graph_data:graph:node_path,graph_data:graph:edge_path,upload:s3_bucket_dir --values kg-idg-$BUILDSTARTDATE,kg-idg-$BUILDSTARTDATE,$OUTPUT_DIR,$BUILDSTARTDATE/merged-kg_nodes.tsv,$BUILDSTARTDATE/merged-kg_edges.tsv,kg-idg/${OUTPUT_DIR}"
                        // make remote output dir
                        def EXIT_CODE_MKDIR=sh script:"gcloud compute ssh $GCLOUD_VM --zone $GCLOUD_ZONE --ssh-flag=\"-tt\" --command=\"sudo runuser -l jtr4v -c \'mkdir -p /home/jtr4v/NEAT/$OUTPUT_DIR\'\"", returnStatus:true
                        // scp NEAT yaml to gcloud instance
                        sh "gcloud compute scp --zone $GCLOUD_ZONE $NEAT_YAML_FULL_PATH jtr4v@$GCLOUD_VM:${NEAT_YAML_FULL_REMOTE_PATH}"
                        def EXIT_CODE_WGET=sh script:"gcloud compute ssh $GCLOUD_VM --zone $GCLOUD_ZONE --ssh-flag=\"-tt\" --command=\"sudo runuser -l jtr4v -c \'cd NEAT && mkdir -p ${BUILDSTARTDATE} && cd $BUILDSTARTDATE && wget https://kg-hub.berkeleybop.io/kg-idg/${BUILDSTARTDATE}/KG-IDG.tar.gz && tar -xzvf KG-IDG.tar.gz &> /home/jtr4v/neat_output.txt\'\"", returnStatus:true
                        def EXIT_CODE=sh script:"gcloud compute ssh $GCLOUD_VM --zone $GCLOUD_ZONE --ssh-flag=\"-tt\" --command=\"sudo runuser -l jtr4v -c \'export PATH=~/anaconda3/bin:$PATH conda activate && cd NEAT && LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 neat run --config ${NEAT_YAML_FULL_REMOTE_PATH} 2>&1 | tee -a /home/jtr4v/neat_output.txt\'\"", returnStatus:true

                        if(EXIT_CODE_MKDIR != 0 || EXIT_CODE_WGET != 0 || EXIT_CODE != 0){
                           currentBuild.result = 'FAILED'
                           return
                        }
                    }
                }
            }
        }


    }

    post {
        always {
            echo 'In always'
            echo 'Shut down gcloud instance'
            dir('./gcloud') {
                withCredentials([file(credentialsId: 'GCLOUD_CRED_JSON', variable: 'GCLOUD_CRED_JSON')]) {
                    echo 'Trying to stop instance...'
                        // keep trying to stop the instance until success
                        sh '''#!/bin/bash
                              gcloud auth activate-service-account --key-file=$GCLOUD_CRED_JSON --project $GCLOUD_PROJECT
                              STATUS=$(gcloud compute instances describe $GCLOUD_VM --zone=$GCLOUD_ZONE --format="yaml(status)")
                              while true
                              do
                                   echo "instance $GCLOUD_VM $STATUS; trying to stop instance..."
                                   gcloud compute instances stop $GCLOUD_VM --zone=$GCLOUD_ZONE
                                   STATUS=$(gcloud compute instances describe $GCLOUD_VM --zone=$GCLOUD_ZONE --format="yaml(status)")
                                   [ "$STATUS" == "status: TERMINATED" ] && break
                                   echo "no dice - sleeping for 10 s"
                                   sleep 10
                              done
                              gcloud compute instances describe $GCLOUD_VM --zone=$GCLOUD_ZONE --format="yaml(status)"
                        '''
                }
            }

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
