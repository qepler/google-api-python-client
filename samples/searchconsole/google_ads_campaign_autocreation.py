
# coding: utf-8
# Duplicate and adapt GEN Campaign model into a same account

# In[1]:

### EXTERNAL SERVICES LAUNCH ###

import datetime
from googleads import adwords
import pandas as pd
import numpy as np


# In[2]:


### INPUT ###

campaign_name = 'Galaxy S7'  # hard input needed
brand = 'samsung' # hard input needed
category = 'smartphone' # Either 'smartphone' or 'other'
country = 'Spain' #hard input


# In[3]:


model_exact = campaign_name.lower() # to be derived from campaign_name
model_broad = model_exact.replace(' ', ' +') # to be derived from campaign_name (if more than 1 word: +in front of every word)


# In[4]:


### YAML FILE ###

def yaml(country):
    
    if country == 'Germany':
        
        client = adwords.AdWordsClient.LoadFromStorage('googleads_germany.yaml')
        
    elif country == 'Spain':
        
        client = adwords.AdWordsClient.LoadFromStorage('googleads_spain.yaml')
        
    elif country == 'France':
        
        client = adwords.AdWordsClient.LoadFromStorage('googleads_france.yaml')
        
    elif country == 'Tests':
        
        client = adwords.AdWordsClient.LoadFromStorage('googleads_tests.yaml')
        
    elif country == 'Italy':
        
        client = adwords.AdWordsClient.LoadFromStorage('googleads_italy.yaml')
        
    elif country == 'Belgium':
        
        client = adwords.AdWordsClient.LoadFromStorage('googleads_belgium.yaml')
        
    return client
        
client = yaml(country)


# In[5]:


### ADVERTISER CHOICE ###

def account(country):
    
    if country == 'Germany':
        
        account = {'BM_Germany_Germany':'391-081-0008'}
        
    elif country == 'Spain':
        
        account = {'BM_Spain_Spain':'880-433-3516'}
        
    elif country == 'France':
        
        account = {'BM_France_France':'954-929-8993'}
        
    elif country == 'Italy':
        
        account = {'BM_Italy_Italy':'823-274-0570'}
        
    elif country == 'Belgium':
        
        account = {'BM_Belgium_Belgium':'294-063-5541'}
        
    elif country == 'Tests':
        
        account = {'BM_Tests_Tests':'319-671-4142'}
        
    return account

account = account(country)
# In[]
print(account)

# In[6]:


### ADVERTISER CHOICE ###

def domain(country):
    
    if country == 'Germany':
        
        domain = 'www.backmarket.de'
        
    elif country == 'Spain':
        
        domain = 'www.backmarket.es'
        
    elif country == 'France':
        
        domain = 'www.backmarket.fr'
        
    elif country == 'Italy':
        
        domain = 'www.backmarket.it'
        
    elif country == 'Belgium':
        
        domain = 'www.backmarket.be'
        
    elif country == 'Tests':
        
        domain = 'www.backmarket.de'
        
    return domain

domain = domain(country)


# In[7]:


### ADVERTISER CHOICE ###

def language(country):
    
    if country == 'Germany':
        
        language = 'de'
        
    elif country == 'Spain':
        
        language = 'es'
        
    elif country == 'France':
        
        language = 'fr'
        
    elif country == 'Italy':
        
        language = 'it'
        
    elif country == 'Belgium':
        
        language = 'fr'
        
    elif country == 'Tests':
        
        language = 'de'
        
    return language

language = language(country)


# In[8]:


### CREATE DEDICATED BUDGET ### - NOT NECESSARY USEFUL

budget_service = client.GetService('BudgetService', version='v201809')

budget = {'name': 'new_budget_new_'+model_exact,
          'amount': 
          {'microAmount': '1000000000'},
          'deliveryMethod': 'STANDARD'
         }

budget_operations = [{'operator': 'ADD',
                      'operand': budget
                     }]

budget_id = budget_service.mutate(budget_operations)['value'][0]['budgetId']


# In[9]:


### GET LATEST SIMILAR CAMPAIGN ###

campaigns_ids_names = []

model = model_exact.split(' ', 1)[0]
model_1 = model_exact.split(' ', 2)[1]
try :
    model_2 = model_exact.split(' ', 2)[2]
except:
    model_2 = model

campaign_service = client.GetService('CampaignService', version='v201809')

# Construct selector and get all campaigns.

selector = {
    'fields': ['Id', 'Name', 'Status', 'StartDate', 'BiddingStrategyId', 'BiddingStrategyType'],
    'predicates' : {
        'field' : 'Status',
        'operator' : 'EQUALS',
        'values' : ['ENABLED']
    }
}


page = campaign_service.get(selector)

for i in page['entries']:
    campaigns_ids_names.append({
        'CAMPAIGN_ID' : i['id'],
        'CAMPAIGN_NAME' : i['name'],
        'CAMPAIGN_STARTDATE' : i['startDate'],
        'BID_STRAT_ID' : i['biddingStrategyConfiguration']['biddingStrategyId'],
        'BID_STRAT_TYPE' : i['biddingStrategyConfiguration']['biddingStrategyType']
    })

campaign_results = pd.DataFrame(campaigns_ids_names)


# In[10]:


### GET CAMPAIGN PERF ###

report_downloader = client.GetReportDownloader(version='v201809')
    
advertisers = account # make it variable given "country"
    
report = {
    'reportName': 'CAMPAIGN_PERFORMANCE_REPORT',
    'dateRangeType': 'LAST_7_DAYS',
    'reportType': 'CAMPAIGN_PERFORMANCE_REPORT',
    'downloadFormat': 'CSV',
    'selector': {
        'fields': ['CampaignId', 'CampaignName', 'Clicks'],
        
    }
}
    
# Print out the report as a string
for __ , key in enumerate(advertisers):
    path = "campaign_perf_"+ country +".csv"
    print('Report for the account {} is being loaded in the local file {} \n'.format(advertisers[key], path))
    
    with open(path,"wb") as fn:
        report_downloader.DownloadReport(report, 
                                         fn ,
                                         client_customer_id=advertisers[key],
                                         skip_report_header=True, 
                                         skip_column_header=False,
                                         skip_report_summary=True, 
                                         include_zero_impressions=True)
        fn.close()


# In[11]:


campaign_perf = pd.read_csv("campaign_perf_"+ country +".csv")
campaign_perf = campaign_perf.rename(columns={'Campaign ID' : 'CAMPAIGN_ID', 'Campaign' : 'CAMPAIGN_NAME'})


# In[12]:


campaign_id = pd.merge(campaign_results, campaign_perf)


# In[13]:


campaign_id['CAMPAIGN_NAME'] = [i.replace('GEN_', '') for i in campaign_id['CAMPAIGN_NAME']]
campaign_id['CAMPAIGN_NAME'] = [i.lower() for i in campaign_id['CAMPAIGN_NAME']]
campaign_id = campaign_id[campaign_id['CAMPAIGN_NAME'].str.contains('rlsa') == False]
campaign_id = campaign_id[campaign_id['CAMPAIGN_NAME'].str.contains('clients') == False]
try:
    campaign_id = campaign_id[campaign_id['CAMPAIGN_NAME'].str.contains(model) and campaign_id['CAMPAIGN_NAME'].str.contains(model_1)]
except:
    try:
        campaign_id = campaign_id[campaign_id['CAMPAIGN_NAME'].str.contains(model)]
    except:
        if category == 'smartphone':
            campaign_id = campaign_id[campaign_id['CAMPAIGN_NAME'].str.contains('iphone 7')]
        else:
            campaign_id = campaign_id[campaign_id['CAMPAIGN_NAME']]

