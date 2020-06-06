# Hedging-Saving

[![Build Status](https://travis-ci.org/chengweilin114/direct_capstone2020.svg?branch=master)](https://travis-ci.org/github/chengweilin114/direct_capstone2020)
[![Coverage Status](https://coveralls.io/repos/github/chengweilin114/direct_capstone2020/badge.svg?branch=master)](https://coveralls.io/github/chengweilin114/direct_capstone2020?branch=master)

Introduction: Enel X has customers that participate in a special system peak program aimed at optimizing cost of energy in batteries. In this program, if Enel X storage or load is dispatched by our customers (ie, make their electricity load small) during the five highest hour long peaks in the year of the total grid, Enel X is rewarded at approximately $100/kW. The system peak program was designed by the local utility to lower peak electricity load on the grid. Thus, Our goal is working on a project that will help Enel X ‘s customers to fully utilize the battery capacity and optimize the electricity cost.

## Table of Contents


- [Organization of the project](#Organization-of-the-project)
- [Software Dependencies](#Software-Dependencies)
- [Project Data](#Project-Data)
- [Documentation](#Documentation)
- [Installation](#Installation)
- [Licensing](#Licensing)


## Organization of the project

The project has the following structure:

    direct_capstone2020/
      |- codes/
        |- Summarize_functions.ipynb
        |- dataset.ipynb
        |- results_for_performance.ipynb
        |- step1_summary.ipynb
        |- step2_summary.ipynb
        |- step3_summary.ipynb
        |- step4_summary.ipynb
      |- database/
        |- data
      |- docs/
        |- Gantt Chart.png
        |- Project_proposal.pdf
        |- use_cases
      |- README.md
      |- environment.yml
      |- .gitignore
      |- LICENSE


## Software Dependencies

- Python 3
- Use `environment.yml` to create an environment


## Project Data


## Documentation

`Hedging-Saving/data_functions.py`

This module contain functions to retrieve and process data from the database folder. 
With all these functions, we can predict our peak hour more accurate. 

## Installation

Below are the steps to install this package:
1. Clone this repo to the computer: `git clone https://github.com/chengweilin114/direct_capstone2020`

2. In the repo directory install and the environment:
```
conda env create -f environment
conda activate environment
```

## Licensing


We use the MIT license to maintains copyright to the authors.
