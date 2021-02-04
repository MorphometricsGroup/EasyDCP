# EasyDCP_Creation

Materials: 

Photos from image acquisition step, organized into folders by group as described in `image acquisition.md`.

~~Agisoft Metashape Professional 1.6.5~~

~~CloudCompare (optional)~~

1. Edit params.ini user-defined variables:
   - Open `easydcp\creation\params.ini` in text editor 
   - set all parameters as desired, defaults are set, and each parameter is explained in the code comments, e.g.:
     - set `align_quality` and `dense_quality`, default medium
     - change`path_folders`to the path containing the folders of images
     - e.g. if `c:\images_root\imageset_1\img_001.jpg...`, `path_folders = c:\images_root`
     - change `blur_threshold` to desired value. Pipeline will disable all images with Agisoft image quality below the `blur_threshold`.
     - set booleans e.g., `ignore_gps`, `align_ground`, and `use_scalebars ` as needed
2. Ensure folder structure matches intended format (see Image acquisition)
   - only folders in root folder (path_folders), no files in root
     - e.g. (`path_folders\images_1\img_001.jpg...`)
   - 'skip' folder contains scalebars.csv if needed 
     - located in `path_folders\skip`
     - **Default scalebars.csv provided in 3dphenotyping\materials to match targets.pdf. Copy to [path_folders]\skip directory.**
3. Open `easydcp\creation\creation.bat` in text editor, and confirm the path to your `easydcp\creation` folder.
4. Run `creation.bat` ~~**[todo] update program to use agisoft package. update installation for .whl.**~~
   - Find output .psx and .ply files in each corresponding folder. **[todo] change output to single folder?** Verify successful 3D reconstruction with Agisoft and CloudCompare, respectively.