#campaign_id = campaign_id.reset_index()
if len(campaign_id) > 1:
    campaign_id = campaign_id.sort_values('Clicks', ascending=False).iloc[1]
else:
    campaign_id = campaign_id.sort_values('Clicks', ascending=False).iloc[0]
#latest_campaign_id = list(campaign_id['CAMPAIGN_ID'])


# In[14]:


latest_campaign_id = campaign_id['CAMPAIGN_ID']


# In[15]:


### GET ADGROUPS OF LATEST CAMPAIGN ###

# Initialize appropriate service.
ad_group_service = client.GetService('AdGroupService', version='v201809')

adgroups = []

def ad_groups():

    # Construct selector and get all ad groups.
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': latest_campaign_id
            }
        ]
    }

    page = ad_group_service.get(selector)

    for i in page['entries']:
        adgroups.append({
            'ADGROUP_ID' : i['id'],
            'ADGROUP_NAME' : i['name']
        })

        
ad_groups()
adgroups = pd.DataFrame(adgroups)


# In[16]:


test_if_ok = adgroups[(adgroups.ADGROUP_NAME.str.contains('(5)')) | (adgroups.ADGROUP_NAME.str.contains('cat.5'))]


# In[17]:


if test_if_ok.empty == True:
    campaign_results['CAMPAIGN_NAME'] = [i.replace('GEN_', '') for i in campaign_results['CAMPAIGN_NAME']]
    campaign_results['CAMPAIGN_NAME'] = [i.lower() for i in campaign_results['CAMPAIGN_NAME']]
    campaign_results = campaign_results[campaign_results['CAMPAIGN_NAME'].str.contains('rlsa') == False]
    campaign_results = campaign_results[campaign_results['CAMPAIGN_NAME'].str.contains('clients') == False]
    campaign_results = campaign_results[campaign_results['CAMPAIGN_NAME'].str.contains('troas') == True]
    if category == 'smartphone':
        campaign_results = campaign_results[campaign_results['CAMPAIGN_NAME'].str.contains('iphone 7') == True]
    else:
        campaign_results = campaign_results[campaign_results['CAMPAIGN_NAME'].str.contains('macbook') == True]
    campaign_id = campaign_results.iloc[0]
    latest_campaign_id = campaign_id['CAMPAIGN_ID']
    campaign_id['CAMPAIGN_NAME'] = 'iphone 7'
else:
    pass
    


# In[18]:


adgroups2 = []

def ad_groups_2():

    # Construct selector and get all ad groups.
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': latest_campaign_id
            }
        ]
    }

    page = ad_group_service.get(selector)

    for i in page['entries']:
        adgroups2.append({
            'ADGROUP_ID' : i['id'],
            'ADGROUP_NAME' : i['name']
        })

        
ad_groups_2()
adgroups = pd.DataFrame(adgroups2)
adgroups_ids = list(adgroups['ADGROUP_ID'])


# In[19]:


bid = campaign_id['BID_STRAT_ID'].astype(int)
byte = campaign_id['BID_STRAT_TYPE']


# In[20]:


### CREATION OF THE CAMPAIGN ###
  
campaign_service = client.GetService('CampaignService', version='v201809')
operations = [{
      'operator': 'ADD',
      'operand': {
          'name': 'GEN_'+campaign_name+' - tROAS',
          'status': 'PAUSED',
          'advertisingChannelType': 'SEARCH',
          'biddingStrategyConfiguration': {
                    'biddingStrategyType': str(byte),
                    'biddingStrategyId' : bid
          },
          #'endDate': (datetime.datetime.now() +
          #            datetime.timedelta(3650)).strftime('%Y%m%d'),
          'budget': {'budgetId' : budget_id},
          'networkSetting': {
              'targetGoogleSearch': 'true',
              'targetSearchNetwork': 'true',
              'targetContentNetwork': 'false',
              'targetPartnerSearchNetwork': 'false'
          },
          'settings': [
                {
                    'xsi_type' : 'DynamicSearchAdsSetting',
                    'domainName' : domain, 
                    'languageCode' : language
                  
                },
                {
                    # Targeting restriction settings. Depending on the
                    # criterionTypeGroup value, most TargetingSettingDetail only
                    # affect Display campaigns. However, the
                    # USER_INTEREST_AND_LIST value works for RLSA campaigns -
                    # Search campaigns targeting using a remarketing list.
                    'xsi_type': 'TargetingSetting',
                    'details': [
                        # Restricting to serve ads that match your ad group
                        # placements. This is equivalent to choosing
                        # "Target and bid" in the UI.
                        {
                            'xsi_type': 'TargetingSettingDetail',
                            'criterionTypeGroup': 'USER_INTEREST_AND_LIST',
                            'targetAll': 'true',
                        }
                    ]
                }
          ]

          
      }
  }]

campaigns = campaign_service.mutate(operations)

for campaign in campaigns['value']:
    print('Campaign with name "%s" and id "%s" was added.'
          % (campaign['name'], campaign['id']))
    
id_campaign = campaign['id']


# In[21]:


campaign_model = campaign_id['CAMPAIGN_NAME']
campaign_model = campaign_model.replace('_', ' ')

if category == 'smartphone':
    campaign_model = campaign_model.replace('sony', '')
    campaign_model = campaign_model.replace('apple', '')
    campaign_model = campaign_model.replace('samsung', '')
else:
    pass

campaign_model = campaign_model.strip()

try:
    campaign_model = campaign_model.split(' - ', 1)[0]
except:
    pass

campaign_model = campaign_model.strip()


# In[22]:


### EXTRACT LATEST CAMPAIGN NAME ###
model_campaign = campaign_model.split(' ', 1)[0]
model_campaign_1 = campaign_model.split(' ', 2)[1]
try :
    model_campaign_2 = campaign_model.split(' ', 2)[2]
except:
    model_campaign_2 = model_campaign
    
model_campaign = model_campaign.strip()
model_campaign_1 = model_campaign_1.strip()
model_campaign_2 = model_campaign_2.strip()


# In[23]:


### UPLOAD LIST OF AD GROUPS ###

ad_groups = pd.read_csv('new_campaigns_template.csv', sep = ';', encoding='latin-1', usecols = [country])
ad_groups = ad_groups.rename(columns={country : 'AD GROUP NAME'})
ad_group_id = list(ad_groups['AD GROUP NAME'].unique())

## TO BE MADE VARIABLE ACCORDING TO COUNTRY


# In[24]:


### GET FINAL LIST###

ad_groups['AD GROUP NAME'] = ad_groups['AD GROUP NAME'].str.replace('model', model_exact, regex=True)
ad_groups['AD GROUP NAME'] = ad_groups['AD GROUP NAME'].str.replace('brand', brand, regex=True)
ad_groups = ad_groups.dropna()
ad_group_id = list(ad_groups["AD GROUP NAME"].unique())


# In[25]:


ad_group_id_dynamic = ad_groups[(ad_groups["AD GROUP NAME"].str.contains('cat.D')) | (ad_groups["AD GROUP NAME"].str.contains('Dynamic')) | (ad_groups["AD GROUP NAME"].str.contains('DSA'))]
ad_group_id_dynamic = list(ad_group_id_dynamic["AD GROUP NAME"])


ad_group_id_normal = ad_groups[(ad_groups["AD GROUP NAME"].str.contains('cat.D') == False) & (ad_groups["AD GROUP NAME"].str.contains('Dynamic') == False) & (ad_groups["AD GROUP NAME"].str.contains('DSA') == False)]
ad_group_id_normal = list(ad_group_id_normal["AD GROUP NAME"].unique())


# In[26]:


ad_group_id_normal


# In[27]:


### CREATION OF THE ADGROUPS ###

