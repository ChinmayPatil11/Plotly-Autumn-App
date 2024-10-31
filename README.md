# Plotly-Autumn-App

This is a dashboard showcasing analysis of Michelin Restaurants around the world. It was created as a part of Plotly Autumn App Challenge. 

## Features
There are 2 tabs available, both having a different kind of theme.

### General Analysis

This displays Michelin star restaurants across the world through a scatter map plot. There are 3 aspects on which the restaurants can be filtered:  
1. Star Rating  
This is the rating of a restaurant. Multiple values can be selected from the below list.
- 1 Star  
- 2 Stars  
- 3 Stars  
- Bib Gourmand  
- Selected Restaurant  

2. Country  
One can select a particular country to check out the restaurants in only a particular country. Currently it focuses on 8 countries which have most number of Michelin Star Restaurants.

3. Cuisine
To get restaurants of only your favourite cuisines type, you can select the types from this dropdown and it will filter restaurants which serve your selected types. Multiple selection is possible as well.  

These filters can be used together for locating your restaurants of choice. The number of restaurants available for above inputs is displayed in the 'Restaurants Available' box. If any combination of filter yields no result, it returns 0 and asks for changing any of the above 3 parameters.

To know more about a restaurant, you can just click on it and its information will be shown along with its website.  

### City Analysis

As a city enthusiast, One can always wonder what else can be done alongside visiting a restaurant. Travelling around the city to see some monuments and places of interest is always fun, this section helps in that.  
The data is created using osmnx library for getting all places of interests in the city. Currently 3 cities are mapped
1. Paris, France
2. London, UK
3. New York, USA

Just click on any restaurant displayed. It will fill up a table with the nearest locations of interests and monuments that one can visit.


## Run Locally
```
pip install -r requirements.txt
python dash_app.py
```

Your Dashboard should be running on ```127.0.0.1:8050```. Open a Browser and paste the link to check it working