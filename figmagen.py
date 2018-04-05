#!/usr/bin/env python
import requests
import requests_cache
from halo import Halo
from unidecode import unidecode as uni
from iterfzf import iterfzf
import sys
from os import environ
from os.path import expanduser

import datetime

home = expanduser("~")
expire_after = datetime.timedelta(hours=8)
requests_cache.install_cache('{}/.figma'.format(home), expire_after=expire_after)
spinner = Halo(spinner = 'dots')

fileId = ""
if environ.get('FIGMA_FILE_ID') is not None:
    fileId = environ.get('FIGMA_FILE_ID')

headers = ""
if environ.get('FIGMA_TOKEN') is not None:
    headers = {'X-Figma-Token': environ.get('FIGMA_TOKEN')}

workFlow = False
if environ.get('FIGMA_WORKFLOW') is not None:
    workFlow = bool(environ.get('FIGMA_WORKFLOW'))

fileFormat = "svg"

def parse_figma(json, frames=False, selection=''):
    # Succeed placed here due to startup time of fzf
    spinner.succeed()
    for canvas in json['document']['children']:
        canvasString = "{} -- {}".format(uni(canvas['name']), uni(canvas['id']))
        yield canvasString
    for canvas in json['document']['children']:
        for frame in canvas['children']:
            frameString = "{}.{} -- {}".format(uni(canvas['name']), uni(frame['name']), uni(frame['id']))
            yield frameString

def get_figma_image(fileId, ids):
    spinner.start("Requesting images from Figma...")
    url = "https://api.figma.com/v1/images/{}?ids={}&format={}".format(fileId, ','.join(id[1] for id in ids), fileFormat)
    response = requests.get(url, headers=headers)
    spinner.succeed()
    urls = []
    print "\nFigma SVG Files:\n"
    for key in response.json()['images']:
        value = response.json()['images'][key]
        if isinstance(value, unicode):
            urls.append(response.json()['images'][key])
            for x in ids:
                if x[1] == key:
                    print "{} -- {}".format(x[0], response.json()['images'][key])
    if (len(urls) > 0) and workFlow:
        print "\nWorkflow URL -- workflow://run-workflow?name=Figma%20URL&input=text&text={}".format(",".join(urls))

if __name__=="__main__":
    specified = False

    idArgs = []
    for arg in sys.argv[1:]:
        if arg == "--help":
            print """
figmagen --file='[FILE ID]' --token='[TOKEN]' [OPTIONS]... [FRAME IDS]...(optional)

OPTIONS:

--help      Display this message.
--file      The ID of the Figma file to fetch and render. A default may be provided by setting the 'FIGMA_FILE_ID' environment variable.
--token     The Access Token for your account. A default may be provided by setting the 'FIGMA_TOKEN' environment variable.
--purge     Clears the local cache of Figma responses (stored for 8 hours by default due to file size)
--workflow  Generate a concatenated x-callback-url for Workflow on iOS to allow passing of all requested images.
[FRAME IDS] A comma separated list of Frame/Canvas IDs to render. Bypasses selection process. (e.g. '2213:1,2235:125')
"""
            sys.exit()
        if arg == "--workflow":
            workFlow = True
        elif arg == "--purge":
            requests_cache.clear()
        elif "--token" in arg:
            try:
                headers = {'X-Figma-Token': arg.split('=')[1]}
            except:
                print "Token must be provided in format `--token='ABC123'`"
                sys.exit()
        elif "--file" in arg:
            try:
                fileId = arg.split('=')[1]
            except:
                print "File must be provided with format `--file='ABC123'`"
                sys.exit()
        elif arg == "--png":
                fileFormat = "png&scale=2.0"
        else:
            specified = True
            # Add arg as name to avoid parsing entire file for request
            idArgs.append([arg, arg])
            
    if fileId == "":
        print "File must be provided in format `--file='ABC123'`"
        sys.exit()

    if headers == "":
        print "Token must be provided in format `--token='ABC123'`"
        sys.exit()
        
    if specified:
        get_figma_image(fileId, idArgs)
    else:
        url = "https://api.figma.com/v1/files/{}".format(fileId)
        spinner.start('Fetching Figma file: {}'.format(fileId))
        response = requests.get(url, headers=headers)
        spinner.succeed()
        spinner.succeed('Fetched Figma file: {}'.format(response.json()['name']))
        spinner.start('Parsing Figma components...')
        selection = iterfzf(parse_figma(response.json()), encoding='utf-8', multi=True)
        selections = []
        if type(selection) is list:
            for item in selection:
                selections.append(item.split(' -- '))
        get_figma_image(fileId, selections)