campaign_id = int(id_campaign)
ad_groups_ids_normal = []

def ad_group_creation(client, campaign_id):
    ad_group_service = client.GetService('AdGroupService', version='v201809')

    # Construct operations and add ad groups.
    operations = [{
        'operator': 'ADD',
        'operand': {
            'campaignId': campaign_id,
            'name': i,
            'status': 'ENABLED',
            'biddingStrategyConfiguration': {
                'bids': [
                    {
                        'xsi_type': 'CpcBid',
                        'bid': {
                            'microAmount': '1000000'
                        },
                    }
                ]
            },
            'settings': [
                {
                    # Targeting restriction settings. Depending on the
                    # criterionTypeGroup value, most TargetingSettingDetail only
                    # affect Display campaigns. However, the
                    # USER_INTEREST_AND_LIST value works for RLSA campaigns -
                    # Search campaigns targeting using a remarketing list.
                    'xsi_type': 'TargetingSetting',
                    'details': [
                        # Restricting to serve ads that match your ad group
                        # placements. This is equivalent to choosing
                        # "Target and bid" in the UI.
                        {
                            'xsi_type': 'TargetingSettingDetail',
                            'criterionTypeGroup': 'PLACEMENT',
                            'targetAll': 'false',
                        },
                        # Using your ad group verticals only for bidding. This is
                        # equivalent to choosing "Bid only" in the UI.
                        {
                            'xsi_type': 'TargetingSettingDetail',
                            'criterionTypeGroup': 'VERTICAL',
                            'targetAll': 'true',
                        },
                    ]
                }
            ]
        }
    }]
    ad_groups = ad_group_service.mutate(operations)

    # Display results.
    for ad_group in ad_groups['value']:
        print ('Ad group with name "%s" and id "%s" was added.'
               % (ad_group['name'], ad_group['id']))

        ad_id = ad_group['id']
        ad_name = ad_group['name']
        ad_groups_ids_normal.append([ad_id, ad_name])

for i in ad_group_id_normal:
    ad_group_creation(client, campaign_id)


# In[28]:


### CREATION OF THE DYNAMIC ADGROUPS ###

campaign_id = int(id_campaign)
ad_groups_ids_dynamic = []

def ad_group_creation(client, campaign_id):
    ad_group_service = client.GetService('AdGroupService', version='v201809')

    # Construct operations and add ad groups.
    operations = [{
        'operator': 'ADD',
        'operand': {
            'campaignId': campaign_id,
            'name': i,
            'status': 'ENABLED',
            'adGroupType': 'SEARCH_DYNAMIC_ADS',
            'biddingStrategyConfiguration': {
                'bids': [
                    {
                        'xsi_type': 'CpcBid',
                        'bid': {
                            'microAmount': '1000000'
                        },
                    }
                ]
            },
            'settings': [
                {
                    # Targeting restriction settings. Depending on the
                    # criterionTypeGroup value, most TargetingSettingDetail only
                    # affect Display campaigns. However, the
                    # USER_INTEREST_AND_LIST value works for RLSA campaigns -
                    # Search campaigns targeting using a remarketing list.
                    'xsi_type': 'TargetingSetting',
                    'details': [
                        # Restricting to serve ads that match your ad group
                        # placements. This is equivalent to choosing
                        # "Target and bid" in the UI.
                        {
                            'xsi_type': 'TargetingSettingDetail',
                            'criterionTypeGroup': 'PLACEMENT',
                            'targetAll': 'false',
                        },
                        # Using your ad group verticals only for bidding. This is
                        # equivalent to choosing "Bid only" in the UI.
                        {
                            'xsi_type': 'TargetingSettingDetail',
                            'criterionTypeGroup': 'VERTICAL',
                            'targetAll': 'true',
                        },
                    ]
                }
            ]
        }
    }]
    ad_groups = ad_group_service.mutate(operations)

    # Display results.
    for ad_group in ad_groups['value']:
        print ('Ad group with name "%s" and id "%s" was added.'
               % (ad_group['name'], ad_group['id']))

        ad_id_dynamic = ad_group['id']
        ad_name_dynamic = ad_group['name']
        ad_groups_ids_dynamic.append([ad_id_dynamic, ad_name_dynamic])

for i in ad_group_id_dynamic:
    ad_group_creation(client, campaign_id)


# In[29]:


ad_groups_ids_dynamic


# In[30]:


ad_groups_ids_normal = pd.DataFrame(ad_groups_ids_normal)
ad_groups_ids_dynamic = pd.DataFrame(ad_groups_ids_dynamic)
ad_groups_ids = pd.concat([ad_groups_ids_normal, ad_groups_ids_dynamic])


# In[31]:


### GET KEYWORDS PER AdGroup ###

keywords = []

ad_group_criterion_service = client.GetService('AdGroupCriterionService', version='v201809')

def negatives_keyword(client, adgroups_ids):
    # Construct selector and get all ad group criteria.
    selector = {
        'fields': ['KeywordText', 'CriterionUse'],
        'predicates': [
            {
                'field': 'AdGroupId', 
                'operator': 'EQUALS',
                'values': j
            },
            {
                'field' : 'CriterionUse',
                'operator' : 'EQUALS',
                'values' : 'BIDDABLE'
            }
        ]
    }
    

    page = ad_group_criterion_service.get(selector)
    
    for i in page['entries']:
        try:
            keywords.append({
                'KEYWORD' : i['criterion']['text'],
                'ADGROUP_ID' : j,
                'MATCH_TYPE' : i['criterion']['matchType']
            })
        except:
            pass
        
for j in adgroups_ids:
    negatives_keyword(client, adgroups_ids)

keywords = pd.DataFrame(keywords)


# In[32]:


if model_campaign_2 == model_campaign and model != model_2:
    model_b = model_1+' +'+model_2
    model_bis1 = model_1+ ' '+model_2
    model_bis2 = model
elif model_campaign_2 != model_campaign and model == model_2:
    model_b = model_1
    model_bis1 = model_1
    model_bis2 = ''
else:
    model_b = model_1
    model_bis1 = model_1
    model_bis2 = model_2


# In[33]:


keywords.KEYWORD = [x.lower() for x in keywords.KEYWORD]


# In[34]:


keywords_broad = keywords[keywords['MATCH_TYPE'] == 'BROAD']
keywords_broad['KEYWORD'] = [i.replace(model_campaign, model) for i in keywords_broad['KEYWORD']]
keywords_broad['KEYWORD'] = [i.replace(model_campaign_1, model_b) for i in keywords_broad['KEYWORD']]
keywords_broad['KEYWORD'] = [
    i.replace(' +', ' ') for i in keywords_broad['KEYWORD']]
keywords_broad['KEYWORD'] = [
    i.replace(' ', ' +') for i in keywords_broad['KEYWORD']]

keywords_exact = keywords[keywords['MATCH_TYPE'] != 'BROAD']
keywords_exact['KEYWORD'] = [i.replace(model_campaign, model) for i in keywords_exact['KEYWORD']]
keywords_exact['KEYWORD'] = [i.replace(model_campaign_1, model_bis1) for i in keywords_exact['KEYWORD']]
keywords_exact['KEYWORD'] = [i.replace(model_campaign_2, model_bis2) for i in keywords_exact['KEYWORD']]

keywords = pd.concat([keywords_broad, keywords_exact])

keywords['KEYWORD'] = [i.replace('+ ', '') for i in keywords['KEYWORD']]

keywords
# In[35]:


if category == 'smartphone':
    adgroups['ADGROUP_NAME'] = [i.replace('sony', '') for i in adgroups['ADGROUP_NAME']]
    adgroups['ADGROUP_NAME'] = [i.replace('apple', '') for i in adgroups['ADGROUP_NAME']]
    adgroups['ADGROUP_NAME'] = [i.replace('samsung', '') for i in adgroups['ADGROUP_NAME']]
