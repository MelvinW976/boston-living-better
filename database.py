from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

DATETIME = 0
LATITUDE = 1
LONGITUDE = 2
CATEGORY = 3
ZIPCODE = 4

def convert_to_cosmos_time(time_in_py):
  return time_in_py.strftime("%Y-%m-%dT%H:%M:%S")

def data_between(start_time,end_time):
    start_time= convert_to_cosmos_time(start_time)
    end_time= convert_to_cosmos_time(end_time)
    query="SELECT * FROM c WHERE c.val[0] BETWEEN '{}%' AND '{}%'".format(start_time, end_time)
    return query

def category_data_between(start_time,end_time,category):
    start_time= convert_to_cosmos_time(start_time)
    end_time= convert_to_cosmos_time(end_time)
    query= "SELECT * FROM c WHERE (c.val[0] BETWEEN '{}%' AND '{}%') AND (c.val[3]='{}')".format(start_time, end_time, category)
    return query

def get_zip_counts(start_time,end_time,category):
    start_time= convert_to_cosmos_time(start_time)
    end_time= convert_to_cosmos_time(end_time)
    query = "Select Count(*) From c \
        where c.val[0] BETWEEN '{}%' and '{}%' \
        AND c.val[3] = '{}' \
        group by c.val[4]".format(start_time, end_time,category)
    return query
    
def past_concerns(zip_code, concern, currentTime, isMonth, num):
    start_time= convert_to_cosmos_time(start_time)
    end_time= convert_to_cosmos_time(end_time)
    end_time = currentTime #depends on the format
    if isMonth:
        start_time = end_time + relativedelta(months=-num) #depends on the format
        query= "Select Count(*) From C \
            Where c.dateTime BETWEEN '{}%' and '{}%' AND \
            c.concern = '{}' AND \
            c.zip_code = '{}' AND \
            group by left(c.date,7)".format(start_time,end_time,concern,zip_code)
    else:
        start_time = end_time + relativedelta(years=-num) #depends on the format
        query="Select Count(*) From C \
            Where c.dateTime BETWEEN '{}%' and '{}%' AND \
            c.concern = '{}' AND \
            c.zip_code = '{}' AND \
            group by left(c.date,4)".format(start_time,end_time,concern,zip_code)
    return query

if __name__ == '__main__':
    print("FETCHING DATA FROM YAHOO")