import pandas as pd
import time as time_obj
import functools
import constants
import numpy as np
import location_services


# ===================== Location Class ======================
class Location:
    lat = 0
    lon = 0
    loc_name = "Null"
    aliases = []

    # Constructor
    def __init__(self, lat=0, lon=0, loc_name="Null", aliases=[]):
        self.lat = lat
        self.lon = lon
        self.loc_name = loc_name
        self.aliases = [x.upper() for x in aliases]

    # Check if a string refers to this location
    def is_location(self, name: str) -> bool:
        return self.loc_name.upper() == name.upper() or name.upper() in self.aliases

    def get_coordinates(self):
        return self.lat, self.lon


# ============ MISC functions ===========================
# Converts csv lat lon into location objects
def convert_locations(dataframe):
    loc = []
    for index, entry in dataframe.iterrows():
        loc.append(Location(entry["Lat"], entry["Lon"], entry[constants.NAME]))
    dataframe[constants.LOCATION] = loc
    return dataframe.drop(["Lat", "Lon"], axis=1)


# Gets a list of location objects from the data frame
def get_locations(dataframe):
    return dataframe[constants.LOCATION]


# Deserialises the data frame from CSV
def retrieve_data_frame(filename):
    data = pd.read_csv(filename)
    return convert_locations(data)


# Formats an integer number(24 hour date format) into 12 hour date format as a string
def format_int_to_time(int_time):
    if int_time > 1200:
        return '{:.2f} PM'.format((int_time - 1200)/100)
    else:
        return '{:.2f} AM'.format(int_time/100)


# Formats an integer in meters into a string representing distance
def format_as_distance(int_dist):
    if int_dist > 1000:
        return '{:.1f} km'.format(int_dist/1000)
    else:
        return str(int_dist) + " m"


# Adds two columns to the dataframe denoting distance and directions
def add_distances_to_data(dataframe, loc: Location):
    # Copies the frame
    dataframe = dataframe.copy()
    loc_list = []
    directions = []
    # Calculates the distances and generates directions
    for index, entry in dataframe.iterrows():
        loc_list.append(entry[constants.LOCATION].get_coordinates())
        # Deprecated way of doing it
        # dist_list.append(location_services.get_distance(loc.get_coordinates(),
        # entry[constants.LOCATION].get_coordinates()))
        directions.append(location_services.get_directions_url(loc.get_coordinates(),
                                                               entry[constants.LOCATION].get_coordinates()))
    if len(loc_list) > 0:
        dist_list = location_services.distance_list(loc.get_coordinates(), loc_list)
        dataframe[constants.DISTANCE] = dist_list
        dataframe[constants.DIRECTIONS] = directions
    else:
        dataframe[constants.DIRECTIONS] = ""
        dataframe[constants.DISTANCE] = 0
    return dataframe


# ========================== INIT =================================================
# Creates data frame
data_set = retrieve_data_frame(constants.DICT_NAME)


# ================================ SORTING =======================================
# Function sorts data by comparator, takes in data, a primary and secondary(by default empty) predicate and a threshold
def sort_by_criteria(data, primary, secondary=None):
    data["primary"] = primary(data)
    if secondary is not None:
        data["secondary"] = secondary(data)
        data.sort_values(by=['primary'])
        data.sort_values(by=['secondary'])
        data.sort_values(by=['primary', 'secondary'])
        return data.sort_values(['primary', 'secondary']).drop(['primary', 'secondary'], axis=1)
    else:
        return data.sort_values(["primary"]).drop(['primary'], axis=1)