else:
    pass

adgroups['ADGROUP_NAME'] = [i.lower() for i in adgroups['ADGROUP_NAME']]
adgroups['ADGROUP_NAME'] = [i.replace(model_campaign, model) for i in adgroups['ADGROUP_NAME']]
adgroups['ADGROUP_NAME'] = [i.replace(model_campaign_1, model_bis1) for i in adgroups['ADGROUP_NAME']]
adgroups['ADGROUP_NAME'] = [x.replace(model_campaign_2, model_bis2) for x in adgroups['ADGROUP_NAME']]
adgroups['ADGROUP_NAME'] = adgroups['ADGROUP_NAME'].astype(str)
adgroups['ADGROUP_NAME'] = [i.strip() for i in adgroups['ADGROUP_NAME']]
adgroups['ADGROUP_NAME'] = [i.replace('marketplaces', 'marketplace') for i in adgroups['ADGROUP_NAME']]
adgroups['ADGROUP_NAME'] = [i.replace('  ', ' ') for i in adgroups['ADGROUP_NAME']]
adgroups['ADGROUP_NAME'] = [i.replace('cat. ', 'cat.') for i in adgroups['ADGROUP_NAME']]


# In[36]:


ad_groups_ids = pd.DataFrame(ad_groups_ids)
ad_groups_ids.rename(columns={0: 'id', 1: 'ADGROUP_NAME'},inplace=True)
ad_groups_ids['ADGROUP_NAME'] = [i.lower() for i in ad_groups_ids['ADGROUP_NAME']]
#ad_groups_ids['ADGROUP_NAME'] = [i.replace(model_exact+' -', model_exact+' ') for i in ad_groups_ids['ADGROUP_NAME']]
#ad_groups_ids['ADGROUP_NAME'] = [i.replace('ipad', '- ipad') for i in ad_groups_ids['ADGROUP_NAME']]

ad_groups_ids['ADGROUP_NAME'] = ad_groups_ids['ADGROUP_NAME'].astype(str)
ad_groups_ids['ADGROUP_NAME'] = [i.strip() for i in ad_groups_ids['ADGROUP_NAME']]
ad_groups_ids['ADGROUP_NAME'] = [i.replace('  ', ' ') for i in ad_groups_ids['ADGROUP_NAME']]


# In[37]:


ad_groups_ids


# In[38]:


### MERGE FETCHED AdGroups ID + NAME WITH FETCHED KEYWORDS ###

ad_groups_kw = pd.merge(adgroups, keywords)
ad_groups_kw = ad_groups_kw[['ADGROUP_NAME', 'KEYWORD', 'MATCH_TYPE']]

if category == 'smartphone':
    ad_groups_kw['ADGROUP_NAME'] = [i.replace('sony', '') for i in ad_groups_kw['ADGROUP_NAME']]
    ad_groups_kw['ADGROUP_NAME'] = [i.replace('apple', '') for i in ad_groups_kw['ADGROUP_NAME']]
    ad_groups_kw['ADGROUP_NAME'] = [i.replace('samsung', '') for i in ad_groups_kw['ADGROUP_NAME']]
else:
    pass


ad_groups_kw['ADGROUP_NAME'] = ad_groups_kw['ADGROUP_NAME'].astype(str)
ad_groups_kw['ADGROUP_NAME'] = [i.strip() for i in ad_groups_kw['ADGROUP_NAME']]
ad_groups_kw['ADGROUP_NAME'] = [i.replace('  ', ' ') for i in ad_groups_kw['ADGROUP_NAME']]
ad_groups_kw['ADGROUP_NAME'] = [i.replace('cat. ', 'cat.') for i in ad_groups_kw['ADGROUP_NAME']]


# In[39]:


### MERGE NEW AdGroups ID WITH KEYWORDS TO BE CREATED ###

new_adgroup_kw = pd.merge(ad_groups_kw, ad_groups_ids)


# In[40]:


ids_new = pd.merge(ad_groups_ids, adgroups, how='left')


# In[41]:


### CREATE AND INSERT KEYWORDS ###

def keywords_creation(client):
    # Initialize appropriate service.
    ad_group_criterion_service = client.GetService(
        'AdGroupCriterionService', version='v201809')

    # Construct keyword ad group criterion object.
    keyword = {
        'xsi_type': 'BiddableAdGroupCriterion',
        'adGroupId': i,
        'criterion': {
            'xsi_type': 'Keyword',
            'matchType': j,
            'text': k
        },
        # These fields are optional.
        'userStatus': 'PAUSED'
    }

    # Construct operations and add ad group criteria.
    operations = [
        {
            'operator': 'ADD',
            'operand': keyword
        }
    ]
    ad_group_criteria = ad_group_criterion_service.mutate(operations)['value']

    # Display results.
    for criterion in ad_group_criteria:
        print ('Keyword ad group criterion with ad group id "%s", criterion id '
               '"%s", text "%s", and match type "%s" was added.'
               % (criterion['adGroupId'], criterion['criterion']['id'],
                  criterion['criterion']['text'],
                  criterion['criterion']['matchType']))

ad_groups_final = new_adgroup_kw[new_adgroup_kw['MATCH_TYPE']!='DYNAMIC'] 

k_ad = list(ad_groups_final["id"])
k_type = list(ad_groups_final["MATCH_TYPE"])
k_key = list(ad_groups_final["KEYWORD"])
        

for i,j,k in zip(k_ad,k_type,k_key):
    keywords_creation(client)


# In[42]:


# CHECK IF ADGROUPS HAVE KEYWORDS

has_keywords = []

ad_group_criterion_service = client.GetService('AdGroupCriterionService', version='v201809')

def negatives_keyword(client, adgroups_ids):
    # Construct selector and get all ad group criteria.
    selector = {
        'fields': ['KeywordText', 'CriterionUse'],
        'predicates': [
            {
                'field': 'AdGroupId', 
                'operator': 'EQUALS',
                'values': j
            },
            {
                'field' : 'CriterionUse',
                'operator' : 'EQUALS',
                'values' : 'BIDDABLE'
            }
        ]
    }
    

    page = ad_group_criterion_service.get(selector)
    
    for i in page['entries']:
        try:
            has_keywords.append({
                'KEYWORD' : i['criterion']['text'],
                'id' : j
            })
        except:
            pass
        
for j in k_ad:
    negatives_keyword(client, adgroups_ids)

has_keywords = pd.DataFrame(has_keywords)


# In[43]:


### DOES THE ADGROUP HAVE KEYWORDS?
keywords_yes = pd.DataFrame()
keywords_yes['id'] = has_keywords['id'].unique()
keywords_yes['STATUS'] = 'ENABLED'

adgroups_status = pd.merge(ad_groups_ids, keywords_yes, how='left')
adgroups_status['STATUS'] = adgroups_status['STATUS'].fillna('PAUSED')


# In[44]:


### PAUSE ADGROUPS WITH NO KEYWORDS ###


def ad_group_creation(client):
    ad_group_service = client.GetService('AdGroupService', version='v201809')
    
    operations = [
        {
            'operator': 'SET',
            'operand': {
                'id': i, # FOR TEST - THEN WE LOOP FOR EACH AdGroup #
                'status': s
            }
        }
    ]

    status = ad_group_service.mutate(operations)

    # Construct operations and add ad groups.
  
for i, s in zip(adgroups_status['id'], adgroups_status['STATUS']):
    ad_group_creation(client)


# In[45]:


### GET SHARED SET OF CAMPAIGNS ###

report_downloader = client.GetReportDownloader(version='v201809')
    
