`[EasyPCP][Point Cloud Creation] Analyze and Disable blurry photos...
AnalyzePhotos
analyzing photos... ******************************************************Traceback (most recent call last):
  File "pipeline-all.py", line 315, in <module>
    disable_below_threshold(blur_threshold)
  File "pipeline-all.py", line 95, in disable_below_threshold
    chunk.analyzePhotos()
MemoryError: bad allocation`

- Solved by re-running `pipeline-all.bat`



`(easypcp) C:\Users\Alex\Documents\GitHub\3Dphenotyping\easypcp>python example/alex_batch3.py
[Pnt][__init__]Append "C:\Users\Alex\Documents\GitHub\3Dphenotyping\easypcp" to system.path
Traceback (most recent call last):
  File "example/alex_batch3.py", line 3, in <module>
    import easypcp as pcp
ModuleNotFoundError: No module named 'easypcp'`

- 



`(easypcp37) C:\Users\Alex>python Documents\GitHub\3Dphenotyping\easypcp\creation\pipeline-all.py
No license found.
Details: No license for product (-1)`

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

C:\Users\Alex\.conda\envs\easypcp37\Lib\site-packages\Metashape

Metashape.app.activated still `False`.





