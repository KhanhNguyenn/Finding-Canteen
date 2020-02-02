import time
import pickle
import constants
import data
import location_services

# ================== User Dictionary =====================

# Initialises the User Dictionary
users = {}


# Serialises the User Dictionary to a file
def serialise_users(filename):
    binary_file = open(filename+".bin", mode='wb')
    pickle.dump(users, binary_file)
    binary_file.close()


# Deserialises the User Dictionary from a file
def deserialise_users(filename):
    try:
        binary_file = open(filename+".bin", mode='rb')
        global users
        users = pickle.load(binary_file)
        binary_file.close()
    # If file does not exist, make the file
    except FileNotFoundError:
        serialise_users(filename)


# ========================= User Profile Class ========================
class UserProfile:
    # ============== Variables =============================
    # Set Up Boolean
    is_setting_up = True
    # User Location
    location = None
    # User-Specified Time(defaulted to time of query if None)
    current_time = None
    # User sorting preferences
    pref = (constants.DIST, constants.PRICE)
    # User filter preferences
    filters = {constants.MAX_DIST: float("inf"),
               constants.PRICE_RANGE: (0, float("inf")),
               constants.MIN_RATING: 0,
               constants.FOOD_TYPES: []}

    results = []
    index = 0
    # ==================== Functions ============================

    # Constructor (Serialises the user dictionary
    def __init__(self):
        serialise_users(constants.FILENAME)

    # Returns the relevant filters for query
    def get_filters(self):
        filt = {}
        if not self.filters[constants.MAX_DIST] == float("inf"):
            filt[constants.MAX_DIST] = self.filters[constants.MAX_DIST]
        if not self.filters[constants.PRICE_RANGE] == (0, float("inf")):
            filt[constants.PRICE_RANGE] = self.filters[constants.PRICE_RANGE]
        if not self.filters[constants.MIN_RATING] == 0:
            filt[constants.MIN_RATING] = self.filters[constants.MIN_RATING]
        if len(self.filters[constants.FOOD_TYPES]) > 0:
            filt[constants.FOOD_TYPES] = self.filters[constants.FOOD_TYPES]
        return filt

    # Returns the filters as a string
    def print_filters(self):
        filt = self.get_filters()
        result = ""
        if filt.__contains__(constants.MAX_DIST):
            result += "Maximum Distance: " + str(filt[constants.MAX_DIST]) + "m\n"
        if filt.__contains__(constants.PRICE_RANGE):
            result += "Price: Under $" + str(filt[constants.PRICE_RANGE][1]) + "\n"
        if filt.__contains__(constants.MIN_RATING):
            result += "Minimum Food Rating: " + str(filt[constants.MIN_RATING]) + "\n"
        if filt.__contains__(constants.FOOD_TYPES):
            result += "Types of food: " + str(filt[constants.FOOD_TYPES]) + "\n"
        if result == "":
            result = "No Filters"
        return result

    # Returns a string representing the user profile
    def to_string(self):
        # Sets the query day
        day = self.current_time[6] if self.current_time is not None else 0
        if day == 0:
            day = "Monday"
        elif day == 1:
            day = "Tuesday"
        elif day == 2:
            day = "Wednesday"
        elif day == 3:
            day = "Thursday"
        elif day == 4:
            day = "Friday"
        elif day == 5:
            day = "Saturday"
        elif day == 6:
            day = "Sunday"

        # Returns the string
        return (("*Location:* " + self.location.loc_name + "\n") if self.location is not None else "") + \
               (("*Time:* " + day + " " + data.format_int_to_time(self.current_time[3]*100+self.current_time[4])
                + "\n") if self.current_time is not None else "")\
                + "*Sort by:* " + str(self.pref) + \
                "\n*Filters:* \n" + self.print_filters()

    # ==================== QUERIES AND RESULTS =========================================
    # Queries the data frame
    def query(self):
        result_string = ""
        c_time = self.current_time
        loc = self.location
        if c_time is None:
            c_time = time.localtime()
            result_string += "Time defaulted to " + time.ctime() + "!\n"
        if loc is None:
            loc = location_from_text("North Spine")
            result_string += "Location defaulted to " + loc.loc_name + "!\n"
        result = data.query_as_dictionary(self.get_filters(), self.pref, c_time, loc)
        self.results = result
        self.index = 0
        return result_string, result

    # Returns a result entry as a list of strings
    def entry_as_str(self):
        if len(self.results) == 0:
            return ["No Results Found... Maybe you are too picky... :("]
        else:
            entry = self.results[self.index]
            res = ""\
                  + ("_Entry " + str(self.index + 1) + " of " + str(len(self.results)) + "_\n")\
                  + ("*" + entry[constants.NAME] + "*\n")\
                  + ("*Location:* " + entry[constants.LOCATION].loc_name + "\n")\
                  + ("*Address:* " + entry[constants.ADDRESS] + " Singapore " + entry[constants.POSTAL] + "\n")\
                  + ("*Distance:* " + entry[constants.DISTANCE]+"\n")\
                  + ("*Getting There:* [Map](" + entry[constants.DIRECTIONS] + ")\n")\
                  + ("*Open from:* " + entry[constants.OPENING][0] + " to " + entry[constants.OPENING][1] + "\n")\
                  + ("*No. of Stalls:* " + entry[constants.STALLS] + "\n")\
                  + ("*Seating Capacity:* " + entry[constants.CAPACITY] + "\n")\
                  + "*FOOD*\n"
            for food_type, food_data in entry[constants.FOOD].items():
                res += ("*~"+food_type+"~*\n")
                res += ("*Rating:* " + food_data[constants.RATE] + "\n")
                res += ("*Price Range:* " + food_data[constants.PRICE][0]
                        + " to " + food_data[constants.PRICE][1] + "\n\n")
            return res

    # Advances to the next entry(returns a string of the next entry)
    def next_entry(self):
        if len(self.results) == 0:
            return ["No Results Found... Maybe you are too picky... :("]
        else:
            self.index += 1
            if self.index >= len(self.results):
                self.index = 0
        return self.entry_as_str()

    # Goes back to the previous entry(returns a string of the previous entry)
    def prev_entry(self):
        if len(self.results) == 0:
            return ["No Results Found... Maybe you are too picky... :("]
        else:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.results) - 1
        return self.entry_as_str()

    # Attempts to set the index. Returns true if successful
    def set_index(self, new_index):
        if 0 <= new_index <= (len(self.results) - 1):
            self.index = new_index
            return True
        else:
            return False

    # ================== Setters ==========================

    # Sets Location from values and serialises
    def set_location_values(self, lat, lon, loc_name):
        self.location = data.Location(lat, lon, loc_name)
        serialise_users(constants.FILENAME)

    # Set Location from location
    def set_location(self, loc: data.Location):
        self.location = loc
        serialise_users(constants.FILENAME)

    # Sets Query Day and serialises
    def set_day(self, day):
        if self.current_time is None:
            self.current_time = [0, 0, 0, 0, 0, 0, day, 0, 0]
        else:
            self.current_time[6] = day
        serialise_users(constants.FILENAME)

    # Sets Query Time and serialises
    def set_time(self, ctime):
        hour = ctime//100
        minute = ctime % 100
        if self.current_time is None:
            self.current_time = [0, 0, 0, hour, minute, 0, 0, 0, 0]
        else:
            self.current_time[3] = hour
            self.current_time[4] = minute
        serialise_users(constants.FILENAME)

    # Clears Query Time and serialises
    def clear_time(self):
        self.current_time = None
        serialise_users(constants.FILENAME)

    # Sets Preferences and serialises
    def set_pref(self, pri_pref=None, sec_pref=None):
        if pri_pref is None:
            pri_pref = self.pref[0]
        self.pref = (pri_pref, sec_pref)
        serialise_users(constants.FILENAME)

    # Sets Filters and serialises
    def set_filter(self, key, value=None, max=None):
        # Input checking
        if value is not None and ((value < 0) or (key == constants.MIN_RATING and value > 10)):
            return False
        if max is not None and max < 0:
            return False

        # Special Case for Price Range Tuple
        if key in self.filters:
            if key == constants.PRICE_RANGE:
                if value is None:
                    self.filters[constants.PRICE_RANGE] = (self.filters[constants.PRICE_RANGE][0], max)
                if max is None:
                    self.filters[constants.PRICE_RANGE] = (value, self.filters[constants.PRICE_RANGE][1])
                else:
                    self.filters[constants.PRICE_RANGE] = (value, max)
            else:
                self.filters[key] = value
            serialise_users(constants.FILENAME)
        else:
            raise KeyError(key + " was not found in User Filters Dictionary!")

        return True

    # Toggles Food Type and serialises (Returns true if it was an addition operation and false if it was removal
    def toggle_type(self, type):
        addition = True
        if type in constants.TYPES:
            if type in self.filters[constants.FOOD_TYPES]:
                self.filters[constants.FOOD_TYPES].remove(type)
                addition = False
            else:
                self.filters[constants.FOOD_TYPES].append(type)
            serialise_users(constants.FILENAME)
            return addition
        else:
            raise ValueError(type + " does not exist!")

    # Adds all food types and serialises
    def add_all_types(self):
        self.filters[constants.FOOD_TYPES] = constants.TYPES.copy()
        serialise_users(constants.FILENAME)

    # Removes all food types and serialises
    def remove_all_types(self):
        self.filters[constants.FOOD_TYPES] = []
        serialise_users(constants.FILENAME)

    # Serialises the user
    def __getstate__(self):
        return self.__dict__,pickle.dumps(self.filters)

    # Deserialises the user
    def __setstate__(self, state):
        self.__dict__ = state[0]
        self.filters = pickle.loads(state[1])

# ====================== Misc Functions =====================


# Getter for a user
def get_user(iden) -> UserProfile:
    if iden not in users:
        users[iden] = UserProfile()
        serialise_users(constants.FILENAME)
    return users[iden]


# Reset user
def reset_user(iden):
    users[iden] = UserProfile()
    serialise_users(constants.FILENAME)


# Location mapping function
def location_from_text(text):
    loc = location_services.place_from_name(text)
    if loc[0] is not None:
        return data.Location(lat=loc[1], lon=loc[2], loc_name=loc[0])
    else:
        return None


# ========================== Called when mediator is starting up ========================
deserialise_users(constants.FILENAME)