advertisers = account # make it variable given "country"
    
report = {
    'reportName': 'CAMPAIGN_SHARED_SET_REPORT',
    'dateRangeType': 'LAST_7_DAYS',
    'reportType': 'CAMPAIGN_SHARED_SET_REPORT',
    'downloadFormat': 'CSV',
    'selector': {
        'fields': ['CampaignId', 'CampaignName', 'SharedSetId', 'SharedSetName'],
    }
}
    
# Print out the report as a string
for __ , key in enumerate(advertisers):
    path = "shared_set_"+ country +".csv"
    print('Report for the account {} is being loaded in the local file {} \n'.format(advertisers[key], path))
    
    with open(path,"wb") as fn:
        report_downloader.DownloadReport(report, 
                                         fn ,
                                         client_customer_id=advertisers[key],
                                         skip_report_header=True, 
                                         skip_column_header=False,
                                         skip_report_summary=True, 
                                         include_zero_impressions=False)
        fn.close()

### KEEP ONLY THE ONE FOR THE LATEST CAMPAIGN ###

shared_set = pd.read_csv("shared_set_"+ country +".csv", sep=",")
shared_set['CAMPAIGN_ID'] = shared_set['Campaign ID']
campaigns_ids_names = pd.DataFrame(campaigns_ids_names)
shared_set = pd.merge(shared_set, campaigns_ids_names, how='inner')
shared_set_id = list(shared_set['Shared Set ID'])


# In[46]:


### ADD THE NEGATIVE KEYWORD LIST ###

def negative_kw(client, campaign_id, shared_set_id):
    # Initialize appropriate services.
    shared_set_service = client.GetService('SharedSetService', version='v201809')
    shared_criterion_service = client.GetService('SharedCriterionService', version='v201809')
    campaign_shared_set_service = client.GetService('CampaignSharedSetService', version='v201809')


    # Attach the articles to the campaign.
    campaign_set = {
        'campaignId': campaign_id,
        'sharedSetId': set_id
    }
    
    operations = [
        {
            'operator': 'ADD',
            'operand': campaign_set
        }
    ]

    response = campaign_shared_set_service.mutate(operations)

    if 'value' in response:
        print ('Shared set ID %d was attached to campaign ID %d' % (
            response['value'][0]['sharedSetId'], response['value'][0]['campaignId']
        ))
    else:
        raise errors.GoogleAdsError('No campaign shared set was added.')
    
try: 
    for set_id in shared_set_id:
        negative_kw(client, campaign_id, shared_set_id)
except:
    pass


# In[47]:


id_geoloc = latest_campaign_id


# In[48]:


#client = adwords.AdWordsClient.LoadFromStorage('/users/backmarket/desktop/googleads_germany.yaml')
location_df = []

def location(client):
    # Initialize appropriate service.
    campaign_criterion_service = client.GetService('CampaignCriterionService', version='v201809')

    selector = {
        'fields': ['CampaignId', 
                   'CriteriaType',
                   'Id', 
                   'LocationName'],
        'predicates': [{
            'field': 'CampaignId',
            'operator': 'EQUALS',
            'values': [id_geoloc]},
            {
                'field': 'CriteriaType',
                'operator': 'IN',
                'values': ['LOCATION']
            }],
    }
    page = campaign_criterion_service.get(selector)

    for campaign_criterion in page['entries']:
        criterion = campaign_criterion['criterion']
        location_df.append([criterion['id'], criterion['locationName']])

location(client)

location_df = pd.DataFrame(location_df)
location_df.rename(columns={0: 'location_id', 1: 'location_name'},inplace=True)


# In[49]:


### ADD THOSE SETTINGS TO THE NEW CAMPAIGN ###

def geo_target(client):

    campaign_criterion_service = client.GetService('CampaignCriterionService', version='v201809')

    operations = [{
        'operator': 'ADD',
        'operand': {
            'campaignId': id_campaign,
            'criterion': {
                'xsi_type': 'Location',
                'id': i
            }
        }
    }]

    result = campaign_criterion_service.mutate(operations)

try:
    locations = list(location_df['location_id'])
except:
    pass

try:
    for i in locations:
        geo_target(client)
except:
    pass


# In[50]:


### URLS LP ###

def urls_lp(country, model_exact, brand):
    
    ## GERMANY ##
    if country == 'Germany':
    
        url_lp = 'https://www.backmarket.de/'+model_exact.replace(' ', '/', 1).replace(' ', '-', 2)+'-gebraucht.html'
        print(url_lp)
    
        
    ## SPAIN ##    
    elif country == 'Spain':
        
        url_lp = 'https://www.backmarket.es/'+model_exact.replace(' ', '/', 1).replace(' ', '-', 2)+'-reacondicionado.html'
        print(url_lp)
        
    
    ## FRANCE ##
    elif country == 'France' :
        
        url_lp = 'https://www.backmarket.fr/'+model_exact.replace(' ', '/', 1).replace(' ', '-', 2)+'-reconditionnes.html'
        print(url_lp)
        
    
    ## ITALY ##
    elif country == 'Italy' :
        
        url_lp = 'https://www.backmarket.it/'+model_exact.replace(' ', '/', 1).replace(' ', '-', 2)+'-ricondizionato.html'
        print(url_lp)
        
    
    ## BELGIUM ##
    elif country == 'Belgium' :
        
        url_lp = 'https://www.backmarket.fr/'+model_exact.replace(' ', '/', 1).replace(' ', '-', 2)+'-reconditionnes.html'
        print(url_lp)
        
    
    ## TESTS ##
    elif country == 'Tests' :
        
        url_lp = 'https://www.backmarket.de/'+model_exact.replace(' ', '/', 1).replace(' ', '-', 2)+'-gebraucht.html'
        print(url_lp)
        
        
    return url_lp

url_lp = urls_lp(country, model_exact, brand)


# In[51]:


import urllib.request
try:
    print(urllib.request.urlopen(url_lp).getcode())
except:
    url_lp = url_lp.replace(brand+'/', brand+'-')

try:
    print(urllib.request.urlopen(url_lp).getcode())
except:
    url_lp = url_lp.replace(model.lower()+'/', brand+'/'+model.lower()+'-')


# In[52]:


### DISPLAY PATH 1 ###

if model == model_2:
    model_2 = model_1
    model_1 = model

def path(country, model_exact, brand): 
    
    ## GERMANY ##
    if country == 'Germany' :
        
        path = model_1+'-'+model_2
        
    ## SPAIN ##    
    elif country == 'Spain' :
        
        path = model+'-'+model_1
        
    ## FRANCE ##
    elif country == 'France' :
        
        path = model+'-'+model_1
        
    ## ITALY ##
    elif country == 'Italy' :
        
        path = model+'-'+model_1

    ## BELGIUM ##
    elif country == 'Belgium' :
        
        path = model+'-'+model_1

    ## TESTS ##
    elif country == 'Tests' :
        
        path = model+'-'+model_1
    
    return path

path = path(country, model_exact, brand)
path = path.replace(' ', '-')


# In[53]:


### DISPLAY PATH 2 ###

def path2(country, model_exact, brand):
    
    ## GERMANY ##
    if country == 'Germany' :
        
        path2 = 'gebraucht'
        
    ## SPAIN ##    
    elif country == 'Spain' :
        
        path2 = 'reacondicionado'
        
    ## FRANCE ##
    elif country == 'France' :
        
        path2 = 'reconditionnes'
        
    ## ITALY ##
    elif country == 'Italy' :
        
        path2 = 'ricondizionato'

    ## BELGIUM ##
    elif country == 'Belgium' :
        
        path2 = 'reconditionnes'

    ## TESTS ##
    elif country == 'Tests' :
        
        path2 = 'reconditionnes'
    
    return path2

