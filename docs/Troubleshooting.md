# Troubleshooting

If you encounter an issue not listed below, please submit an issue in the repository issue tracker. ("Issues" in top bar)

## EasyDCP_Creation

---

`error - 'document saving disabled in read-only mode'`

**Cause:** Closing EasyDCP_Creation during execution. Metashape creates a 'lock' file within a project while it is open. The 'lock' file is automatically deleted by Metashape after saving and closing the project normally.

**Solution:** delete 'lock' file in [project id].files folder, or delete project .psx and .files. Re-run EasyDCP_Creation (creation.py) starting from the affected image set. **see Running EasyDCP on a subset of image sets TODO**

---

`No license found.
Details: No license for product (-1)`

**Cause:** cause: trying to use demo version of Metashape

**Solution:** Request 30-day trial code for Metashape Professional at https://www.agisoft.com/downloads/request-trial/ and activate Metashape. 

---

`OSError: Document.save(): saving is disabled`

**Cause:** running Metashape in demo mode. 

**Solution:** Get trial Metashape Professional license and activate. (See above)

---

`MemoryError: bad allocation`

**Cause:** `detect_noncoded_targets = True` in `params.ini`

**Solution**: set `detect_noncoded_targets = False`

---

```
file_list = os.listdir(path_photos)

FileNotFoundError: [WinError 3] The system cannot find the path specified:
```

Cause: `root_folder` variable in `params.ini` does not have a `\` at the end

Solution: Add `\` to the end of the `root_folder` folder path

---

## EasyDCP_Analysis

---

`ModuleNotFoundError: No module named 'easydcp'`

**Cause**: `import __init__.py` is missing from python script. 

**Solution**: Add line: `import __init__.py` before `import easydcp`.

---

`SyntaxError: EOL while scanning string literal`

**Cause**: String is a file or folder path, containing `\` character.

**Solution**: Replace `\` characters with `/`.

---

**Issue**: EasyDCP hangs on `Clustering`

**Cause**: `eps_points` is too high

**Solution**: Reduce `eps_points` value.

---

**Issue**: Plant segmentation incorrectly separates one plant into two segments

**Cause**: Distance between points is high

**Solution**: Increase `eps_points` parameter in `dbscan_segment()` function of `analysis.py`

---

## Output data

---

Opening output .csv in Excel:

"[filename.csv] cannot be accessed. The file may be corrupted, located on a server that is not responding, or read-only"

**Cause**: Filename or path is too long

**Solution**: Rename the .csv file to a shorter name, or move to a folder with a shorter path.

```

```