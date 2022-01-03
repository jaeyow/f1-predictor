[![F1 Prediction MLOps](https://github.com/jaeyow/f1-predictor/actions/workflows/f1-mlops.yml/badge.svg)](https://github.com/jaeyow/f1-predictor/actions/workflows/f1-mlops.yml)

# ![](https://ga-dash.s3.amazonaws.com/production/assets/logo-9f88ae6c9c3871690e33280fcf557f33.png) Capstone Project
---
#### [Capstone Project, Part 1: Proposal](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part1-proposal.ipynb)
#### [Capstone Project, Part 2: Brief](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part2-brief.ipynb)
- [Writing data to MongoDB](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part2-brief.ipynb#mongo_db)
- [Data Dictionary](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part2-brief.ipynb#data_dictionary)
- [Map of races around the world](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part2-brief.ipynb#world-map)

#### [Capstone Project, Part 3: Technical Notebook](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part3-technical-notebook.ipynb)
- [Feature Engineering](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part3-technical-notebook.ipynb#feature_eng)
- [Regression Approaches](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part3-technical-notebook.ipynb#regression_approaches)
- [Classification Approaches](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part3-technical-notebook.ipynb#classification_approaches)
- [Feature Importance](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part3-technical-notebook.ipynb#feature_importance)
- [Feature Selection](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part3-technical-notebook.ipynb#feature_selection)
- [Models Comparison](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part3-technical-notebook.ipynb#models_comparison)

#### [Capstone Project, Part 4: Presentation](https://61c08c5e1627a3416b0c37b4--pensive-nobel-d54f9f.netlify.app/)
#### [Capstone Project, Part 5: Appendix](https://nbviewer.org/github/jaeyow/f1-predictor/blob/main/final-project-part5-appendix.ipynb)

#### [Capstone Project, Part 6: MLOps](https://github.com/jaeyow/f1-predictor/blob/main/.github/workflows/f1-mlops.yml)
Using GitHub Actions as a cheap (and free) MLOps tool alternative: - invoke MLOps workflow on-demand (or with a cron schedule)
- get latest source
- setup Python build/MLOps environment
- data retrieval and preparation
- feature engineering
- preparation for model training (including dummify categorical features)
- feature selection
- model building and scoring
- setup serverless (lambda) API in AWS
- deploy model to serverless API
- profit!
![](images/f1-mclaren-car.png)

## Problem Statement

Ever since the first season of [Drive to Survive](https://en.wikipedia.org/wiki/Formula_1:_Drive_to_Survive), I've been captivated by the drama and excitement that is Formula 1. I've been consuming this public API in some of my past blog posts and I thought it would be fun to continue this trend and explore the insights and predictions that can be gleaned from past race data:

- predict the podium placers (1st, 2nd, 3rd) in a race
- predict the winner (pole-position) in a qualifying race
- predict who wins the fastest lap in the race
- who wins the constructor at the end of the year
- explore the effect of factors such as Constructor/team membership, weather, home circuit advantage, age/years of experience of driver, qualifying position, etc on the outcome of the race


### Hypothesis and Assumptions

1. Some Formula 1 constructors (teams) have a tendency to win championships more than others

2. The weather plays a crucial factor to the result of a race. Some drivers drive their best in inclement weather, while others excel in perfect weather conditions.

3. Starting the race towards the front of the grid (pole position), increases the odds of winning the race.

4. Home circuit advantage increases the odds of winning the race. 

5. Driver's age and years of experience in F1 affects winning races. That there is an optimum age for winning races  and that this is not just a linear relationship.

### Goals and success metrics

The main goal is to predict the winner of a 2021 season race, based on past racing data. 

There are a few other things I would also like to explore, as I have specified in the hypothesis above.

Another thing I am also curious about is the comparison of another machine learning algorithm to solve the same problem. Would it be worse or better off?

### Risks or limitations

This Capstone Project's goal is to be able to apply the learnings of this course to create a model using an appropriate machine learning algorithm. 

Since I am a software developer by profession, I would really like to productionise this project:

- to be able to expose the prediction functionality through an API, or if possible the ability to infer the predictions with out needing an internet connection (inferring in the client)

- to be able to show the functionality through a website or a mobile app

- to be able to create a data pipeline so that when the new results are ready (there are races all thoughout the year), the system can collect the latest race data and update the model to be used for future predictions. 

## Dataset

[Ergast Motor Racing](http://ergast.com/mrd/) has been publishing these Formula 1 results from 1950 up to the present. Majority of my data set will be from this API. 

I will also be scraping some data from the following sites:
- [Chicane F1](https://chicanef1.com/) - Since 1997 this website has been publishing F1 Race statistics and may have some data that is missing in the Ergast API
- [Wikipedia](https://en.wikipedia.org/) - Weather information is missing in the Ergast data set and this can be scraped from Wikipedia
- [World Weather Online](https://www.worldweatheronline.com/) - some weather information is also missing from Wikipedia, so we can use WWO as a backup
- [F1 Metrics](https://f1metrics.wordpress.com/) - We are not really using any dataset from F1 Metrics, however, the author of this blog had so many past predictions and analysis, that I felt it important to consider his domain knowledge as I develop the machine learning models in this project. It is a shame that his blog updates are few and far between, however when he does, it's gold. 

