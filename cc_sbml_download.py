import cellcollective
import biolqm
import requests
import json
from urllib.request import urlretrieve
import glob
import pandas as pd

#a simple function creating a permanent local file from the retrieved model file
def download_local(url, path, model_id, suffix='sbml'):
    filename = path+str(model_id)+'.'+suffix
    filename, _ = urlretrieve(url, filename=filename)
    return filename

def main():
    print('Hello World')

if __name__ == "__main__":
    main()