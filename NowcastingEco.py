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
        - Add regex
        - Adapt the filtering column rules
        - Revise the filters lists and keywords
        """

        df = self.df # to make it iterable

        theme = input('Choose a theme filter option:' + str(list(filter_dic.keys())) )

        if theme.lower() in map(str.lower, filter_dic):
            theme_filter = filter_dic[theme.lower()]
            df = df[df['cleaned_themes'].apply(lambda x: any(keyword.upper() in x for keyword in theme_filter)) ] #and self.df['cleaned_url'].apply(lambda x: any(keyword in x for keyword in theme_filter))]
    
        else:
            print('ERROR Invalid input')
            self._theme_filtering()   
            return None
        
        self.df = df
        return self.df # filtered dataframe containing only data related to the corresponding theme

    def read_country_data(self,path):
        
        """
        TO DO:
        - Add path to the indicators data of each country
        (for now it will be local path)
        """

        sheet_names = pd.ExcelFile(path).sheet_names
 
        option = input("Choose your indicator:" + str(sheet_names))

        if option in sheet_names: data = pd.read_excel(path, sheet_name=str(option),usecols=[0,1])

        else:
            print("Invalid option. Please choose between: " + str(sheet_names))

            self.read_country_data(path)
            return None
        
        # Conversion of the date format
        #data.Date = data.Date.apply(lambda x: datetime.strptime(str(x), '%d/%m/%Y'))  
        data = data.groupby(data.Date.dt.year)['Value'].mean()

        return data, option

    def tone_analysis(self,path,indicator=None): # The idea is to visualize the reference indicator over the 'tone', add in the future CPI etc.
        
        """
        TO DO:
        - Computation of the correlation between indicator and the tone curves => DONE
        """

        self.df = self._theme_filtering()

        if indicator:
            ind, name_ind = self.read_country_data(path)

        # Defining new column related to tone
        self.df['mean_tone'] = self.df.tone.apply(lambda x: x[0])
        self.df['binary_tone'] = self.df.tone.apply(lambda x: 1 if x[1] > x[2] else 0)
        boxplot_df = self.df.groupby(self.df.date.dt.year)

        # Count the filtered number of articles per year
        nb_articles = self.df.groupby(self.df.date.dt.year)['cleaned_themes'].count()
        # Average of the tone of articles per year
        avg_tone = self.df.groupby(self.df.date.dt.year)['mean_tone'].mean()
        # Ratio of pos and neg tone of articles per year
        ratio_tone = self.df.groupby(self.df.date.dt.year)['binary_tone'].mean()

        ### Plotting ###
        fig , (ax1,ax2,ax3) = plt.subplots(nrows=3, ncols=1, figsize=(8, 12))
        
        # First graph
        ax1.plot(avg_tone,'r',label='Average tones')
        ax1.axhline(avg_tone.mean(), color='red', linestyle='--', label='Mean of average tones')
        # plot the indicator if wanted (from 2015 to match the start of headlines data)
        if indicator:
            ax1_twin = ax1.twinx()
            ax1_twin.plot(ind.loc[2015:],color='b',label=str(name_ind))
            #ax1_twin.set_ylabel('Dollars')
            
        # set axis labels and title
        ax1.set_xlabel('date')
        ax1.set_ylabel('Tone')

        #Compute the pearson correlation 
        # => need the indicator to have more data (or equal) than avg_tone that starts in 2015
        #{\displaystyle \rho _{X,Y}={\frac {\operatorname {cov} (X,Y)}{\sigma _{X}\sigma _{Y}}}}
        if indicator:
            max_date_ind = ind.index.max()
            max_date_avg_tone = avg_tone.index.max()
            max_date = min(max_date_avg_tone,max_date_ind)
            #if len(ind) > len(avg_tone.loc[:max_date]):
            corr_1, _ = pearsonr(avg_tone.loc[:max_date], ind.loc[2015:max_date])
            print(f"The correlation between the average tones and the {name_ind} from 2015 to {max_date} is: {corr_1}.")

        ax1.legend()
        ax1.set_title(f'Evolution of the average tone and {name_ind} throughout the years ')

        # Second graph
        ax2.plot(ratio_tone,'g',label=' % positive articles')
        ax2.axhline(ratio_tone.mean(), color='green', linestyle='--', label='Mean %')
        if indicator:
            ax2_twin = ax2.twinx()
            ax2_twin.plot(ind.loc[2015:],color='b',label=str(name_ind))
            #ax2_twin.set_ylabel('Dollars')

        ax2.set_xlabel('date')
        ax2.set_ylabel('Percentage of articles')

        if indicator:
            # Compute the max date of the indicator and the headlines to have the same length and compute the correlation
            max_date_ind = ind.index.max()
            max_date_ratio_tone = avg_tone.index.max()
            max_date = min(max_date_ratio_tone,max_date_ind)
            #if len(ind) > len(ratio_tone.loc[:max_date]):
            corr_2, _ = pearsonr(ratio_tone.loc[:max_date], ind.loc[2015:max_date])
            print(f"The correlation between the positive article ratio and the {name_ind} from 2015 to {max_date} is: {corr_2}.")

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
