# CRP_Nowcasting_Economy

1. NowcastingEco.py file contains a class which allows to:
- Clean and preprocess the headlines data from the media
- Basic tone analysis: filter and analyze the tones of articles for a specific theme and country (and compute correlation with an indicator if selected)
- [To facilitate the 'advanced modeling']: Generate and return the 14 filtered tone times series and indicator time series


2. To use, you can use the run_pipeline.ipynb file. 
This notebook also allows to use the more advanced modelling. This modeling takes mutliple filtered tone time series as inputs (among the 14 filters) and fit/predict with OLS (with L1 and L2 regularization) in order to nowcast an indicator. 
Note: Train from 2015 to 2019 and test from 2020 to 2022.

In this repository, you can also find independant analysis among the following notebooks:
- GDP_correlations_&_seasonality_analysis.ipynb:
   - Correlations between sub-components of the GDP and the GDP itself
   - Study of the seasonality of each of theses indicators
     
- NLP_models.ipynb:
  - Training and testing of 3 different NLP techniques in order to better estimate the tone of our news data 
