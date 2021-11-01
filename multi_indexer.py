# multi_indexer.py
"""
Index the contexts of a directory, creating an Apache HTTPd index-like page dictated by the mustache template provided.
If provided with a remote location on an AWS S3 bucket, will create an index of remote directories/files.
(Does not upload any index files.)
Local indexing is *recursive* - it will index subfolders relative to the provided path.
Remote indexing is *not recursive* - it will create a single index for the provided path only.

Adapted from directory_indexer.py Eric Douglass, Seth Carbon, and Justin Reese, originally at
https://github.com/Knowledge-Graph-Hub/go-site/blob/master/scripts/multi_indexer.py

 Example usage for local indexing (local testing):
  python3 multi_indexer.py --help
  mkdir -p /tmp/foo/bar/bib/bab && mkdir -p /tmp/foo/bar/fish && mkdir -p /tmp/foo/bar/foul && touch /tmp/foo/top.md && touch /tmp/foo/bar/bib/bab/bottom.txt && touch /tmp/foo/bar/fish/trout.f && touch /tmp/foo/bar/fish/bass.f
  python3 multi_indexer.py -v --inject ./directory-index-template.html --directory /tmp/foo --prefix file:///tmp/foo -x
 python3 multi_indexer.py -v --inject ./directory-index-template.html --directory /tmp/foo --prefix file:///tmp/foo -x -u

 Example usage for local indexing (production):
  python3 multi_indexer.py -v --inject ./directory-index-template.html --directory $WORKSPACE/mnt --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/ -x'

 Example usage for remote indexing:
  python3 multi_indexer.py -v --inject ./directory-index-template.html --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/ -b kg-hub-public-data -r $S3PROJECTDIR -x'

"""

import sys
import argparse
import logging
import os
import urllib.parse
import json
import pystache
import boto3

## Logger basic setup.
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('aggregate')
LOG.setLevel(logging.WARNING)

IFILENAME = "index.html"

def die_screaming(instr):
    """Make sure we exit in a way that will get Jenkins's attention."""
    LOG.error(instr)
    sys.exit(1)

def main():
    """The main runner for our script."""

    ## Ignore list.
    ignore_list = [IFILENAME,"raw"]
    LOG.info('Will ignore: "' + '", "'.join(ignore_list) + '"')

    # Args
    # TODO: use Click instead
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i', '--inject', required=True,
                        help='Mustache template file to inject into')
    parser.add_argument('-d', '--directory',
                        help='The directory to copy from')
    parser.add_argument('-p', '--prefix', required=True,
                        help='The prefix to add to all files and links')
    parser.add_argument('-x', '--execute', action='store_true',
                        help='Actually run--not the default dry run')
    parser.add_argument('-u', '--up', action='store_true',
                        help='Release version, where pages have a link pointing up one level')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='More verbose output')
    parser.add_argument('-b', '--bucket',
                        help='Name of S3 bucket, if creating index for remote directory')
    parser.add_argument('-r', '--remote_directory',
                        help='Name of S3 remote directory (without leading / ), if creating index for it')                    
    args = parser.parse_args()

    if args.verbose:
        LOG.setLevel(logging.INFO)
        LOG.info('Verbose: on')

    if args.execute:
        LOG.info('Will actually write to filesystem.')
    else:
        LOG.info('Will do a dry run.')

    ## Get template in hand.
    LOG.info('Will inject into: ' + args.inject)
    output_template = None
    with open(args.inject) as fhandle:
        output_template = fhandle.read()

    if not args.prefix.endswith("/"):
        prefix = "{}/".format(args.prefix)
    else:
        prefix = args.prefix

    LOG.info(f'Will use prefix: {prefix}')

    #If an S3 bucket name isn't provided, we're just indexing locally.
    if not args.bucket:
        rootdir = os.path.normpath(args.directory)
        LOG.info(f'Will operate in: {rootdir}')

        # Walk tree.
        # First, make a clean path to use in making new pathnames.
        # webrootdir = rootdir.lstrip('.').lstrip('//').rstrip('//')
        for currdir, dirs, files in os.walk(rootdir):

            ## Create index on every "root".
            parent = None
            children = []
            current = []

            ## We can navigate up if we are not in the root.
            # print('one_up: ' + one_up)
            if rootdir != currdir or args.up:
                parent = parent_url(rootdir, currdir, prefix)

            ## Note files and directories.
            for fname in files:
                #print('fname: ' + fname)
                ## Naturally, skip index.html, and other hidden files.
                if fname not in ignore_list:
                    current.append(map_file_to_url(rootdir, currdir, fname, prefix))

            for dname in dirs:
                #print('dname: ' + dname)
                children.append(map_dir_to_url(rootdir, currdir, dname, prefix))

            ## Assemble for use.
            dir_index = {
                'parent': parent,
                'children': sorted(children, key=lambda x: x['name']),
                'location': map_current_dir_to_url(rootdir, currdir, prefix),
                'current': sorted(current, key=lambda x: x['name']),
            }

            ## Test output.
            jsondump = json.dumps(dir_index, sort_keys=True, indent=4)
            LOG.info(jsondump)

            ## Output to filesystem.
            output = pystache.render(output_template, dir_index)

            ## Final writeout.
            outf = os.path.join(currdir, IFILENAME)
            if args.execute:
                with open(outf, 'w') as fhandle:
                    fhandle.write(output)

            LOG.info(f'Wrote: {outf}')
            
    elif args.bucket: # Provided a bucket, so let's index the remote dir

        children = []
        current = []

        bucket = args.bucket
        if not args.remote_directory:
            die_screaming("Not provided path of remote directory to create index for.")
        else:
            remote_path = args.remote_directory

        LOG.info(f'Will create index for S3 bucket with name: {bucket}')
        LOG.info(f'And this directory on the bucket: {remote_path}')

        remote_files = get_remote_file_list(bucket, remote_path, ignore_list)

        ## Note files and directories.
        for filename in remote_files[1]:
            mapped = {
                        "name": filename,
                        "url": urllib.parse.urljoin(prefix, filename)
                        }
            current.append(mapped)

        for dirname in remote_files[0]:
            mapped = {
                        "name": dirname,
                        "url": urllib.parse.urljoin(prefix, dirname)
                        }
            children.append(mapped)

        ## Assemble for use.
        dir_index = {
                'parent': prefix.rsplit('/', 2)[0], #Just want the main directory
                'children': sorted(children, key=lambda x: x['name']),
                'location': remote_path,
                'current': sorted(current, key=lambda x: x['name'])
                }

            ## Test output.
        jsondump = json.dumps(dir_index, sort_keys=True, indent=4)
        LOG.info(jsondump)

        ## Output to filesystem.
        output = pystache.render(output_template, dir_index)

        ## Final writeout.
        outf = IFILENAME
        if args.execute:
            with open(outf, 'w') as fhandle:
                fhandle.write(output)

        LOG.info(f'Wrote: {outf}')
    