path2 = path2(country, model_exact, brand)

# In[]:

# In[54]:


### GETS ADS FROM ADGROUPS LATEST CAMPAIGN ###

text_ads = []

def get_text_ads(client):
    # Initialize appropriate service.
    ad_group_ad_service = client.GetService('AdGroupAdService', version='v201809')

    # Construct selector and get all ads for a given ad group.
    selector = {
        'fields': ['Id', 'AdGroupId', 'Status', 'HeadlinePart1', 'HeadlinePart2', 'Headline', 
                   'Description', 'Description2', 'Path1', 'Path2', 'CreativeFinalUrls'],
        'predicates': [
            {
                'field': 'AdGroupId',
                'operator': 'EQUALS',
                'values': [j]
            },
            {
                'field': 'AdType',
                'operator': 'EQUALS',
                'values': ['EXPANDED_TEXT_AD']
            }
        ]
    }
    
    page = ad_group_ad_service.get(selector)
    
    for i in page['entries']:
        text_ads.append({
            'HEADLINE1' : i['ad']['headlinePart1'],
            'HEADLINE2' : i['ad']['headlinePart2'],
            'HEADLINE3' : i['ad']['headlinePart3'],
            'DESCRIPTION1' : i['ad']['description'],
            'DESCRIPTION2' : i['ad']['description2'],
            'ADGROUP_ID' : j
    })
    
    return text_ads


for j in adgroups_ids:
    get_text_ads(client)


# In[55]:


try:
    text_ads = pd.DataFrame(text_ads)
except:
    pass

# In[56]:


text_ads = pd.merge(text_ads, ids_new)
text_ads = pd.merge(text_ads, adgroups)

# In[]
text_ads['ADGROUP_NAME'] = [
    x.replace(model_exact, '') for x in text_ads['ADGROUP_NAME']]
text_ads['ADGROUP_NAME'] = [x.replace('- ', '') for x in text_ads['ADGROUP_NAME']]

# In[]
text_ads['ADGROUP_NAME'] = [x.replace('  ', ' ') for x in text_ads['ADGROUP_NAME']]
text_ads['ADGROUP_NAME'] = [x.split(' ', 1)[1] for x in text_ads['ADGROUP_NAME']]
text_ads['ADGROUP_NAME'] = [x.strip() for x in text_ads['ADGROUP_NAME']]

# In[]

text_ads['H1'] = campaign_name+' '+text_ads['ADGROUP_NAME']

if country == 'Spain'or country == 'Italy' or country == 'France':
    text_ads['HEADLINE'] = [campaign_name if len(x) > 30 else x for x in text_ads['H1']]
else:
    if len(campaign_name+' '+path2) > 30:
        text_ads['HEADLINE'] = campaign_name
    else:
        text_ads['HEADLINE'] = campaign_name+' '+path2


# In[57]:
text_ads
# In[]
try:
    ad_h2 = list(text_ads["HEADLINE2"])
except:
    pass

try:
    ad_h3 = list(text_ads["HEADLINE3"])
except:
    pass

try:
    ad_d1 = list(text_ads["DESCRIPTION1"])
except:
    pass

try:
    ad_d2 = list(text_ads["DESCRIPTION2"])
except:
    pass

try:
    ad_id = list(text_ads["id"])
except:
    pass

try:
    ad_h1 = list(text_ads["HEADLINE"])
except:
    pass


# In[58]:


model = model.capitalize()
model_bis1 = model_bis1.capitalize()
model_bis2 = model_bis2.capitalize()

model_campaign = model_campaign.capitalize()
model_campaign_1 = model_campaign_1.capitalize()
model_campaign_2 = model_campaign_2.capitalize()

model_cap = model.upper()
model_bis1_cap = model_bis1.upper()
model_bis2_cap = model_bis2.upper()

model_campaign_cap = model_campaign.upper()

if model_campaign_1.isdigit() == False:
    model_campaign_1_cap = model_campaign_1.upper()
else:
    model_campaign_1_cap = model_bis1_cap

if model_campaign_2.isdigit() == False:
    model_campaign_2_cap = model_campaign_2.upper()
else:
    model_campaign_2_cap = model_bis2_cap


# In[]


# In[59]:


ad_h2 = ['' if i is None
         else i.replace(model_campaign, model) for i in ad_h2]
ad_h2 = ['' if i is None
         else i.replace(model_campaign_1, model_bis1) for i in ad_h2]
ad_h2 = ['' if i is None
         else i.replace(model_campaign_2, model_bis2) for i in ad_h2]
ad_h2 = ['' if i is None
         else i.replace(model_campaign_cap, model_cap) for i in ad_h2]
ad_h2 = ['' if i is None
         else i.replace(model_campaign_1_cap, model_bis1_cap) for i in ad_h2]
ad_h2 = ['' if i is None
         else i.replace(model_campaign_2_cap, model_bis2_cap) for i in ad_h2]



ad_h3 = ['' if i is None
         else i.replace(model_campaign, model) for i in ad_h3]
ad_h3 = ['' if i is None
         else i.replace(model_campaign_1, model_bis1) for i in ad_h3]
ad_h3 = ['' if i is None
         else i.replace(model_campaign_2, model_bis2) for i in ad_h3]
ad_h3 = ['' if i is None
         else i.replace(model_campaign_cap, model_cap) for i in ad_h3]
ad_h3 = ['' if i is None
         else i.replace(model_campaign_1_cap, model_bis1_cap) for i in ad_h3]
ad_h3 = ['' if i is None
         else i.replace(model_campaign_2, model_bis2) for i in ad_h3]



ad_d1 = ['' if i is None
         else i.replace(model_campaign_2, model_bis2) for i in ad_d1]
ad_d1 = ['' if i is None
         else i.replace(model_campaign, model) for i in ad_d1]
ad_d1 = ['' if i is None
         else i.replace(model_campaign_1, model_bis1) for i in ad_d1]
ad_d1 = ['' if i is None
         else i.replace(model_campaign_2_cap, model_bis2_cap) for i in ad_d1]
ad_d1 = ['' if i is None
         else i.replace(model_campaign_cap, model_cap) for i in ad_d1]
ad_d1 = ['' if i is None
         else i.replace(model_campaign_1_cap, model_bis1_cap) for i in ad_d1]



ad_d2 = ['' if i is None
         else i.replace(model_campaign, model) for i in ad_d2]
ad_d2 = ['' if i is None
         else i.replace(model_campaign_1, model_bis1) for i in ad_d2]
ad_d2 = ['' if i is None
         else i.replace(model_campaign_2, model_bis2) for i in ad_d2]
ad_d2 = ['' if i is None
         else i.replace(model_campaign_cap, model_cap) for i in ad_d2]
ad_d2 = ['' if i is None
         else i.replace(model_campaign_1_cap, model_bis1_cap) for i in ad_d2]
ad_d2 = ['' if i is None
         else i.replace(model_campaign_2_cap, model_bis2_cap) for i in ad_d2]


# In[60]:


ad_d1 = [i.replace(model_2.upper(), model_2.capitalize()) if model_2.isalpha() == True 
         else i for i in ad_d1]

ad_d2 = [i.replace(model_2.upper(), model_2.capitalize()) if model_2.isalpha() == True 
         else i for i in ad_d2]

ad_h2 = [i.replace(model_2.upper(), model_2.capitalize()) if model_2.isalpha() == True 
         else i for i in ad_h2]

ad_h3 = [i.replace(model_2.upper(), model_2.capitalize()) if model_2.isalpha() == True 
         else i for i in ad_h3]


# In[61]:


