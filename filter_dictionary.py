# define the filter dictionary
# the keys are the subcomponents of GDP, in 2 aspects: 1)4 components of GDP, and 2)essential industries.
# the values are the lists of keywords: the most relevant single-word keywords that cooccur with the concept of that GDP subcomponent

filter_dic = {
    'consumption': ['consume','consumer','consumption','purchase','purchasing','purchases','buyer',\
                   'durable','non-durable','housing','spending','household','inflation','retail','inflation',\
                    'income','services','prices','lifestyle','growth','cpi'],
    'expenditure': ['expenditures','expenditure','fiscal','spending','subsidies','subsidy','budget',\
                    'deficit','taxes','tax','stimulus','debt','infrastructure','earmarks','earmark',\
                    'military','healthcare','education'],
    'trade': ['trade','imports','import','exports','import','tariffs','tariff','currency','shipping','commodities',\
              'commodity','foreign','balance','global'],
    'investment':['investment','investments','stock','stocks', 'capital','funding','venture','equity','startups',\
                  'startup','entrepreneurship','entrepreneur','acquisitions','acquisition','IPO','nationalization'],
    'employment': ['job','jobs','jobless','employment','unemployment','workforce','hiring','wage','income','benefits',\
                   'salary','salaries','skills','training','layoffs','worker','workers','strikes','strike'],
    'manufacturing': ['manufacture','manufacturer','manufacturing','production','factory','equipment','machinery',\
                      'automation','assembly','output','engineering'],
    'oil_gas': ['petroleum','energy','exploration','reserves','refinery','opec','drilling','gasoline','crude',\
                  'pipeline','fuel','oil','gas'],
    'construction': ['infrastructure','estate','urbanization','skyscrapers','skyscraper','engineering',\
                     'contractors','contractor'],
    'finance': ['banking','banks','capital','stocks','stock','bonds','insurance','fintech','asset','shares'],
    'tourism': ['travel','traveling','hospitality','tourists','destination','leisure','entertainment','hotels','hotel'\
                'attractions','events'],
    'transportation': ['transportation','logistics','shipping','port','ports','aviation','airlines','airline',\
                       'cargo','freight'],
    'real estate': ['housing','property', 'estate'],
    'ICT': ['digital','telecommunications','internet','software','cybersecurity','e-commerce','technology','data',\
            'telecom','cloud','intelligence','artificial']
    }
