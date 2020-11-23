import pandas as pd
import xml.etree.ElementTree as ET
import urllib
import json
import requests, zipfile, io


def get_element(tag, element_string):
    if tag.find(element_string) is None:
        element = 'None'
    else:
        element = tag.find(element_string).text

    return element


def parking_zones(split_zone_identifiers_list):
    length_element = len(split_zone_identifiers_list)

    if length_element > 1:
        list_zone_identifiers = split_zone_identifiers_list
    else:
        list_zone_identifiers = [split_zone_identifiers_list[0], 'None']
    return list_zone_identifiers


def str_cleaning_valid_time(string):
    string = string.replace('.', '')
    string = string.replace('to', '-')
    string = string.replace('\xa0', '')
    return string


def str_cleaning_permited_time(string):
    string = string.lstrip().rstrip()
    string = string.replace('.', '')

    string = string.replace('\xa0', '')
    string = string.replace('hours', 'hour')

    string = string.replace(' (delivery vehicles parking zone)', '')
    string = string.replace(' (delivery vehicle parking zone)', '')
    string = string.replace(' hour', '*60')
    string = string.replace(' mins', '')
    string = string.replace(' min', '')
    string = string.replace('None', '0')
    if string.endswith(r'(buses only)') or string.endswith(r'(busesonly)'):
        string = '0'
    return string


def str_cleaning_area_between(string):
    string = string.lstrip().rstrip().lower()
    string = string.replace('\xa0', '')
    string = string.replace('a point ', '').replace('thereof', '')

    return string


def import_dataset():

    '''
    This pulls in and processes the raw dataset directly from the toronto open data platform

    :return:
    '''

    url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
    params = { "id": "72040958-e532-46f7-9228-8d07b4677a2b"}
    response = urllib.request.urlopen(url, data=bytes(json.dumps(params), encoding="utf-8"))
    package = json.loads(response.read())

    zip_file_url = package['result']['resources'][0]['url']

    r = requests.get(zip_file_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()

    root = ET.parse('Ch_950_Sch_15_ParkingForRestrictedPeriods.xml').getroot()

    raw_id = []
    raw_street = []
    raw_side = []
    raw_between = []
    raw_time = []
    raw_max_time = []

    for tag in root.findall('Ch_950_Sch_15_ParkingForRestrictedPeriods'):
        raw_id.append(get_element(tag,'ID'))
        raw_street.append(get_element(tag,'Highway'))
        raw_side.append(get_element(tag,'Side'))
        raw_between.append(get_element(tag,'Between'))
        raw_time.append(get_element(tag,'Times_and_or_Days'))
        raw_max_time.append(get_element(tag,'Maximum_Period_Permitted'))

    import_df = pd.DataFrame({
        'ID':raw_id ,
        'street':raw_street ,
        'park_side':raw_side ,
        'area_between':raw_between ,
        'valid_time':raw_time ,
        'permited_time':raw_max_time
    })

    np_df = import_df[import_df.park_side.isna()].copy()
    raw_df = import_df[~import_df.park_side.isna()].copy()


    raw_df['permited_time_mins']= raw_df.permited_time.apply(lambda x:str_cleaning_permited_time(x)).copy()
    raw_df.permited_time_mins = raw_df.permited_time_mins.apply(lambda x: eval(x))

    split_zones = raw_df.area_between.apply(lambda x: str_cleaning_area_between(x)).str.split('and')

    raw_df['start_zone'] = split_zones.apply(lambda x: parking_zones(x)[0])
    raw_df['end_zone'] = split_zones.apply(lambda x: parking_zones(x)[1])

    return raw_df