result_1 = []
for i in ad_d1:
    if len(i) > 90:
        a = i.replace(brand.capitalize()+' ', '')
    else:
        a = i
    result_1.append(a)
    
result_2 = []
for i in ad_d2:
    if len(i) > 90:
        a = i.replace(brand.capitalize()+' ', '')
    else:
        a = i
    result_2.append(a)


# In[62]:


ad_d1 = result_1
ad_d2 = result_2

# In[63]:


result_1 = []
for i in ad_d1:
    if len(i) > 90:
        a = i.split('.')[0]
    else:
        a = i
    result_1.append(a)
    
result_2 = []
for i in ad_d2:
    if len(i) > 90:
        a = i.split('.')[0]
    else:
        a = i
    result_2.append(a)


# In[64]:


ad_d1 = result_1
ad_d2 = result_2

# In[65]:


### CREATE ADS ###

def adss(client, path, url_lp, ad_groups_ids):
    # Initialize appropriate service.
    ad_group_ad_service = client.GetService('AdGroupAdService', version='v201809')


    operations = [
        {
            'operator': 'ADD',
            'operand': {
                'xsi_type': 'AdGroupAd',
                'adGroupId': z, # FOR TEST - THEN WE LOOP FOR EACH AdGroup #
                'ad': {
                    'xsi_type': 'ExpandedTextAd',
                    'headlinePart1': a,
                    'headlinePart2': i,
                    'headlinePart3' : j,
                    'description': k,
                    'description2': n,
                    'path1' : path,
                    'path2' : path2,
                    'finalUrls': [url_lp]
                },
                'status': 'PAUSED'
            }
        }
    ]

    ads = ad_group_ad_service.mutate(operations)

    # Display results.
    for ad in ads['value']:
        print('Ad of type "%s" with id "%d" was added.'
              '\n\theadlinePart1: %s\n\theadlinePart2: %s\n\theadlinePart3: %s'
              % (ad['ad']['Ad.Type'], ad['ad']['id'],
                 ad['ad']['headlinePart1'], ad['ad']['headlinePart2'],
                 ad['ad']['headlinePart3']))


for i,j,k,n,z,a in zip(ad_h2, ad_h3, ad_d1, ad_d2, ad_id, ad_h1):
    try:
        adss(client, path, url_lp, ad_groups_ids)
    except:
        pass


# In[66]:


ad_groups_ids_dynamic = ad_groups_ids_dynamic.rename(columns={0 : 'id', 1 : 'adgroup'})
dynamic_id = list(ad_groups_ids_dynamic['id'])


# In[67]:


text1 = ad_d1[0]
text2 = ad_d2[0]


# In[68]:


### CREATE DSA ADS ###
# Initialize appropriate service.
ad_group_ad_service = client.GetService('AdGroupAdService', version='v201809')

def dynamic():
    operations = [
        {
            'operator': 'ADD',
            'operand': {
                'xsi_type': 'AdGroupAd',
                'adGroupId': i, # FOR TEST - THEN WE LOOP FOR EACH AdGroup #
                'ad': {
                    'xsi_type': 'ExpandedDynamicSearchAd',
                    'description': text1,
                    'description2': text2,
                   
                },
                'status': 'PAUSED'
            }
        }
    ]

    ads = ad_group_ad_service.mutate(operations)
    
    for ad in ads['value']:
        print('Ad of type "%s" with id "%d" was added.'
              '\n\theadlinePart1: %s\n\theadlinePart2: %s'
              % (ad['ad']['Ad.Type'], ad['ad']['id'],
                 ad['ad']['description'], ad['ad']['description2']))



for i in dynamic_id:
    dynamic()


# In[69]:


#######################################
### NEGATIVES KEYWORDS FOR ADGROUPS ###
#######################################


# In[71]:


### GET CAMPAIGN LEVEL NEGATIVE KEYWORDS ###

report_downloader = client.GetReportDownloader(version='v201809')
    
advertisers = account # make it variable given "country"
    
report = {
    'reportName': 'CAMPAIGN_NEGATIVE_KEYWORDS_PERFORMANCE_REPORT',
    'dateRangeType': 'LAST_7_DAYS',
    'reportType': 'CAMPAIGN_NEGATIVE_KEYWORDS_PERFORMANCE_REPORT',
    'downloadFormat': 'CSV',
    'selector': {
        'fields': ['CampaignId', 'CampaignName', 'Criteria', 'Id', 'IsNegative', 'KeywordMatchType']
    }
}
    
# Print out the report as a string
for __ , key in enumerate(advertisers):
    path = "campaign_negative_keywords_"+ country +".csv"
    print('Report for the account {} is being loaded in the local file {} \n'.format(advertisers[key], path))
    
    with open(path,"wb") as fn:
        report_downloader.DownloadReport(report, 
                                         fn ,
                                         client_customer_id=advertisers[key],
                                         skip_report_header=True, 
                                         skip_column_header=False,
                                         skip_report_summary=True, 
                                         include_zero_impressions=True)
        fn.close()

### KEEP ONLY THE ONE FOR THE LATEST CAMPAIGN ###

campaign_nkw = pd.read_csv("campaign_negative_keywords_"+ country +".csv")
campaign_nkw['CAMPAIGN_ID'] = campaign_nkw['Campaign ID']
campaigns_ids_names = pd.DataFrame(campaigns_ids_names)
campaign_nkw = pd.merge(campaign_nkw, campaigns_ids_names, how='inner')


# In[72]:


campaign_nkw = campaign_nkw[campaign_nkw['Campaign ID'] == latest_campaign_id]


# In[74]:


new_nkw = campaign_nkw.iloc[0]['Campaign']
new_nkw = new_nkw.replace('GEN_', '').lower()

campaign_ngw_2 = {'Negative keyword' : [new_nkw], 'Match type' : ['Phrase']}
campaign_ngw_2 = pd.DataFrame(campaign_ngw_2)
campaign_nkw = campaign_nkw[['Negative keyword', 'Match type']]
nkw_final = pd.concat([campaign_nkw, campaign_ngw_2])


# In[77]:


nkw_final = nkw_final[['Negative keyword', 'Match type']]
nkw_final = nkw_final.rename(columns={'Negative keyword' : 'KEYWORD', 'Match type' : 'MATCH_TYPE'})


# In[79]:


model = model.lower()
model_bis1 = model_bis1.lower()
model_bis2 = model_bis2.lower()

model_campaign = model_campaign.lower()
model_campaign_1 = model_campaign_1.lower()
model_campaign_2 = model_campaign_2.lower()


# In[80]:


nkw_final['KEYWORD'] = [i.lower() for i in nkw_final['KEYWORD']]
nkw_final['KEYWORD'] = [i.replace(model_campaign, model) for i in nkw_final['KEYWORD']]
nkw_final['KEYWORD'] = [i.replace(model_campaign_1, model_bis1) for i in nkw_final['KEYWORD']]
nkw_final['KEYWORD'] = [i.replace(model_campaign_2, model_bis2) for i in nkw_final['KEYWORD']]


# In[83]:


nkw_final['MATCH_TYPE'] = [i.upper() for i in nkw_final['MATCH_TYPE']]


# In[85]:


### ADD NEGATIVE KW TO CAMPAIGN ###

def negative_kw_campaign(client):
    
    campaign_criterion_service = client.GetService('CampaignCriterionService', version='v201809')
    
    neg_keyword = {
        'xsi_type': 'NegativeCampaignCriterion',
        'campaignId': campaign_id,
        'criterion': {
            'xsi_type': 'Keyword',
            'matchType': i,
            'text': j
        }
    }
    
    operations = [
        {
            'operator': 'ADD',
            'operand': neg_keyword
        }
    ]
    
    campaign_criteria = campaign_criterion_service.mutate(operations)['value']