# Cheapest Price by food type(s) comparator
# (Generates a list with the food pricing of the canteen converted into an integer value)
def cheaper_price_criterion(food_types=constants.FOOD_TYPES, threshold=100):
    def func(dataframe):
        sort_list = []
        for index, i in dataframe.iterrows():
            min_x = float('inf')
            for f_type in food_types:
                # Compares the minimum price for this food type against current max
                type_x = i[f_type+"_min"]
                min_x = min(min_x, type_x if pd.notna(type_x) else float('inf'))
            sort_list.append(min_x*100 // threshold)
        return sort_list
    return func


# Best Rating by food type(s) comparator
# (Generates a list with the food rating of the canteen converted into an integer value)
def rating_criterion(food_type=constants.FOOD_TYPES, threshold=1):
    def func(dataframe):
        sort_list = []
        for index, i in dataframe.iterrows():
            max_x = float('-inf')
            for f_type in food_type:
                # Compares the minimum price for this food type against current max
                type_x = i[f_type+"_rating"]
                max_x = max(max_x, type_x if pd.notna(type_x) else float('-inf'))
            sort_list.append(max_x//threshold)
        return sort_list
    return func


# Distance comparator
# (Generates a list with the distance of the canteen from the current location converted into an integer value)
def distance_criterion(location: Location, threshold=200):
    def func(dataframe):
        if constants.DISTANCE not in dataframe.columns:
            dataframe = add_distances_to_data(dataframe, location)
        return dataframe[constants.DISTANCE] // threshold
    return func

# ==================================== FILTERING ============================================


# Type filter: filters by types of food
def type_filter(dataframe, food_types):
    dataframe = dataframe.copy()
    filt = []
    for f_type in food_types:
        # Checks if the minimum price for that food type is NA
        filt.append(dataframe[f_type + "_min"].notna())
    # Combines the food_type lists with logical OR to return a final predicate.
    # This denotes whether canteen has food of types user is interested in
    pred = functools.reduce(lambda x, y: x | y, filt)
    # Eliminate columns in the data frame not relevant to the context
    cols_to_eliminate = []
    non_types = np.setdiff1d(constants.TYPES, food_types)
    for f_type in non_types:
        cols_to_eliminate.append(f_type + "_min")
        cols_to_eliminate.append(f_type + "_max")
        cols_to_eliminate.append(f_type + "_rating")
    return dataframe[pred].drop(cols_to_eliminate, axis=1)


# Time filter: Filters by opening hours vs input time
def time_filter(dataframe, time=time_obj.localtime()):
    # Takes a subset of the main data frame, focusing on the opening hours
    dataframe = dataframe.copy()
    opening_hours = ["opt_o_daily", "opt_c_daily", "opt_o_6", "opt_c_6", "opt_o_7", "opt_c_7"]
    data_subset = pd.DataFrame(dataframe, columns=opening_hours)
    # Takes the 24H time
    cur = int(time[3]*100 + time[4])
    result = []
    open_h = []
    close_h = []
    # Checks what day of the week it is, and compares it against the opening hours for that day
    if 0 <= time[6] <= 4:
        for index, i in data_subset.iterrows():
            result.append(i["opt_o_daily"] < cur < i["opt_c_daily"])
            open_h.append(i["opt_o_daily"])
            close_h.append(i["opt_c_daily"])
    elif time[6] == 5:
        for index, i in data_subset.iterrows():
            result.append(i["opt_o_6"] < cur < i["opt_c_6"])
            open_h.append(i["opt_o_6"])
            close_h.append(i["opt_c_6"])
    else:
        for index, i in data_subset.iterrows():
            result.append(i["opt_o_7"] < cur < i["opt_c_7"])
            open_h.append(i["opt_o_7"])
            close_h.append(i["opt_c_7"])
    # Consolidates opening hours into two columns and drops the other columns
    dataframe["Open"] = open_h
    dataframe["Close"] = close_h
    return dataframe[result].drop(opening_hours, axis=1)


# Price-Type Filter: Filters by price per type of food can be called with None as food_types to get general result
def price_typed_filter(dataframe, min_price, max_price, food_types=constants.FOOD_TYPES):
    dataframe = dataframe.copy()
    filt = []
    # Iterates through all involved food types to check the price range of food
    for f_type in food_types:
        # Checks if the minimum price for that food type is less than budget
        price_filt = (dataframe[f_type + "_min"] <= max_price)
        # Removes ineligible columns from the result
        dataframe.loc[[not i for i in price_filt], [f_type+"_min", f_type+"_max", f_type+"_rating"]] = np.NaN
        filt.append(price_filt)
    # Combines the food_type lists using logical or to return a final boolean list
    pred = functools.reduce(lambda x, y: x | y, filt)
    return dataframe[pred]


# Best Rating by food type(s) comparator
# (Generates a list with the food rating of the canteen converted into an integer value)
def rating_typed_filter(dataframe, min_rating, food_types=constants.FOOD_TYPES):
    dataframe = dataframe.copy()
    filt = []
    # Iterates through all involved food types to check the rating for that type of food
    for f_type in food_types:
        # Checks if the minimum rating for that food type is above or equal to the min rating
        rating_filt = dataframe[f_type + "_rating"] >= min_rating
        # Removes ineligible columns from the result
        dataframe.loc[[not i for i in rating_filt], [f_type+"_min", f_type+"_max", f_type+"_rating"]] = np.NaN
        filt.append(rating_filt)
    # Combines the food_type lists using logical or to return a final boolean list
    pred = functools.reduce(lambda x, y: x | y, filt)
    return dataframe[pred]


# Distance Filter
def distance_filter(dataframe, loc: Location, max_dist):
    dataframe = dataframe.copy()
    if constants.DISTANCE not in dataframe.columns:
        dataframe = add_distances_to_data(dataframe, loc)
    return dataframe[dataframe[constants.DISTANCE] <= max_dist]


# ========================== QUERY ===========================================
# One Stop query endpoint (Distance is queried last because it is an external REST call(slower))
def receive_query(filters, pref, q_time, location):
    # ------------------------------- Initialise dataframe and food types -----------------------
    dataframe = data_set
    food_types = constants.TYPES
    # ----------------------------- FILTERING ----------------------------
    # OPENING HOURS
    dataframe = time_filter(dataframe, q_time)

    # FOOD TYPES
    if constants.FOOD_TYPES in filters:
        food_types = filters[constants.FOOD_TYPES]
        dataframe = type_filter(dataframe, food_types)

    # PRICE RANGE
    if constants.PRICE_RANGE in filters:
        dataframe = price_typed_filter(dataframe,
                                       filters[constants.PRICE_RANGE][0],
                                       filters[constants.PRICE_RANGE][1],
                                       food_types)

    # RATING
    if constants.MIN_RATING in filters:
        dataframe = rating_typed_filter(dataframe,
                                        filters[constants.MIN_RATING],
                                        food_types)

    # DISTANCE
    if constants.MAX_DIST in filters:
        dataframe = distance_filter(dataframe, location, filters[constants.MAX_DIST])

    if constants.DISTANCE not in dataframe.columns:
        dataframe = add_distances_to_data(dataframe, location)

    # ------------------------ SORTING ------------------------------
    # Primary Criterion
    if pref[0] == constants.DIST:
        primary_sort = distance_criterion(location)
    elif pref[0] == constants.PRICE:
        primary_sort = cheaper_price_criterion(food_types)
    else:
        primary_sort = rating_criterion(food_types)

    # Secondary Criterion
    if pref[1] == constants.DIST:
        secondary_sort = distance_criterion(location)
    elif pref[1] == constants.PRICE:
        secondary_sort = cheaper_price_criterion(food_types)
    elif pref[1] == constants.RATE:
        secondary_sort = rating_criterion(food_types)
    else:
        secondary_sort = None
    # Calls the sort
    dataframe = sort_by_criteria(dataframe, primary_sort, secondary_sort)
    return dataframe


# Makes a query but returns the result as a dictionary
def query_as_dictionary(filters, pref, q_time, location):
    # ----------------------- INIT VARIABLES ----------------------------------
    food_types = constants.TYPES
    if constants.FOOD_TYPES in filters:
        food_types = filters[constants.FOOD_TYPES]
    dataframe = receive_query(filters, pref, q_time, location)
    # Formats results as dictionary
    results = []
    for index, entry in dataframe.iterrows():
        canteen = {}
        canteen[constants.NAME] = entry[constants.NAME]
        canteen[constants.LOCATION] = entry[constants.LOCATION]
        canteen[constants.ADDRESS] = entry[constants.ADDRESS]
        canteen[constants.POSTAL] = str(entry[constants.POSTAL])
        canteen[constants.DISTANCE] = format_as_distance(entry[constants.DISTANCE])
        canteen[constants.DIRECTIONS] = entry[constants.DIRECTIONS]
        canteen[constants.OPENING] = (format_int_to_time(entry['Open']),
                                      format_int_to_time(entry['Close']))
        canteen[constants.STALLS] = str(entry[constants.STALLS])
        canteen[constants.CAPACITY] = str(entry[constants.CAPACITY])
        canteen[constants.FOOD] = {}
        for f_type in food_types:
            if pd.notna(entry[f_type+"_min"]):
                canteen[constants.FOOD][f_type] = {}
                canteen[constants.FOOD][f_type][constants.PRICE] = ('${:,.2f}'.format(entry[f_type+"_min"]),
                                                                    '${:,.2f}'.format(entry[f_type+"_max"]))
                canteen[constants.FOOD][f_type][constants.RATE] = str(entry[f_type+"_rating"]) + " / 10"
        results.append(canteen)
    return results
