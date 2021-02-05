# Installation

## Requirements

Any PC with Windows, Linux, or Mac OS.

32 GB RAM recommended. As little as 8 GB may be usable depending on the case.

[Agisoft Metashape Professional 1.6.~~5~~**6!**](https://www.agisoft.com/downloads/installer/) 

​	[30-day trial license](https://www.agisoft.com/downloads/request-trial/)

​	[Educational license](https://www.agisoft.com/buy/online-store/educational-license/)

​	[System requirements](https://www.agisoft.com/downloads/system-requirements/)

Python 3.7+ environment

​	We recommend [Anaconda](https://www.anaconda.com/products/individual#Downloads).

## Recommendations

One or more dedicated GPU (GeForce, Radeon, etc.)

[CloudCompare](http://www.danielgm.net/cc/release/) - for viewing .ply files

[GIMP](https://www.gimp.org/downloads/) or other image manipulation software - for creating .png training data images for EasyDCP_Analysis

## Installing from source code

1. Clone or download the EasyDCP repository to any path on your PC.

2. Open your python 3 environment (we recommend creating a new environment using Anaconda or similar) or python IDE, install the `requirements.txt` in **Administrator permission**.

   - Using Anaconda, Select your EasyDCP environment, and 'Open Terminal'. 

   - Navigate to the EasyDCP directory: `cd D:\Program\EasyDCP`

   - Install requirements using `pip`:

     `(YourEnv) D:\Program\EasyDCP`\> pip install -r requirements.txt`

3. Ensure Agisoft Metashape Professional is installed and activated using 30-day trial or paid license. 

   - Note: EasyDCP currently supports metashape.exe control via python script. ~~In future, will update to use python Wheels package: https://pip.pypa.io/en/latest/user_guide/#installing-from-wheels~~

4. EasyDCP is now ready to use. See other docs: [Image acquisition](0_Image_acquisition.md), [EasyDCP Creation](1_EasyDCP_Creation.md), and [EasyDCP Analysis](2_EasyDCP_Analysis.md) for instructions.

## Installation Errors

---

For **China Mainland** users, some packages via pip may be very slow, and may get HTTP network error:

```bash
    raise ReadTimeoutError(self._pool, None, "Read timed out.")
pip._vendor.urllib3.exceptions.ReadTimeoutError: HTTPSConnectionPool(port=443): Read timed out.
```

Please keep trying to reinstall **or use Tsinghua pip mirror** to accelerate the installation:

`(YourEnv) D:\Program\EasyDCP`\> pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

---

### Open3d import errors

```python
Traceback (most recent call last):
	File "", line 1, in
	File "C:\Python37\lib\site-packages\open3d_init_.py", line 28, in
	from .open3d import * # py2 py3 compatible
ImportError: DLL load failed: The specified module could not be found.
```

Please refer this link to solve this problem:https://github.com/intel-isl/Open3D/issues/979

The author solved this by installing `Microsoft Visual C++ Redistributable for Visual Studio 2015, 2017 and 2019`  as suggested by previous link. Quick download link: https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads

