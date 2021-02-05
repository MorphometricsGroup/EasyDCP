# EasyDCP_Creation

### Materials: 

Photos from image acquisition step, organized into folders by group as described in [Image acquisition](0_Image_acquisition.md).

Agisoft Metashape Professional 1.6.6 with activated trial license, or paid license.

CloudCompare (optional) for viewing output .ply files.

1. Edit user-defined variables in `easydcp\creation\params.ini` using text editor
   - Set `root_folder`to the path containing the folders of images. Include a trailing `\`!
     - e.g. if `c:\population001\group001\img_001.jpg...`, `root_folder = c:\population001\`
   - Set other parameters as needed. Defaults are set, and each parameter is explained with a code comment.
- `params.ini` must be located in `easydcp\creation`!
  
2. Ensure folder structure matches intended format (see step 4 of [Image acquisition](0_Image_acquisition.md))
   - Ensure the only items in the `root_folder` folder are the image set folders and `\skip\`. Any other files or folders in the `root_folder` folder may cause an error.
   - `\skip\` must contain `scalebars.csv` and `orientation.ini`

4. Run `creation-win.bat` or `creation-mac.sh`
   - A terminal window will open showing output from EasyDCP_Creation and Metashape.
   - EasyDCP_Creation will work through each image set folder (imaged group of plants) and produce a 3D point cloud, outputted to .ply format.
   - If you must close the terminal window (or an error occurs) while EasyDCP_Creation is running, there may be a `lock` file left in the last folder that was being processed. You must either delete the .lock file from within the `[groupID].files\` folder or delete the entire `[groupID].files\` folder and `[groupID].psx` file.
   
5. Find output .psx and .ply files in each corresponding folder. Verify successful 3D reconstruction with Metashape and CloudCompare, respectively. 
   
   - A .pdf report is also created where you can quickly view an overhead image of the point cloud check details such as the number of camera images used by Metashape, the parameters passed by EasyDCP_Creation, image resolution, processing time, etc.
   
5. We recommend copying the .ply files to a new folder for use with EasyDCP_Analysis, if storage space is available.

   ```population001
   ply_out
   ├── group001.ply
   ├── ...
   └── group009.ply
   ```

6. Save a copy of `params.ini` for reproducibility.

7. Proceed to [EasyDCP_Analysis](2_EasyDCP_Analysis.md).