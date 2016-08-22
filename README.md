# cDM_to_mods
for converting the output of cdm_xporter into mods format (especially for inject into Islandora)

1)  Turn on your python3 virtualenv.  It needs lxml.  Ananconda works well.

2)  Make sure there is a directory Cached_Cdm_files in the same folder as your cDM_to_mods folder.

3)  In the command line, navigate to the cDM_to_mods directory.

4)  `python convert_to_mods.py $alias`

5)  If all goes well, `python post_converstion_cleanup.py $alias`

