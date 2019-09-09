# How to:

for converting the output of cdm_xporter/scrape_cdm.py into mods format (especially for ingest into Islandora)

### Setup
  
  1a) Windows:  Check if Anaconda is your default python, by typing in a command prompt: `python --version`.  It should read `python3 Anaconda ...`.  Install dependencies, using Powershell as an Administrator, `pip install py-trello`
        
  1b) Linux/Mac:  Turn on your python3 virtualenv.  `pip install lxml`.  If there are any libraries it fails on, then `sudo apt-get install` those prerequesites.  There's some obscure library they forget to tell you to install.  After apt-getting those libraries, `pip install lxml` works.  Also run in you virtualenv `pip install py-trello`.
 
  2) Have the folder Cached_Cdm_files (the output of cdm_xporter/scrape_cdm.py) on your computer (or network).

### Converting contentDM output to mods
  
  1) In the command line, navigate into the cDM_to_mods directory.
  
  2) Have a file `trello_keys.json` in this cDM_to_mods folder.  This file is not synced to git for security reasons.  The contents of this file is `{"api_key":"something","api_secret":"something","token":"something"}` where your api_key, etc are found from https://trello.com/app-key .
  
  3) Make a mapping_file for each collection.  A mapping file assigns each Dublin Core element to it's MODS equivalent.  See the examples in ./mappings_files/

  4) Make an alias_xslt file for each collection.  An alias_xslt file is a list of xslts to run against the rough mods files.  After they run, the mods should be valid mods.  You'll find a number of useful xlst's in the ./xsl/ folder.  But you may also write your own & save it at ./xls/

  5) `python convert_to_mods.py {alias} {path/to/Cached_Cdm_files}`
        -this /Cached_Cdm_files needs only metadata.
  
  6) `python post_converstion_cleanup.py {alias} {path/to/U_drive/Cached_Cdm_files}`
        -this /Cached_Cdm_files needs metadata+binaries

### Converting a spreadsheet to mods

  1) See Xslx_Template_Prototype for an example.

  2) Make an alias_xslt file for each collection.  An alias_xslt file is a list of xslts to run against the rough mods files.  After they run, the mods should be valid mods.  You'll find a number of useful xlst's in the ./xsl/ folder.  But you may also write your own & save it at ./xls/

  3) The mapping is a sheet in your xslx file; no need for a separate file.

  4) Your binaries can be grouped in whatever folder(s) you name in the Spreadsheet.  With one restriction: a compound object's binaries must all be in one folder named after the "Identifier" of the parent object as named in the Spreadsheet.

  4) `python xlsx_to_mods.py {path/to/your_spreadsheet.xlsx}`

  5) `python post_xlsx_cleanup.py {alias} {root folder with the spreadsheet.xslx & binaries}


## What they do

convert_to_mods.py:
  - applies the cDM_to_mods/mappings_file/{alias}.csv to the Cached_Cdm_files data to create a rough mods file.

convert_to_mods.py and xlsx_to_mods.py:
  - performs xsl transformations named in the cDM_to_mods/alias_xlsts/{alias}.txt file to refine the mods.
  - validates each mods record against the mods schema.
  - compares the count of xmls to the reported number of items in TotalRecs.xml
  - complains loudly if anything fails.

  - This step's output can be found in cDM_to_mods/output/{alias}\_simple/final_format and cDM_to_mods/output/{alias}\_compound/final_format.  Seperating simples from compounds facilitates easier uploading into Islandora.

post_conversion_cleanup.py and post_xlsx_cleanup.py:
  - verifies that each object in the collection was converted into a mod file.  
  - pulls the binaries from the source_directory into the proper position within the output files.
  - complains if there is not exactly one {.jp2, .mp3, .mp4, .pdf} for each mods.
  - creates a structure file, which is necessary for Islandora Compound Batch Upload.  
  - checks all the mods for access restrictions, and reports those to cDM_to_mods/{alias}\_restrictions.txt  
  - packages the items into zips as required by Islandora Batch importer
  - moves the zip files to the shared network drive (U/Upload_to_Islandora)
  - posts the log onto the matching Trello card & moves the card to the column 'Whole Collection Packaged at U'

  - This step's output can be found in cDM_to_mods/Upload_to_Islandora/{alias}
