import pandas as pd
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

#Business Data functions

def yelp_call(url_params):
    response = requests.get(url= 'https://api.yelp.com/v3/businesses/search', headers=headers, params=url_params)
    return response.json()['businesses']

def parse_results(list_of_data):
    # create a container to hold our parsed data
    biz_list = []
    # loop through our business and 
    for business in list_of_data:
    # parse each individual business into a tuple
    #parseing out transactions
        if 'pickup'in business['transactions']:
            business['pickup'] = True
        else:
            business['pickup'] = False
        if 'delivery' in business['transactions']:
            business['delivery'] = True
        else:
            business['delivery'] = False
        if 'restaurant_reservation' in business['transactions']:
            business['restaurant_reservation'] = True
        else:
            business['restaurant_reservation'] = False
    
    #checking if price is there
        if 'price' not in business:
            business['price'] = np.nan
        biz_tuple = (business['id'],
                     business['name'],
                     business['location']['address1'],
                     business['rating'],
                     business['price'],
                     business['location']['zip_code'],
                     business['pickup'],
                     business['delivery'],
                     business['restaurant_reservation'],
                     business['review_count'],
                     business['categories'],
                     business['is_closed'])   
    # add each individual business tuple to our data container
        biz_list.append(biz_tuple)
    # return the container with all of the parsed results
    return biz_list

def df_save(csv_file_path, parsed_results):
    # code to open the csv file, concat the current data, and save the data. 
    business_df = pd.DataFrame(parsed_results, columns = ['Id','Name', 'Location', 'Rating', 'Price', 'Zipcode', 'Pickup', 'Delivery', 'Reservation', 'Review Count', 'Categories','Status'])
    x = business_df.to_csv(csv_file_path, mode = 'a')
    return x

#Review Data functions

def yelp_call_rev(url_params, given_df):
    #container for review per business
    responses=[]
    #loops through business ids and inserts for new url per business review
    for business in list(given_df['Id']):
        url = 'https://api.yelp.com/v3/businesses/{}/reviews'.format(business)
        #try except block to continue code for any errors
        try:
            response = requests.get(url, headers=headers)
            responses.append((response.json()['reviews'],business))
        except:
            continue
    return responses

def parse_results_review(list_of_data, given_df):
    review_list = []
    for l in yelp_call_rev(url_params, given_df):
        for review in l:
            for t in review:
#             print (t)
                try:
                    review_tuple = (l[1],
                            t['id'],
                            t['text'],
                            t['rating'],
                            t['time_created'])   
    # add each individual business tuple to our data container
                    review_list.append(review_tuple)
                except:
                    break
    # return the container with all of the parsed results
    return review_list

def df_save_review(csv_file_path, parsed_results):
    # your code to open the csv file, concat the current data, and save the data. 
    business_df = pd.DataFrame(parsed_results, columns = ['Business ID','ID', 'Review', 'Rating', 'Date'])
    business_df.to_csv(csv_file_path, mode = 'a')
    new_df = pd.read_csv(csv_file_path, delimiter = ",") #delte this later
    return new_df

#importing all csvs
thaidf = pd.read_csv('../Data/thaii.csv')
mexdf = pd.read_csv('../Data/mexx.csv')

thai_rev_df=pd.read_csv('../Data/thaireview.csv')
mex_rev_df=pd.read_csv('../Data/mexreview.csv')

#add column to df to specify Thai or Mexican restaurant
thaidf['type']='Thai'
mexdf['type']='Mexican'

#concat dataframes and set id to unique identifier
df=pd.concat([thaidf,mexdf])
df_review=pd.concat([thai_rev_df,mex_rev_df])
df=df.set_index('Id')
df_review=df_review.set_index('ID')

#had duplicate indicies so dropped that column
df=df.drop(df.columns[0], axis=1)
df_review=df_review.drop(df_review.columns[0],axis=1)

#had headers in place of data so removed those rows
df = df[df['Rating']!='Rating']
thaidf=thaidf[thaidf['Rating']!='Rating']
mexdf=mexdf[mexdf['Rating']!='Rating']

#changed column types from objects to type of choice
df['Review Count']=df['Review Count'].astype(int)
df['Rating']=df['Rating'].astype(float)
df['Price']=df['Price'].astype('string')
thaidf['Rating']=thaidf['Rating'].astype(float)
mexdf['Rating']=mexdf['Rating'].astype(float)
thaidf['Review Count'] = thaidf['Review Count'].astype(int)
mexdf['Review Count'] = mexdf['Review Count'].astype(int)

#functions to use for series.map()

#convert dates to datetime object
def convert_dt(string):
    date_time_obj=datetime.strptime(string, '%Y-%m-%d %H:%M:%S' )
    return date_time_obj

#function to convert $$$ to length of price object
def convert_to_len(obj):
    if obj=='0':
        return 0
    else:
        return len(obj)
    
#convert data to datetime object and sort by date
df_review['Date'].map(convert_dt)
df_review = df_review.sort_values(by='Date',ascending=False)
    
#visuals functions
sns.set_style('darkgrid')

