import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from datetime import datetime
from scipy.stats import pearsonr
import re
from filter_dictionary import filter_dic

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
        
    def extract_title(self,xml_string):
        try:
            title = re.findall('<PAGE_TITLE>(.*?)</PAGE_TITLE>', xml_string)[0]
        except:
            title = 'NA'
        return title
        
    def xml_cleaning(self, sentence):
        sentence = str(sentence)
        words = [elem.upper() for elem in sentence.split(' ')]
        return words

    def clean_data(self):

        self.set_country_filter()
        
        self.df['xml_headline'] = self.df['extrasxml'].apply(lambda x: self.extract_title(x))

        self.df['cleaned_xml'] = self.df['xml_headline'].apply(lambda x: self.xml_cleaning(x))

        self.df['cleaned_locations'] = self.df['enhancedlocations'].apply(lambda x: self._country_filtering(x))

        self.df = self.df[ (self.df['cleaned_locations'] != 0)]

        self.df.date = self.df.date.apply(lambda x: datetime.strptime(str(int(x)), '%Y%m%d%H%M%S'))

        self.df.tone = self.df.tone.apply(lambda x: self.convert_into_list(x))

        self.df['cleaned_url'] = self.df['documentidentifier'].apply(lambda x: self.title_url(x))

        self.df['old_themes'] = self.df['enhancedthemes'].apply(lambda x: self.headlines_cleaning(x))

        self.df['cleaned_themes'] = self.df.apply(lambda x: x['old_themes'] + x['cleaned_url'] if x['cleaned_xml'] == ['na'] else x['old_themes'] + x['cleaned_xml'], axis=1)

        self.df['cleaned_themes'] = self.df['cleaned_themes'].apply(lambda x: [s.upper() for s in x])

        self.df.drop(columns=['enhancedlocations', 'documentidentifier', 'enhancedthemes' , 'extrasxml' , 'xml_headline', 'cleaned_url' , 'cleaned_xml' , 'old_themes'], inplace=True)

        self.df = self.df

        return self.df

    #############
    ### Tone part
    #############

    def _theme_filtering(self):   

        """
        TO DO:
        - Add regex => DONE
        - Adapt the filtering column rules => DONE
        - Revise the filters lists and keywords => DONE
        """

        df = self.df # to make it iterable

        theme = input('Choose a theme filter option:' + str(list(filter_dic.keys())) )

        while theme.lower() not in map(str.lower, filter_dic):
            print('ERROR Invalid input')
            theme = input('Choose a theme filter option:' + str(list(filter_dic.keys())) )
            #self._theme_filtering()

        if theme.lower() in map(str.lower, filter_dic):
            theme_filter = filter_dic[theme.lower()]
            df2 = df[df['cleaned_themes'].apply(lambda x: any(keyword.upper() in x for keyword in theme_filter)) ] #and self.df['cleaned_url'].apply(lambda x: any(keyword in x for keyword in theme_filter))]         

            return df2 # filtered dataframe containing only data related to the corresponding theme




    def read_country_data(self,path):
        
        """
        TO DO:
        - Add path to the indicators data of each country => DONE
        (for now it will be local path)
        """

        sheet_names = pd.ExcelFile(path).sheet_names[1:]
 
        option = input("Choose your indicator:" + str(sheet_names))

        while option not in sheet_names:
            print("Invalid option. Please choose between: " + str(sheet_names))
            option = input("Choose your indicator:" + str(sheet_names))

        if option in sheet_names: 
            data = pd.read_excel(path, sheet_name=str(option),usecols=[0,1])
            
            # Create a column with year+month and just the year
            data['year_month'] = data['Date'].dt.to_period('M')

            data['year'] = data['Date'].dt.to_period('2Y')
            data['year'] = data['year'].dt.year

            
            ## To check the indicator frequency
            data.set_index('Date', inplace=True)
            freq_estimate = (data.index[0] - data.index[1]).days

            # Check if the time difference is consistent with a monthly frequency
            if freq_estimate > 27 and freq_estimate < 32: # if greater than 27 and samller than 32 => monthly freq
                freq = 'M'
            elif freq_estimate > 89 and freq_estimate < 93: # quarterly freq
                freq = 'Q'
            else:
                freq = 'Y' # otherwise it's yearly

            return data, option, freq
  

    def tone_analysis(self,path,indicator=None): # The idea is to visualize the reference indicator over the 'tone', add in the future CPI etc.
        
        """
        TO DO:
        - Computation of the correlation between indicator and the tone curves => DONE
        """
        # Filtering tone data according to selected filter
        df2 = self._theme_filtering()

        # Set the date as index for the news data
        df2.set_index('date', inplace=True)
        
        if indicator:
            ind, name_ind, freq = self.read_country_data(path)
            
        # Defining new column related to tone
        df2['mean_tone'] = df2.tone.apply(lambda x: x[0])
        df2['binary_tone'] = df2.tone.apply(lambda x: 1 if x[1] > x[2] else 0)
        boxplot_df = df2.groupby(df2.index.year)

        # Count the filtered number of articles per year
        nb_articles = df2.resample(freq,convention='end')['cleaned_themes'].count()
        # Average of the tone of articles per year
        avg_tone = df2.resample(freq,convention='end')['mean_tone'].mean()
        # Ratio of pos and neg tone of articles per year
        ratio_tone = df2.resample(freq,convention='end')['binary_tone'].mean()

        ### Plotting ###
        fig , (ax1,ax2,ax3) = plt.subplots(nrows=3, ncols=1, figsize=(8, 12))
        
        # First graph
        ax1.plot(avg_tone,'r',label='Average tones')
        ax1.axhline(avg_tone.mean(), color='red', linestyle='--', label='Mean of average tones')
        
        # Plotting of the indicator + correlation computation
        if indicator:

            ax1_twin = ax1.twinx()

            # Defining the starting date according to the data freq
            ind = ind[ind.index >= '2015-02-01']
            ind.sort_index(inplace=True) # reorder to easily .loc[]

            # Plotting the indicator from the starting date
            ax1_twin.plot(ind.Value,color='b',label=str(name_ind))
            
            # Compute the pearson correlation 
            max_date_ind = ind.index.max()
            max_date_avg_tone = avg_tone.index.max()
            max_date = min(max_date_ind,max_date_avg_tone)

            # To get indicator until max date only
            print(avg_tone.loc[:max_date])
            print(ind.Value.loc[:max_date])
            corr_1, _ = pearsonr(avg_tone.loc[:max_date], ind.Value.loc[:max_date])

            print(f"The correlation between the average tones and the {name_ind} from 2015 to {max_date} is: {corr_1}.")

        # set axis labels and title
        ax1.set_xlabel('date')
        ax1.set_ylabel('Tone')
        ax1.legend()
        ax1.set_title(f'Evolution of the average tone and {name_ind} throughout the years ')


        # Second graph
        ax2.plot(ratio_tone,'g',label=' % positive articles')
        ax2.axhline(ratio_tone.mean(), color='green', linestyle='--', label='Mean %')

        if indicator:

            ax2_twin = ax2.twinx()
            
            # Plotting the indicator from the (previously computed) starting date 
            ax2_twin.plot(ind.Value,color='b',label=str(name_ind))
            
            # Compute the pearson correlation (based on the max date previously computed)
            corr_2, _ = pearsonr(ratio_tone.loc[:max_date], ind.Value.loc[:max_date])

            print(f"The correlation between the average tones and the {name_ind} from 2015 to {max_date} is: {corr_2}.")


        ax2.set_xlabel('date')
        ax2.set_ylabel('Percentage of articles')
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


    def compute_tone_time_series(self,path):
        """
        """
        tone_time_series = []
        # Load the indicator to get its frequency and adapt the frequency of the tone time series
        ind, _, freq = self.read_country_data(path)

        for theme in map(str.lower, filter_dic):

            # Filtering tone data according to selected filter
            theme_filter = filter_dic[theme.lower()]
            df3 = self.df[self.df['cleaned_themes'].apply(lambda x: any(keyword.upper() in x for keyword in theme_filter)) ]       

            # Set the date as index for the news data
            df3.set_index('date', inplace=True)

            # Transform the new tone comptued with NLP model into a binary : 1 for positive and 0 for negative
            df3['binary_tone'] = df3.new_tone.apply(lambda x: 1 if x == "positive" else 0)

            # Ratio of pos and neg tone of articles per year =>
            ratio_tone = df3.resample(freq,convention='end')['binary_tone'].mean()

            tone_time_series.append(ratio_tone)

        # Loading the indicator time series
        ind = ind[ind.index >= '2015-02-01']
        ind.sort_index(inplace=True) 
        indicator_time_series = ind

        return (tone_time_series,indicator_time_series)

    