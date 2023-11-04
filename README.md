## Final Degree Project
Code for data integration, processing, and creation of univariate, bivariate, and survival analysis
# Medical Data Analysis Tools

This repository contains a set of tools and scripts developed in Python for the analysis of medical data. These tools allow data integration and processing, the creation of informative graphs, and the generation of PowerPoint slides for presenting results.

## Repository Structure

The repository is organized into three main folders:

1. `integration_processing`: This folder contains the scripts and auxiliary modules necessary for the integration and processing of medical data. The included files are:
    - `concat.py`: Performs the integration of tables obtained from a relational database into a single pandas DataFrame.
    - `processing.py`: Processes medical variables of interest for subsequent analysis.

2. `slide_creation`: In this folder, you will find the functions and code required for generating PowerPoint slides. The included files are:
    - `univ_functions.py`: Contains functions for creating graphs of different types of variables, handling missing values and data collection errors, and generating informative PowerPoint slides.
    - `biv_functions.py`: Similar to `univ_functions.py`, but includes functions for bivariate data analysis, taking a grouping variable as an argument.

3. `data_analysis`: This folder contains the main scripts for performing data analysis. The included files are:
    - `Univ_main.py`: Generates univariate analysis and creates PowerPoint slides.
    - `Biv_main.py`: Generates bivariate analysis and creates PowerPoint slides.
    - `surv_main.py`: Provides a graphical interface to generate survival curves and download the results in PowerPoint format.

To run the main scripts, simply open a terminal in the corresponding directory and execute the command `python <script_name>.py`.
