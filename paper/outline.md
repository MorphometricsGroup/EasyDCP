# Paper outline - 3Dphenotyping [Paper Title]

## Introduction

### Background

- phenotyping for breeding, yield, etc

### Purpose
- phenotype a huge amount of plants automatically
- reduce money and time costs

### Current techniques
- Paulus 2019 "Measuring crops in 3D: using geometry for plant phenotyping"
- weakness of current techniques

### difference of our work
- open source
- affordable software and hardware
- low cost (money and time)

## Materials and Methods

### Section 1: Photos to PCD

- container plants
- camera, markers, scalebar, etc
- pc with agisoft metashape pro 
- auto_ctrl scripts from github

### Section 2: PCD to Traits

- PCD from Agisoft
- PCD from Planteye
- pc with python/anaconda
- phenotypy scripts from github

## Results

### Section 1: Photos to PCD

- Produced PCD . Show figures
- compare Projected LA from raw image to PLA from HZ script

### Section 2: PCD to Traits

- Produced individual plant PLY, output graphics, and CSV.
- Compare to Planteye traits (height, heightmax?, and projected leaf area)

## Discussion
- ground level. Substrate surface or bottom of container? Below ground leaves in the case of measuring on a raised platform like planteye?
- tested on field with spaces between plants but difficulties with classification and segmentation make it difficult to use 
- - (too many misclassified weeds throw off the segmentation)

## Conclusion 
- our system works well for container plants, enables batch photographing and processing
- eliminates need for a photogrammetry chamber

### Future Work
- need develop model to work on field 