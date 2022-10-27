import logging
import os
from os import path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import yaml
from tqdm.auto import tqdm  # type: ignore


def download_from_yaml(
    yaml_file: str, output_dir: str, ignore_cache: bool = False, snippet_only=False, verbose=False
) -> None:
    """Given an download info from an download.yaml file, download all files

    Args:
        yaml_file: A string pointing to the download.yaml file,
        to be parsed for things to download.
        output_dir: A string pointing to where to write out downloaded files.
        ignore_cache: Ignore cache and download files even if they exist [false]
        snippet_only: Downloads only the first 5 kB of each uncompressed source,
        for testing and file checks
        verbose: verbose [False]

    Returns:
        None.
    """

    os.makedirs(output_dir, exist_ok=True)
    with open(yaml_file) as f:
        data = yaml.safe_load(f, Loader=yaml.FullLoader)
        items = tqdm(data, desc="Downloading files")
        for item in items:
            if verbose:
                items.set_description(f"Downloading {item['url']} to {item['local_name']}\n")
            if "url" not in item:
                logging.warning("Couldn't find url for source in {}".format(item))
                continue
            if snippet_only and (item["local_name"])[-3:] in [
                "zip",
                ".gz",
            ]:  # Can't truncate compressed files
                logging.warning("Asked to download snippets; can't snippet {}".format(item))
                continue
            outfile = os.path.join(
                output_dir,
                item["local_name"] if "local_name" in item else item["url"].split("/")[-1],
            )
            logging.info("Retrieving %s from %s" % (outfile, item["url"]))

            if path.exists(outfile):
                if ignore_cache:
                    logging.info("Deleting cached version of {}".format(outfile))
                    os.remove(outfile)
                else:
                    logging.info("Using cached version of {}".format(outfile))
                    continue

            try:
                req = Request(item["url"], headers={"User-Agent": "Mozilla/5.0"})
                with urlopen(req) as response, open(outfile, "wb") as out_file:  # type: ignore
                    if snippet_only:
                        data = response.read(5120)  # first 5 kB of a `bytes` object
                    else:
                        data = response.read()  # a `bytes` object for the full contents
                    out_file.write(data)
                    if snippet_only:  # Need to clean up the outfile
                        in_file = open(outfile, "r+")
                        in_lines = in_file.read()
                        in_file.close()
                        splitlines = in_lines.split("\n")
                        outstring = "\n".join(splitlines[:-1])
                        cleanfile = open(outfile, "w+")
                        for i in range(len(outstring)):
                            cleanfile.write(outstring[i])
                        cleanfile.close()

            except HTTPError as e:
                logging.warning("Couldn't download source in {} due to error {}".format(item, e))

    return None
