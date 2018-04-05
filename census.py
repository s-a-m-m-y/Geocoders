# Threading example
import time, thread
import csv
import sys
import requests, json

def parse_csv( field_name, input_csv_file, output_csv_file ):
    with open( input_csv_file ) as csv_file:
        with open( output_csv_file, 'wb' ) as out_csv_file:
            reader = csv.DictReader(csv_file)
            writer = None
            for row in reader:
                if 'google url' not in row:
                    row['census url'] = ""
                if '_geocode_status' in row and (
                   row['_geocode_status'] == 'Exception' or
                   row['_geocode_status'] == 'Ok'
                ):
                    if writer is None:
                        keys = row.keys()
                        keys.sort()
                        writer = csv.DictWriter( out_csv_file, fieldnames=list(keys) )
                        writer.writeheader()
                    writer.writerow(row)
                    continue
                row['_lat'] = ''
                row['_lng'] = ''
                row['_location_type'] = ''
                row['_geocode_status'] = 'Ok'

                lat_lng = query_api( row[field_name] )
                row['census url'] = lat_lng['url']
                row['_geocode_status'] = lat_lng['geocode_status']
                if lat_lng['result'] is not None:
                    try:
                      row['_lat'] = lat_lng['result']['y']
                      row['_lng'] = lat_lng['result']['x']
                      row['_location_type'] = 'ROOFTOP' # Hardcoding this - it matches google.py's location_type
                      if writer is None:
                          keys = row.keys()
                          keys.sort()
                          writer = csv.DictWriter( out_csv_file, fieldnames=list(keys) )
                          writer.writeheader()
                      writer.writerow(row)
                    except NameError:
                      row['_geocode_status'] = 'Exception'
                      if writer is None:
                          keys = row.keys()
                          keys.sort()
                          writer = csv.DictWriter( out_csv_file, fieldnames=list(keys) )
                          writer.writeheader()
                      writer.writerow(row)
                else:
                    if '_geocode_status' not in row:
                        row['_geocode_status'] = 'Bad Request'
                    if writer is None:
                        keys = row.keys()
                        keys.sort()
                        writer = csv.DictWriter( out_csv_file, fieldnames=list(keys) )
                        writer.writeheader()
                    writer.writerow(row)

def parse_api_results ( data ):
    for result_row in data['result']['addressMatches'] :
        if (result_row['coordinates']):
            return result_row['coordinates']
    return None

def query_api( address ):
    url = 'https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?&benchmark=4&format=json&address=' + address
    try:
        response = requests.get(url)
        data = response.json()
        new_field_value = parse_api_results( data )
        if new_field_value is None:
            return {'url': url, 'result': None, 'geocode_status': 'Failed to geocode'}
        else:
            return {'url': url, 'result': new_field_value, 'geocode_status': 'Ok'}
    except Exception as ex:
        print ex
        return {'url': url, 'result': None, 'geocode_status': 'Failed to geocode'}

if __name__ == "__main__":
    field_name = sys.argv[1]
    input_csv_file = sys.argv[2]
    output_csv_file = sys.argv[3]

    parse_csv( field_name, input_csv_file, output_csv_file)