def get_remote_file_list(bucket: str, remote_path: str, ignore_list: list) -> tuple:
    """
    Checks a specified remote path on an S3 bucket, 
    then return a list of all keys contained within that location,
    with the intent of using them to build an index.
    Files/directories in subdirectories are ignored.
    :param bucket: str of S3 bucket
    :param remote_path: str of path to get keys from
    :param ignore_list: list of filenames to ignore
    :return: tuple of list of directories, list of file key values
    """
    client = boto3.client('s3')
    pager = client.get_paginator("list_objects_v2")

    # Get list of remote files
    remote_keys = [] # All file keys
    try:
        for page in pager.paginate(Bucket=bucket, Prefix=remote_path+"/"):
            remote_contents = page['Contents']
            for key in remote_contents:
                if os.path.basename(key['Key']) not in ignore_list and \
                    os.path.basename(os.path.split(key['Key'])[0]) not in ignore_list:
                    print(key['Key'])
                    remote_keys.append(os.path.relpath(key['Key'], remote_path))
    except KeyError:
        print(f"Found no existing contents at {remote_path}")
    
    remote_directories = []
    final_remote_files = []
    for filename in remote_keys:
        if (os.path.dirname(filename)) != "": #i.e., it's a dir
            remote_directories.append((filename.split("/"))[0])
        else:
            final_remote_files.append(filename)

    remote_directories = list(set(remote_directories))

    remote_dirs_and_files = (remote_directories, final_remote_files)

    return remote_dirs_and_files

def map_current_dir_to_url(base_dir, current_dir, url_prefix):
    relative_current = os.path.relpath(current_dir, start=base_dir)
    return urllib.parse.urljoin(url_prefix, relative_current)

def map_dir_to_url(base_dir, current_dir, directory, url_prefix):
    relative_current = os.path.relpath(current_dir, start=base_dir)
    directory_index = os.path.normpath(os.path.join(relative_current, directory, IFILENAME))
    name = os.path.basename(directory)
    return {
        "name": name,
        "url": urllib.parse.urljoin(url_prefix, directory_index)
    }

def map_file_to_url(base_dir, current_dir, a_file, url_prefix):
    relative_current = os.path.relpath(current_dir, start=base_dir)
    file_path = os.path.normpath(os.path.join(relative_current, a_file))
    name = os.path.basename(a_file)
    return {
        "name": name,
        "url": urllib.parse.urljoin(url_prefix, file_path)
    }

def parent_url(base_dir, current_dir, url_prefix):
    relative_current = os.path.relpath(current_dir, start=base_dir)
    up_one_index = os.path.normpath(os.path.join(relative_current, "..", IFILENAME))
    return urllib.parse.urljoin(url_prefix, up_one_index)

if __name__ == '__main__':
    main()
