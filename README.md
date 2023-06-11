# CRP_Nowcasting_Economy

1. NowcastingEco.py file containsa class which allows to:
- clean and preprocess the headlines data from the media
- filter and analyze the tones of articles for a specific theme and country
- compare the tone series it to a reference indicator and compute the correlation

2. To use, you can use the run_pipeline.ipynb file. This notebook also allows to use the more advanced modelling with linear regression (taking multiple tone series as input in order to model an indicator).

In this repository, you can also find independant analysis such as:
- Correlations between sub-components of the GDP and the GDP itself
- Study of the seasonality of each of theses indicators
- Training and testing of NLP models in order to better estimate the tone of our news data 
