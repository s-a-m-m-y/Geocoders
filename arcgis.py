# Threading example
import time, thread
import csv
import sys
import urllib, json

token = '' #arc gis token
def parse_csv( field_name, input_csv_file, output_csv_file, missing_csv_file ):
    with open( input_csv_file ) as csv_file:
        with open( output_csv_file, 'wb' ) as out_csv_file:
            with open( missing_csv_file, 'wb' ) as miss_csv_file:
                reader = csv.DictReader(csv_file)
                writer = None
                miss = None
                for row in reader:
                    row['_lat'] = ''
                    row['_lng'] = ''
                    row['_location_type'] = ''

                    lat_lng = query_api( row[field_name] )
                    if lat_lng is not None:
                        try:
                          row['_lat'] = lat_lng['location']['lat']
                          row['_lng'] = lat_lng['location']['lng']
                          row['_location_type'] = ''.join(lat_lng['location_type'])

                          if writer is None:
                              writer = csv.DictWriter(out_csv_file, fieldnames=row.keys())
                              writer.writeheader()
                          writer.writerow(row)
                        except NameError:
                          row['_bad_request'] = 'exception';
                          if miss is None:
                              miss = csv.DictWriter(miss_csv_file, fieldnames=row.keys())
                              miss.writeheader()
                          miss.writerow(row)
                    else:
                        row['_bad_request'] = 'bad request'
                        if miss is None:
                            miss = csv.DictWriter(miss_csv_file, fieldnames=row.keys())
                            miss.writeheader()
                        miss.writerow(row)

def parse_api_results ( data ):
    print data
    for result_row in data['results'] :
        print result_row['types']
        print result_row['geometry']['location_type']
        if result_row['geometry']['location_type'] == "ROOFTOP" :
            return result_row['geometry']

def query_api( address ):
    url = 'http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/geocodeAddresses?addresses={"records":['
    url += '{"attributes":{"OBJECTID":1,"SingleLine": ' + address + '}},'
    url += ']}&token=' + token + '=pjson'
    print url
    try:
        response = urllib.urlopen( url )
        data = json.loads( response.read() )
        new_field_value = parse_api_results( data )
        return new_field_value
    except:
        return None;


if __name__ == "__main__":
    field_name = sys.argv[1]
    input_csv_file = sys.argv[2]
    output_csv_file = sys.argv[3]
    missing_csv_file = sys.argv[4]

    parse_csv( field_name, input_csv_file, output_csv_file, missing_csv_file)
