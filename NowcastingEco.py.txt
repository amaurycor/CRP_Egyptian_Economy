import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from datetime import datetime
from scipy.stats import pearsonr

class NowcastingEco:

    def __init__(self,df):
        self.country_filter = []
        self.theme_filter = []
        self.df = df
        self.country = 0

    #################
    ### Cleaning part
    #################
    def set_country_filter(self):
        option = input("Choose a theme filter option (Egypt, UAE, or KSA): ")
        if option == 'Egypt':
            self.country = 'Egypt'
            self.country_filter = ['Egypt', 'Egyptian', 'Cairo', 'Alexandria', 'Egyptians']
        elif option == 'UAE':
            self.country = 'UAE'
            self.country_filter = ['United Arab Emirates', 'Dubai']
        elif option == 'KSA':
            self.country = 'KSA'
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
        filtered_words = [word for word in final_str if word in self.country_filter]
        ratio = len(filtered_words) / len(final_str)
        return filtered_words if ratio >= 0.3 else 0
        
    def convert_into_list(self,string):
        list_ = list(string.split(","))
        list_ = [eval(i) for i in list_] # to get a float list
        return list_

    def clean_data(self):

        self.set_country_filter()

        self.df['cleaned_locations'] = self.df['enhancedlocations'].apply(lambda x: self._country_filtering(x))

        self.df = self.df[ (self.df['cleaned_locations'] != 0)]

        self.df.date = self.df.date.apply(lambda x: datetime.strptime(str(int(x)), '%Y%m%d%H%M%S'))

        self.df.tone = self.df.tone.apply(lambda x: self.convert_into_list(x))

        self.df['cleaned_url'] = self.df['documentidentifier'].apply(lambda x: self.title_url(x))

        self.df['cleaned_themes'] = self.df['enhancedthemes'].apply(lambda x: self.headlines_cleaning(x))

        self.df.drop(columns=['enhancedlocations', 'documentidentifier', 'enhancedthemes'], inplace=True)

        self.df = self.df

        return self.df

    #############
    ### Tone part
    #############
    def _theme_filtering(self):   

        """
        TO DO:
        - Add regex
        - Adapt the filtering column rules
        - Revise the filters lists and keywords
        """

        df = self.df # to make it iterable

        theme = input('Choose a theme filter option "CONSUMPTION", "TRADE", "EMPLOYMENT": ')

        if theme == 'CONSUMPTION':
            theme_filter = ['CONSUMPTION','CONSUME','CONSUMER','PURCHASE','PURCHASING','PURCHASER','BUYER', 'RECESSION', 'INFLATION', 'GROWTH']
            df = df[df['cleaned_themes'].apply(lambda x: any(keyword in x for keyword in theme_filter)) ] #and self.df['cleaned_url'].apply(lambda x: any(keyword in x for keyword in theme_filter))]

        elif theme == 'TRADE':
            theme_filter = ['TRADE','MARKET', 'EXPORTS', 'IMPORTS', 'PAYMENTS', 'DEFICIT', 'BALANCE', 'DEBT', 'BORROWING', 'SPENDING'] # don't find these two keywords in the title
            df = df[df['cleaned_themes'].apply(lambda x: any(keyword in x for keyword in theme_filter)) ] #and self.df['cleaned_url'].apply(lambda x: any(keyword in x for keyword in filter))]

        elif theme == 'EMPLOYMENT':
            theme_filter = ['EMPLOYMENT','UNEMPLOYMENT', 'LAYOFFS', 'SALARY', 'LABOR', 'STRIKES', 'UNIONS', 'WORKERS']
            df = df[df['cleaned_themes'].apply(lambda x: any(keyword in x for keyword in theme_filter)) ] #and self.df['cleaned_url'].apply(lambda x: any(keyword in x for keyword in theme_filter))]
        
        else:
            print('ERROR Invalid input')
            self.set_country_filter()   

        self.df = df

        return self.df # filtered dataframe containing only data related to the corresponding theme

    def read_country_data(self):
        
        """
        TO DO:
        - Add path to the indicators data of each country
        (for now it will be local path)
        """

        if self.country == 'Egypt':
            path = '/Users/amaury/Documents/!DSBA/CRP/Bloomberg_Data_Egypt.xlsx'
        elif self.country == 'KSA':
            path = 'x'
        elif self.country =='UAE':
            path = 'x'
        else:
            print('COUNTRY ERROR')

        option = input("Choose your indicator: 'GDP','CPI','Foreign Invests' ,'Exports','Imports','Private Consumption','Government Exp','Country Invests'")

        if option == 'GDP': data = pd.read_excel(path, sheet_name='GDP',usecols=[0,1])
        elif option == 'CPI': data = pd.read_excel(path, sheet_name='CPI',usecols=[0,1])
        elif option == 'Foreign Invests' :data = pd.read_excel(path, sheet_name='Foreign Invests',usecols=[0,1])
        elif option =='Exports': data = pd.read_excel(path, sheet_name='Exports',usecols=[0,1])
        elif option =='Imports': data = pd.read_excel(path, sheet_name='Imports',usecols=[0,1])
        elif option =='Private Consumption': data = pd.read_excel(path, sheet_name='Private Consumption',usecols=[0,1])
        elif option =='Government Exp': data = pd.read_excel(path, sheet_name='Government Exp',usecols=[0,1])
        elif option =='Country Invests - pred': data = pd.read_excel(path, sheet_name='Egypt Invests - pred',usecols=[0,1])
        
        else:
            print("Invalid option. Please choose between: 'GDP','CPI','Foreign Invests' ,'Exports','Imports','Private Consumption','Government Exp','Country Invests'")
            self.read_country_data()

        # Conversion of the date format
        data.Date = data.Date.apply(lambda x: datetime.strptime(str(x), '%m/%d/%y'))  
        data = data.groupby(data.Date.dt.year)['Value'].mean()
        #print(data)
        return data, option

    def tone_analysis(self,indicator=None): # The idea is to visualize the reference indicator over the 'tone', add in the future CPI etc.
        
        """
        TO DO:
        - Computation of the correlation between indicator and the tone curves => DONE
        """

        self.df = self._theme_filtering()

        if indicator:
            ind, name_ind = self.read_country_data()

        # Defining new column related to tone
        self.df['mean_tone'] = self.df.tone.apply(lambda x: x[0])
        self.df['binary_tone'] = self.df.tone.apply(lambda x: 1 if x[1] > x[2] else 0)
        boxplot_df = self.df.groupby(self.df.date.dt.year)

        # Count the filtered number of articles per year
        nb_articles = self.df.groupby(self.df.date.dt.year)['cleaned_themes'].count()
        # Average of the tone of articles per year
        avg_tone = self.df.groupby(self.df.date.dt.year)['mean_tone'].mean()
        #print(avg_tone)
        # Ratio of pos and neg tone of articles per year
        ratio_tone = self.df.groupby(self.df.date.dt.year)['binary_tone'].mean()

        ### Plotting ###
        fig , (ax1,ax2,ax3) = plt.subplots(nrows=3, ncols=1, figsize=(8, 12))
        
        # First graph
        # plot the data
        ax1.plot(avg_tone.loc[:2022],'r',label='Average tones')
        ax1.axhline(avg_tone.loc[:2022].mean(), color='red', linestyle='--', label='Mean of average tones')
        # plot gdp if wanted
        if indicator:
            ax1_twin = ax1.twinx()
            ax1_twin.plot(ind,color='b',label=str(name_ind))
            #ax1_twin.set_ylabel('Dollars')
            
        # set axis labels and title
        ax1.set_xlabel('date')
        ax1.set_ylabel('Tone')

        #Compute the pearson correlation 
        # => need the indicator to have more data (or equal) than avg_tone that starts in 2015
        #{\displaystyle \rho _{X,Y}={\frac {\operatorname {cov} (X,Y)}{\sigma _{X}\sigma _{Y}}}}
        if len(ind) > len(avg_tone.loc[:2022]):
            corr_1, _ = pearsonr(avg_tone.loc[:2022], ind.loc[2015:2022])
            print(f"The correlation between the average tones and the {name_ind} from 2015 is: {corr_1}.")

        ax1.legend()
        ax1.set_title(f'Evolution of the average tone and {name_ind} throughout the years ')

        # Second graph
        ax2.plot(ratio_tone.loc[:2022],'g',label=' % positive articles')
        ax2.axhline(ratio_tone.loc[:2022].mean(), color='green', linestyle='--', label='Mean %')
        if indicator:
            ax2_twin = ax2.twinx()
            ax2_twin.plot(ind,color='b',label=str(name_ind))
            #ax2_twin.set_ylabel('Dollars')

        ax2.set_xlabel('date')
        ax2.set_ylabel('Percentage of articles')

        if len(ind) > len(ratio_tone.loc[:2022]):
            corr_2, _ = pearsonr(ratio_tone.loc[:2022], ind.loc[2015:2022])
            print(f"The correlation between the positive article ratio and the {name_ind} from 2015 is: {corr_2}.")

        ax2.legend()
        ax2.set_title(f'Evolution of the positive toned articles ratio and {name_ind} throughout the years ')

        # Third graph - boxplots
        for name, group in boxplot_df:
            ax3.boxplot(group['mean_tone'], positions=[name])
        ax3.set_xticklabels(boxplot_df.groups.keys())
        ax3.set_xlabel('date')
        ax3.set_ylabel('Tone')
        ax3.set_title('Box plots of the tone averages')

        plt.tight_layout()
        plt.show()

        print('Number of articles per year for the filtered country and theme: ',nb_articles)
