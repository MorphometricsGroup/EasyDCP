# Troubleshooting

## EasyDCP_Creation

---

`error - 'document saving disabled in read-only mode'`

**Cause:** Closing EasyDCP_Creation during execution. Metashape creates a 'lock' file within a project while it is open. The 'lock' file is automatically deleted by Metashape after saving and closing the project normally.
**solution:** delete 'lock' file in [project id].files folder, or delete project .psx and .files. Re-run EasyDCP_Creation (creation.py) starting from the affected image set. **see Running EasyDCP on a subset of image sets TODO**

----

`(easydcp37) C:\Users\Alex>python Documents\GitHub\3Dphenotyping\easydcp\creation\pipeline-all.py
No license found.
Details: No license for product (-1)`

**Cause:** cause: trying to use demo version of Metashape
**Solution:** Request 30-day trial code for Metashape Professional at https://www.agisoft.com/downloads/request-trial/ and activate Metashape. 

---

**TODO: wheels support. delete or implement?**

- https://www.agisoft.com/forum/index.php?topic=12092.0
- https://www.agisoft.com/forum/index.php?topic=10647.0

>>> `agisoft_LICENSE = agisoft_LICENSE = 'C:\Program Files\Agisoft\Metashape Pro'`
>>> `agisoft_LICENSE`
>>> `'C:\\Program Files\\Agisoft\\Metashape Pro'`
>>> `import Metashape`
>>> `print(Metashape.app.activated)`
>>> `False`
>>
>>

copied metashape.lic to python directory 

C:\Users\Alex\.conda\envs\easydcp37\Lib\site-packages\Metashape

Metashape.app.activated still `False`.

**This should also solve the issue with running from .whl!**

"You can try Agisoft Metashape software either in demo mode (export and save functions are blocked) or test it in full function mode with 30-day trial license for free."

https://www.agisoft.com/downloads/request-trial/

---

`OSError: Document.save(): saving is disabled`

Same as above. Issue is caused by running Metashape in DEMO mode. Get trial Metashape Professional license and activate.

---

## EasyDCP_Analysis

---

`MemoryError: bad allocation`

**Cause:** `detect_noncoded_target = True`

**Solution**: set `detect_noncoded_target = False

---

`(easydcp) C:\Users\Alex\Documents\GitHub\3Dphenotyping\easydcp>python example/alex_batch3.py
[__init__]Append "C:\Users\Alex\Documents\GitHub\3Dphenotyping\easydcp" to system.path
Traceback (most recent call last):
  File "example/alex_batch3.py", line 3, in <module>
    import easydcp as dcp
ModuleNotFoundError: No module named 'easydcp'`

- `example\__init__.py` was missing. replaced it and error resolved.

---

`FileNotFoundError: [Errno 2] No such file or directory: 'plot_out\\s2g1-v054-all-nocross-high-med816-class[0].png'`

caused by plot_out folder not existing in location where easydcp is being run

**Tried modifying easydcp to create the plot_out folder if it does not exist. Now need error catching for when the folder does exist, or comment that line out.**

**Todo**: Implement create folder if not exist functionality

---

`[Plant][Traits] No. 0 Calculating
Traceback (most recent call last):
  File "example\alex_batch3.py", line 53, in <module>
    if not planteye: traits = plot_class.get_traits(container_ht=0.06)#, ground_ht =g_ht)
  File "C:\Users\Alex\Documents\GitHub\3Dphenotyping\easydcp\base.py", line 543, in get_traits
    container_ht=container_ht, ground_ht=ground_ht)
  File "C:\Users\Alex\Documents\GitHub\3Dphenotyping\easydcp\base.py", line 611, in __init__
    corner)
  File "C:\Users\Alex\Documents\GitHub\3Dphenotyping\easydcp\base.py", line 651, in get_region_props
    regions = regionprops(binary, coordinates='xy')
  File "C:\Users\Alex\.conda\envs\easydcp37\lib\site-packages\skimage\measure\_regionprops.py", line 881, in regionprops
    raise ValueError(msg)
ValueError: Values other than "rc" for the "coordinates" argument to skimage.measure.regionprops are no longer supported. You should update your code to use "rc" coordinates and stop using the "coordinates" argument, or use skimage version 0.15.x or earlier.`

solved by uninstalling scikit-image and reinstalling 0.15.0 

updated requirements.txt 

**todo: update for current version of scikit-image**

---

# Data analysis

---

Opening output .csv in Excel:

"[filename.csv] cannot be accessed. The file may be corrupted, located on a server that is not responding, or read-only"

Cause: Filename is too long

Solution: Rename the .csv file to a shorter name.