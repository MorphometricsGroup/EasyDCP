# Image acquisition

Materials : 

Floor area minimum 1 m x 1 m, as level as possible.

Container plants. Avoid using green-colored container.

floor covering (black or other non-plant color) (optional)

RGB camera

Printed attached .pdf file `easydcp\materials\targets.pdf`, first 2 pages. ~~[EasyDCP requires 4 targets per page. i used 6mm radius .]~~ Attach to clipboard or other rigid backing. Measure the distances between the center points of the coded targets and compare to `materials/scalebars.csv`. Correct the .csv file if needed.

1. The height of plant container is needed by EasyDCP, so be sure to measure and record the height of the container in meters. If the container is on any riser platform, record the height of the riser and add it to the container height.

2. If using floor covering, place on desired area to be used for image acquisition. If not using floor covering, ensure floor area is free of any materials that may be similar to plant color (e.g. weeds)

3. Define measurement area by placing the two printed target target pages at opposite corners. [see figure 1] Page 1 in bottom-left corner, page 2 in top-right corner. Ensure target pages are level (especially page 1!) and not upside-down.

4. Arrange a group of container plants within the measurement area, by placing them in a single row, or 2 rows using triangular spacing [see figure 1]. Ensure at least 10cm gap between all plants. *Note: The number of plants per group is only limited by the size of the measurement area and the size of the plants.*

   <p align="center"><img src="iaq_1.png" width=600></p>

   *Figure 1*

5. Photograph the plants from above, in one or more rows parallel to plant row. We recommend 10-15 images per each meter of plant row at 1 meter camera distance from target. See figure 2 for example: 4 rows of images (blue rectangles) were captured over a 1 m x 2 m space, average 12 images per meter per row.

   <p align="center"><img src="iaq_2.png" width=600></p>

   *Figure 2*

6. Repeat steps 4 and 5 for all remaining plants. We recommend to keep the number of plants per group constant if possible, and keep plant spacing uniform across groups. See figure 1a and 1b.

7. Organize photos into folders by group. The root folder can be located anywhere on any drive. One folder per one group of plants. Even if there is only one group, follow this folder structure. Create a `/skip/` folder and copy `/materials/scalebars.csv` and `/materials/orientation.ini` to `/skip/`.
   Example: for a given population, assume 9 plants divided into 3 groups of 3 plants each:

```
population001
├───group001
│   ├── IMG_0001.JPG
│   ├── IMG_0002.JPG
│   └── ...
├───group002
│   ├── IMG_0001.JPG
│   ├── IMG_0002.JPG
│   └── ...
├───group003
│   ├── IMG_0001.JPG
│   ├── IMG_0002.JPG
│   └── ...
└───skip
    ├── scalebars.csv
    ├── orientation.ini
    └── [other files/folders to ignore]
```

8. Proceed to [EasyDCP_Creation](1_EasyDCP_Creation.md).