def rest_services_visual():
    #categorized pickup, delivery, and reservation types per df
    thai_pickup = thaidf[thaidf['Pickup']=='True'].count()['Name']
    thai_delivery = thaidf[thaidf['Delivery']=='True'].count()['Name']
    thai_reservation = thaidf[thaidf['Reservation']=='True'].count()['Name']

    mex_pickup = mexdf[mexdf['Pickup']=='True'].count()['Name']
    mex_delivery = mexdf[mexdf['Delivery']=='True'].count()['Name']
    mex_reservation = mexdf[mexdf['Reservation']=='True'].count()['Name']
    
    #Number of pairs 
    N = 3
    thai_bar = (thai_pickup, thai_delivery, thai_reservation)
    mex_bar = (mex_pickup, mex_delivery, mex_reservation)

    # # Position of bars on x-axis
    ind = np.arange(N)
    figure,axes=plt.subplots(figsize=(9,5))
    width = 0.3       

    plt.bar(ind, thai_bar , width, label= 'Thai Services')
    plt.bar(ind + width, mex_bar, width, label='Mexican Services')
    
    axes.set_xlabel('Restaurant Services')
    axes.set_ylabel('Number')
    axes.set_title('Thai vs. Mexican Services')

    # xticks()
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    axes.set_xticks(ind + width/ 2, ('Pickup', 'Delivery', 'Reservation'))
    axes.set_xticklabels(['','Pickup','', 'Delivery','', 'Reservation'])

    # Finding the best position for legends and putting it
    plt.legend(loc='best')
    return plt.show()

#convert price to number of dollar signs
thaidf['Price'] = thaidf['Price'].fillna('0')
thaidf['Price'] = thaidf['Price'].map(convert_to_len)
mexdf['Price'] = mexdf['Price'].fillna('0')
mexdf['Price'] = mexdf['Price'].map(convert_to_len)
    
def rest_price_visual():
    # categorize by price and plot count
    thai_price_0 = thaidf[thaidf['Price'] == 0].count()['Name']
    thai_price_1 = thaidf[thaidf['Price'] == 1].count()['Name']
    thai_price_2 = thaidf[thaidf['Price'] == 2].count()['Name']
    thai_price_3 = thaidf[thaidf['Price'] == 3].count()['Name']
    thai_price_4 = thaidf[thaidf['Price'] == 4].count()['Name']

    mex_price_0 = mexdf[mexdf['Price'] == 0].count()['Name']
    mex_price_1 = mexdf[mexdf['Price'] == 1].count()['Name']
    mex_price_2 = mexdf[mexdf['Price'] == 2].count()['Name']
    mex_price_3 = mexdf[mexdf['Price'] == 3].count()['Name']
    mex_price_4 = mexdf[mexdf['Price'] == 4].count()['Name']

    N = 5
    thai_price = (thai_price_0, thai_price_1, thai_price_2, thai_price_3, thai_price_4)
    mex_price = (mex_price_0, mex_price_1, mex_price_2, mex_price_3, mex_price_4)

    # # Position of bars on x-axis
    ind = np.arange(N)
    figure,axes=plt.subplots(figsize=(9,5))

    width = 0.3       

    plt.bar(ind, thai_price , width, label= 'Thai Restaurant Prices')
    plt.bar(ind + width, mex_price, width, label='Mexican Restaurant Prices')

    axes.set_xlabel('Restaurant Prices on Yelp')
    axes.set_ylabel('Number of Restaurants')
    axes.set_title('Thai vs. Mexican Prices')

    # # Finding the best position for legends and putting it
    plt.legend(loc='best')
    
    return plt.show()

def rating_box_and_whisk():
    fig, ax = plt.subplots()

    # Add a boxplot for the Rating column in the DataFrames
    ax.boxplot([thaidf['Rating'], mexdf['Rating']], vert=False)
    ax.set_title('Restaurant Ratings')

    # Add x-axis tick labels:
    ax.set_yticklabels(['Thai', "Mexican"])

    # Add a y-axis label
    ax.set_xlabel("Rating")
    return plt.show()

def rating_hist():
    fig, ax = plt.subplots()
    # Plot a histogram of Rating for thai restaurant
    ax.hist(thaidf['Rating'], label="Thai Rating", bins=5, histtype='step')
    # Compare to histogram of rating for mex restaurant
    ax.hist(mexdf['Rating'], label="Mexican Rating", bins=5, histtype='step')
    # Set the x-axis label to rating
    ax.set_xlabel('Rating')
    # Set the y-axis label to num of restaurants
    ax.set_ylabel('Number of Restaraunts')
    ax.set_title('Restaurant Rating')
    ax.legend(loc=2)
    return plt.show()

def high_performingrest_visual():
    #graphing ratings above 4 and review count above 100 for thai vs mex
    top_rated=df[df['Rating']>=4.5]
    top_rated=top_rated.sort_values('Review Count', ascending=False)
    top_rated_and_reviews=top_rated[top_rated['Review Count']>=100]

    high_mex = top_rated_and_reviews[top_rated_and_reviews['type']=='Mexican']
    high_thai = top_rated_and_reviews[top_rated_and_reviews['type']=='Thai']
    fig, ax = plt.subplots(figsize=(10,5))

    # Plot a bar-chart 
    ax.barh(['Thai', 'Mexican'], [high_thai.count()['Name'], high_mex.count()['Name']], color=('blue','orange'))

    # Set the y-axis tick labels 
    ax.set_yticklabels(['Thai', 'Mexican'])

    # Set the axis label
    ax.set_xlabel('Number of Restaurants')
    ax.set_ylabel("Restaurant Type")

    ax.set_title('High Performing Restaurants')
    
    return plt.show()
