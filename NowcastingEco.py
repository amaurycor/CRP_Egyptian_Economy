import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import urlparse

class NowcastingEco:

    def __init__(self,df):
        self.country_filter = []
        self.df = df

    def set_country_filter(self):
        option = input("Choose a theme filter option (Egypt, UAE, or KSA): ")
        if option == 'Egypt':
            self.country_filter = ['Egypt', 'Egyptian', 'Cairo', 'Alexandria', 'Egyptians']
        elif option == 'UAE':
            self.country_filter = ['United Arab Emirates', 'Dubai']
        elif option == 'KSA':
            self.country_filter = ['Saudi Arabia', 'Riyadh']
        else:
            print("Invalid option. Please choose Egypt, UAE, or KSA.")
            self.set_country_filter()

    def headlines_cleaning(self, s_):
        s_ = str(s_)
        modified_str = [elem.split(',')[0] for elem in s_.split(';')] # delete the number after the coma

        final_str=[]
        separator=' '
        for s in modified_str:
            if s.split('_')[0]=='WB':
                final_str.append(separator.join(s.split('_')[2:]).split(' ')) # delete the prefix 'WB_XXX', remove underscore and split each word
            else:
                final_str.append(separator.join(s.split('_')).split(' '))

    # to get a list of words and not a list of sub lists
        merged_list = []
        for sublist in final_str:
            merged_list.extend(sublist)
        return(merged_list) 
    
    def title_url(self, url):
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.split('/')
        desired_string = [elem.split('-') for elem in path_segments]
        merged_list = [item for sublist in desired_string[-2:] for item in sublist if item.isalpha()]
        return (merged_list)

    def _country_filtering(self,s_): # optimized
        s_ = str(s_)
        modified_str = [elem.split('#')[1] for elem in s_.split(';')]
        final_str = [elem.split(', ')[-1] for elem in modified_str]
        filtered_words = set(final_str).intersection(self.country_filter)
        ratio = len(filtered_words) / len(final_str)
        return filtered_words if ratio >= 0.3 else 0
        

    def clean_data(self):

        self.set_country_filter()

        self.df['cleaned_locations'] = self.df['enhancedlocations'].apply(lambda x: self._country_filtering(x))

        self.df = self.df[ (self.df['cleaned_locations'] != 0)]

        self.df['cleaned_url'] = self.df['documentidentifier'].apply(lambda x: self.title_url(x))

        self.df['cleaned_themes'] = self.df['enhancedthemes'].apply(lambda x: self.headlines_cleaning(x))

        self.df.drop(columns=['enhancedlocations', 'documentidentifier', 'enhancedthemes'], inplace=True)

        return self.df


    ###   
    def _theme_filtering(self):

        theme = input('Choose a theme filter option "CONSUMPTION", "TRADE", "EMPLOYMENT": ')

        if theme == 'CONSUMPTION':
            filter = ['CONSUMPTION','CONSUME','CONSUMER','PURCHASE','PURCHASING','PURCHASER','BUYER']
            self.df = self.df[self.df['cleaned_themes'].apply(lambda x: any(keyword in x for keyword in filter)) and self.df['cleaned_url'].apply(lambda x: any(keyword in x for keyword in filter))]

        elif theme == 'TRADE':
            filter = ['TRADE','MARKET']
            self.df = self.df[self.df['cleaned_themes','cleaned_url'].apply(lambda x: any(keyword in x for keyword in filter)) and self.df['cleaned_url'].apply(lambda x: any(keyword in x for keyword in filter))]

        elif theme == 'EMPLOYMENT':
            filter = ['EMPLOYMENT','UNEMPLOYMENT']
            self.df = self.df[self.df['cleaned_themes'].apply(lambda x: any(keyword in x for keyword in filter)) and self.df['cleaned_url'].apply(lambda x: any(keyword in x for keyword in filter))]
        
        else:
            print('ERROR Invalid input')
            self.set_country_filter()

        return self.df # filtered dataframe containing only data related to the corresponding theme
    

    def tone_analysis(self,gdp=None): # The idea is to visualize the reference indicator over the 'tone', add in the future CPI etc.

        self.df = self._theme_filtering()

        if gdp:
            gdp = {'date':[2015,2016,2017,2018,2019,2020,2021],'gdp_per_capita':[3370.382447,3331.612461,2315.896627,2407.086543,2869.576588,3398.801432,3698.834981]}
            df_gdp = pd.DataFrame(data = gdp)
        else:
            print("You didn't select a reference indicator to plot.")

        # Defining new column related to tone
        self.df['mean_tone'] = self.df.tone.apply(lambda x: x[0])
        self.df['binary_tone'] = self.df.tone.apply(lambda x: 1 if x[1] > x[2] else 0)
        boxplot_df = self.df.groupby(self.df.date.dt.year)['mean_tone']

        # Count the filtered number of articles per year
        nb_articles = self.df.groupby(self.df.date.dt.year)['enhancedthemes'].count()
        # Average of the tone of articles per year
        avg_tone = self.df.groupby(self.df.date.dt.year)['mean_tone'].mean()
        # Ratio of pos and neg tone of articles per year
        ratio_tone = self.df.groupby(self.df.date.dt.year)['binary_tone'].mean()

        ### Plotting ###
        fig , (ax,bx,cx) = plt.subplots(3)
        
        # First graph
        # plot the data
        ax.plot(avg_tone.loc[:2021])
        ax.axhline(avg_tone.loc[:2021].mean(), color='red', linestyle='--', label='Average tone')
        # plot gdp if wanted
        if gdp:
            ax2 = ax.twinx()
            ax.plot(df_gdp.date,df_gdp.gdp_per_capita)
            ax2.ylabel('GDP per capita')
            
        # set axis labels and title
        ax.xlabel('date')
        ax.ylabel('Average Tone')
        ax.legend()
        ax.set_title('Comparison between the evolution of tone and GDP per capita throughout the years ')

        # Second graph
        bx.plot(ratio_tone.loc[:2021])
        bx.axhline(ratio_tone.loc[:2021].mean(), color='green', linestyle='--', label='Average %')
        if gdp:
            bx2 = ax.twinx()
            bx2.plot(df_gdp.date,df_gdp.gdp_per_capita)
            bx2.ylabel('GDP per capita')

        bx.xlabel('date')
        bx.ylabel('Percentage of positive tone articles')
        bx.legend()
        bx.set_title('Comparison between the evolution of the percentage of positive tone articles and GDP per capita throughout the years ')

        # Third graph - boxplots
        for name, group in boxplot_df:
            cx.boxplot(group['valeurs'], positions=[name])
        cx.set_xticklabels(boxplot_df.groups.keys())
        cx.xlabel('date')
        cx.ylabel('Average tone')
        cx.set_title('Box plots of tone averages')

        plt.show()

        print('Number of articles per year for the filtered country and theme: ',nb_articles)

        return self.df