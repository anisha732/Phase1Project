import pandas as pd
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
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
    # your code to open the csv file, concat the current data, and save the data. 
    business_df = pd.DataFrame(parsed_results, columns = ['Id','Name', 'Location', 'Rating', 'Price', 'Zipcode', 'Pickup', 'Delivery', 'Reservation', 'Review Count', 'Categories','Status'])
    x = business_df.to_csv(csv_file_path, mode = 'a')
    return x

#Review Data functions

def yelp_call_rev(url_params, given_df):
    responses=[]
    for business in list(given_df['Id']):
        url = 'https://api.yelp.com/v3/businesses/{}/reviews'.format(business)
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

#functions to use for series.map()

def convert_dt(string):
    date_time_obj=datetime.strptime(string, '%Y-%m-%d %H:%M:%S' )
    return date_time_obj

def convert_to_len(obj):
    if obj=='0':
        return 0
    else:
        return len(obj)
    
#visuals functions
def rest_services_visual():
    thai_pickup = thaidf[thaidf['Pickup']=='True'].count()['Name']
    thai_delivery = thaidf[thaidf['Delivery']=='True'].count()['Name']
    thai_reservation = thaidf[thaidf['Reservation']=='True'].count()['Name']

    mex_pickup = mexdf[mexdf['Pickup']=='True'].count()['Name']
    mex_delivery = mexdf[mexdf['Delivery']=='True'].count()['Name']
    mex_reservation = mexdf[mexdf['Reservation']=='True'].count()['Name']

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
    
