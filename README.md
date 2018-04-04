## figmagen

A python script to retrieve programmatically retrieve Figma design files and generate SVGs use the first-party Figma API.

### Requirements
```bash
pip install -r requirements.txt
```
figmagen requires Python **2.7.14** or greater, but is not compatible with Python 3.

### Usage
```
figmagen --file='[FILE ID]' --token='[TOKEN]' [OPTIONS]... [FRAME IDS]...(optional)

OPTIONS:

--help      Display this message.
--file      The ID of the Figma file to fetch and render. A default may be provided by setting the 'FIGMA_FILE_ID' environment variable.
--token     The Access Token for your account. A default may be provided by setting the 'FIGMA_TOKEN' environment variable.
--purge     Clears the local cache of Figma responses (stored for 8 hours by default due to file size)
--workflow  Generate a concatenated x-callback-url for Workflow on iOS to allow passing of all requested images.
[FRAME IDS] A comma separated list of Frame/Canvas IDs to render. Bypasses selection process. (e.g. '2213:1,2235:125')
```

#### File ID
The `file` identifier can be retrieved from any Figma file URL. For example: `https://www.figma.com/file/jfa1skOOHVadsfh884h/Example.File` would result in a File ID of `jfa1skOOHVadsfh884h`. A default file will be used if the environment variable `FIGMA_FILE_ID` is set and no file parameter is specified.

#### Token
Figma offers [Personal Access Tokens](https://www.figma.com/developers/docs#auth-dev-token) to authenticate requests to their API. This can be passed as a command line parameter, but figmagen will also read from the environment variable `FIGMA_TOKEN` for convenience.


#### Frame IDs
If you happen to know your node IDs (e.g. `22314:5724`), you may provide a string delineated listed at the end of your parameter input to bypass the full Figma file retrieval and interactive selection steps.

#### Workflow
As was conceived to enable reviewing Figma assets on laptops/devices that Figma was unavailable (or undesirable), I included the ability to generate a grouped Workflow x-callback-url. This URL will include all the requested image URLs and run a Workflow titled `Figma URL`. You must have a Workflow with this name for the callback URL to function.

### Caching
Despite the Figma's API responding with JSON, Figma file requests may be quite large -- possibly over 100MB. To address this, figmagen utilized the [requests-cache](https://github.com/reclosedev/requests-cache) library to provide a persistence cache for responses. By default, the cache will be valid for **eight** hours from the last request. This also applies to rendering requests. This should reduce load time if you're planning on reviewing multiple areas of a Figma file or repeating requests.

If the source file is changed and you'd like to retrieve the latest details, include the `--purge` parameter with your request. 
