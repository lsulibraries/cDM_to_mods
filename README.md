# cDM_to_mods
for converting the output of cdm_xporter into mods format (especially for inject into Islandora)

1)  Turn on your python3 virtualenv.  It needs lxml.  Ananconda works well.

2)  In the command line, navigate to the cDM_to_mods directory.

3)  `python convert_to_mods.py $alias`

4)  If all goes well, `python post_converstion_cleanup.py $alias`

