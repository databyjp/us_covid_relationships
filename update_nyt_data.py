# ========== (c) JP Hwang 30/6/20  ==========

import logging

# ===== START LOGGER =====
logger = logging.getLogger(__name__)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
root_logger.addHandler(sh)

import urllib.request
import os
from datetime import datetime

srcpath = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
dstpath = "srcdata/us-counties.csv"
dlflag = False

if os.path.exists(dstpath):
    modtime = os.path.getmtime(dstpath)
    olddate = datetime.fromtimestamp(modtime).date()
    if datetime.utcnow().date() > olddate:
        logger.info(f"Existing data file is potentially outdated {olddate}, setting download flag to True.")
        os.rename(dstpath, dstpath + ".old")
        dlflag = True
    else:
        logger.info(f"Existing data file is dated {olddate}, all seems well.")
else:
    logger.info("File not found, setting download flag to True")
    dlflag = True

if dlflag:
    logger.info("Downloading the latest NYT COVID-19 data.")
    with urllib.request.urlopen(srcpath) as f:
        srcfile = f.read().decode('utf-8')

    logger.info(f"Saving the downloaded data to {dstpath}.")
    with open(dstpath, "w") as f:
        f.write(srcfile)