nkw_final = nkw_final[nkw_final['MATCH_TYPE']!='DYNAMIC']
        

nk_type = list(nkw_final["MATCH_TYPE"])
nk_key = list(nkw_final["KEYWORD"])

for i,j in zip(nk_type,nk_key):
    try:
        negative_kw_campaign(client)
    except:
        pass


# In[86]:


### GET NEGATIVES KEYWORDS PER AdGroup ###

keywords = []

ad_group_criterion_service = client.GetService('AdGroupCriterionService', version='v201809')

def negatives_keyword(client, adgroups_ids):
    # Construct selector and get all ad group criteria.
    selector = {
        'fields': ['KeywordText', 'CriterionUse'],
        'predicates': [
            {
                'field': 'AdGroupId', 
                'operator': 'EQUALS',
                'values': j
            },
            {
                'field' : 'CriterionUse',
                'operator' : 'EQUALS',
                'values' : 'NEGATIVE'
            }
        ]
    }
    

    page = ad_group_criterion_service.get(selector)
    
    for i in page['entries']:
        try:
            keywords.append({
                'KEYWORD' : i['criterion']['text'],
                'ADGROUP_ID' : j,
                'MATCH_TYPE' : i['criterion']['matchType']
        })
        except:
            pass
        
    return keywords
        
for j in adgroups_ids:
    negatives_keyword(client, adgroups_ids)
    
keywords = pd.DataFrame(keywords)


# In[87]:


adgroups_keyword = pd.merge(keywords, ids_new)


# In[88]:


adgroups_keyword['KEYWORD'] = [i.lower() for i in adgroups_keyword['KEYWORD']]
adgroups_keyword['KEYWORD'] = [i.replace(model_campaign, model) for i in adgroups_keyword['KEYWORD']]
adgroups_keyword['KEYWORD'] = [i.replace(model_campaign_1, model_bis1) for i in adgroups_keyword['KEYWORD']]
adgroups_keyword['KEYWORD'] = [i.replace(model_campaign_2, model_bis2) for i in adgroups_keyword['KEYWORD']]


# In[89]:


negative_kw = adgroups_keyword


# In[91]:


final_list_nkw = negative_kw
final_list_nkw['MATCH_TYPE'] = final_list_nkw['MATCH_TYPE'].str.upper()


# In[93]:


### ADD NEGATIVE KW TO AdGroups ###

def negative_kw_adgroups(client):
    
    ad_group_criterion_service = client.GetService('AdGroupCriterionService', version='v201809')
    
    neg_keyword = {
        'xsi_type': 'NegativeAdGroupCriterion',
        'adGroupId': i,
        'criterion': {
            'xsi_type': 'Keyword',
            'matchType': j,
            'text': k
        }
    }
    
    operations = [
        {
            'operator': 'ADD',
            'operand': neg_keyword
        }
    ]
    
    ad_group_criteria = ad_group_criterion_service.mutate(operations)['value']

negative_kw = negative_kw[negative_kw['MATCH_TYPE']!='DYNAMIC']
        
k_ad = list(final_list_nkw["id"])
k_type = list(final_list_nkw["MATCH_TYPE"])
k_key = list(final_list_nkw["KEYWORD"])

for i,j,k in zip(k_ad,k_type,k_key):
    try:
        negative_kw_adgroups(client)
    except:
        pass


# In[94]:


### GET LATEST CAMPAIGN USERLISTS ###

report_downloader = client.GetReportDownloader(version='v201809')
    
advertisers = account # make it variable given "country"
    
report = {
    'reportName': 'AUDIENCE_PERFORMANCE_REPORT',
    'dateRangeType': 'ALL_TIME',
    'reportType': 'AUDIENCE_PERFORMANCE_REPORT',
    'downloadFormat': 'CSV',
    'selector': {
        'fields': ['CampaignId', 'CampaignName', 'Id', 'UserListName', 'Status'],
        'predicates' : [
            {
            'field' : 'CampaignId',
            'operator' : 'EQUALS',
            'values' : str(latest_campaign_id)
            }
        ]
    }
}
    
# Print out the report as a string
for __ , key in enumerate(advertisers):
    path = "user_list_"+ country +".csv"
    print('Report for the account {} is being loaded in the local file {} \n'.format(advertisers[key], path))
    
    with open(path,"wb") as fn:
        report_downloader.DownloadReport(report, 
                                         fn ,
                                         client_customer_id=advertisers[key],
                                         skip_report_header=True, 
                                         skip_column_header=False,
                                         skip_report_summary=True, 
                                         include_zero_impressions=True)
        fn.close()


# In[95]:


userlists = pd.read_csv("user_list_"+ country +".csv")


# In[96]:


#userlists.to_csv('userlits_campaignk.csv', index=False, sep=";")


# In[97]:


### GET ALL USERLIST ID ###

userlist_id = []

trial_service = client.GetService('AdwordsUserListService', version = 'v201809')

selector = {
            'fields': ['Id'],
}

page = trial_service.get(selector)


# In[98]:


userlist_id = []

for i in range(len(page.entries)):
    userlist_id.append({
        'USERLIST_ID' : page.entries[i]['id'],
        'USERLIST_NAME' : page.entries[i]['name']
    })

userlist_id = pd.DataFrame(userlist_id)

#userlist_id.to_csv('userlits_to_check.csv', index=False, sep=";")


# In[99]:


### MERGE LATEST CAMPAIGN USERLIST WITH USERLIST ID ###

userlists = userlists.rename(columns={'User list name' : 'USERLIST_NAME'})
try:
    final_userlist_id = pd.merge(userlist_id, userlists, how='inner')
    criterion_list = list(final_userlist_id.USERLIST_ID)
except:
    pass


# In[100]:


### ADD USERLIST TO NEW CAMPAIGN ###

def userlist():
    
    campaign_criterion_service = client.GetService(
          'CampaignCriterionService', version='v201809')

    userlist = {
        'xsi_type' : 'CampaignCriterion',
        'campaignId': id_campaign,
        'criterion': {
            'xsi_type': 'CriterionUserList',
            'userListId': ids        
        }
    }

    operations = [
        {
            'operator' : 'ADD',
            'operand' : userlist
        }
    ]


    ul = campaign_criterion_service.mutate(operations)['value']

for ids in criterion_list:
    try:
        userlist()
    except:
        pass


# In[101]:


ad_group_criterion_service = client.GetService('AdGroupCriterionService', version='v201809')

    # Construct selector and get all ad group criteria.
selector = {
        'fields': ['KeywordText', 'CriteriaType', 'AdGroupId'],
        'predicates': [
            {
                'field' : 'CriterionType',
                'operator' : 'EQUALS',
                'values' : 'WEBPAGE'
            },
            {
                'field' : 'AdGroupId',
                'operator' : 'EQUALS',
                'values' : 79095443428
            }
        ]
    }

page = ad_group_criterion_service.get(selector)
print(page)


# In[102]:


ad_group_criterion_service = client.GetService('AdGroupCriterionService', version='v201809')

def webpage():
    webpage = {
        'xsi_type': 'BiddableAdGroupCriterion',
        'adGroupId': i,
        'criterion' : {
            'xsi_type' : 'Webpage',
            'parameter' : {
                'criterionName' : 'LP',
                'conditions' : [
                    {
                        'operand' : 'URL',
                        'argument' : url_lp,
                        'operator' : 'CONTAINS'
                    }
                ]
            }
        }
    }

    operations = [
        {
            'operator': 'ADD',
            'operand': webpage
        }
    ]

    ad_group_criteria = ad_group_criterion_service.mutate(operations)['value']
    
for i in dynamic_id:
    webpage()

