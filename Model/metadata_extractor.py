import os
from exiftool import ExifToolHelper
from PIL import ExifTags
from pillow_heif import register_heif_opener
from geopy.geocoders import Nominatim
from datetime import datetime

register_heif_opener()


class MetadataExtractor:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="omniquery")

    def convert_gps_to_degree(self, gps):
        gps = eval(gps)
        d, m, s = gps[0], gps[1], gps[2]
        return d + (m / 60.0) + (s / 3600.0)

    def get_time_of_the_day(self, hour):
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 18:
            return "Afternoon"
        elif 18 <= hour < 23:
            return "Evening"
        else:
            return "Night"

    def parse_date_time(self, exif=None, date_time_string=""):
        if not date_time_string:
            date_time = exif.get('DateTime') or exif.get('DateTimeOriginal')
            if not date_time:
                return None
        else:
            date_time = date_time_string

        date_time = date_time.replace('PM', '') if 'PM' in date_time else date_time
        date_time_object = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
        day_of_week = date_time_object.strftime('%A')
        time_of_the_day = self.get_time_of_the_day(date_time_object.hour)

        return {
            'date_string': date_time,
            'day_of_week': day_of_week,
            'time_of_the_day': time_of_the_day,
        }


    # Extracts the file’s last modification time as a backup if EXIF data is missing.
    def extract_date_time_modified(self, filepath):
        modification_time = os.path.getmtime(filepath)
        return datetime.fromtimestamp(modification_time).strftime('%Y:%m:%d %H:%M:%S')

    def read_GPS_from_image(self, image):
        image_info = image.getexif().get_ifd(0x8825)

        geo_tagging_info = {}
        # mapping keys in image info to these readable ones
        gps_keys = ['GPSVersionID', 'GPSLatitudeRef', 'GPSLatitude', 'GPSLongitudeRef', 'GPSLongitude',
                'GPSAltitudeRef', 'GPSAltitude', 'GPSTimeStamp', 'GPSSatellites', 'GPSStatus', 'GPSMeasureMode',
                'GPSDOP', 'GPSSpeedRef', 'GPSSpeed', 'GPSTrackRef', 'GPSTrack', 'GPSImgDirectionRef',
                'GPSImgDirection', 'GPSMapDatum', 'GPSDestLatitudeRef', 'GPSDestLatitude', 'GPSDestLongitudeRef',
                'GPSDestLongitude', 'GPSDestBearingRef', 'GPSDestBearing', 'GPSDestDistanceRef', 'GPSDestDistance',
                'GPSProcessingMethod', 'GPSAreaInformation', 'GPSDateStamp', 'GPSDifferential']
        for k, v in image_info.items():
            try:
                geo_tagging_info[gps_keys[k]] = str(v)
            except IndexError:
                pass

        if geo_tagging_info == {}:
            return {}
        # GPSLatitude, GPSLongitude -> (degrees, minutes, seconds)
        latitude_ref = geo_tagging_info['GPSLatitudeRef']
        latitude = geo_tagging_info['GPSLatitude']
        latitude = self.convert_gps_to_degree(latitude)
        if latitude_ref == 'S':
            latitude = -latitude
        longitude_ref = geo_tagging_info['GPSLongitudeRef']
        longitude = geo_tagging_info['GPSLongitude']
        longitude = self.convert_gps_to_degree(longitude)
        if longitude_ref == 'W':
            longitude = -longitude

        gps = (latitude, longitude)
        # Getting address
        geolocator = Nominatim(user_agent="omniquery")
        location = geolocator.reverse(f"{latitude}, {longitude}")
        address = location.address
        address_split = address.split(', ')
        address_split.reverse()

        location_info = {}
        location_info['gps'] = gps
        location_info['address'] = address

        label_list = ['country', 'zip', 'state', 'county', 'city']
        for i, label in enumerate(label_list):
            if i >= len(address_split):
                break
            location_info[label] = address_split[i]

        return location_info

    def read_metadata_from_image(self, image, filepath="", latitude=None, longitude=None):
        try:
            exif_info = image._getexif()
        except:
            exif_info = image.getexif()
        # For mapping names
        exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_info.items()}
        if 'GPSInfo' in exif:
            gps_data = self.read_GPS_from_image(image)
            capture_method = 'photo'
        else:
            gps_data = {}
            if 'UserComment' in exif:
                user_comment = exif['UserComment']
                if 'Screenshot' in user_comment.decode('utf-8'):
                    capture_method = 'screenshot'
                #### ==================== Added ====================
                else:
                    capture_method = 'unknown'
            else:
                capture_method = 'unknown'


        if 'DateTimeOriginal' in exif or 'DateTime' in exif:
            temporal_data = self.parse_date_time(exif)
        else:
            date_time = self.extract_date_time_modified(filepath)
            temporal_data = self.parse_date_time(exif=None, date_time_string=date_time)

        if gps_data == {} and longitude and latitude:
            print("Given GPS data")
            gps_data = self.__read_location_given_lat_long(latitude , longitude)

        return {
            'temporal_info': temporal_data,
            'location': gps_data,
            'capture_method': capture_method,
        }

    def parse_date_time_exiftool(self, date_time):
          if 'PM' in date_time:
              date_time = date_time.replace('PM', '')
          if 'AM' in date_time:
              date_time = date_time.replace('AM', '')
          if '-' in date_time:
              date_time = date_time.split('-')[0]
          if '+' in date_time:
              date_time = date_time.split('+')[0]

          if '上午' in date_time:
              date_time = date_time.split('上午')[0]
          if '下午' in date_time:
              date_time = date_time.split('下午')[0]

          year = date_time.split(':')[0]
          month = date_time.split(':')[1]
          day_hour = date_time.split(':')[2]
          day = day_hour.split(' ')[0]
          hour = day_hour.split(' ')[1]
          minute = date_time.split(':')[3]
          second = date_time.split(':')[4]
          second = second[:2]

          date_time = f"{year}:{month}:{day} {hour}:{minute}:{second}"



          date_time_object = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
          day_of_week = date_time_object.strftime('%A')
          time_of_the_day = self.get_time_of_the_day(date_time_object.hour)

          date_info = {
              'date_string': date_time,
              'day_of_week': day_of_week,
              'time_of_the_day': time_of_the_day
          }
          return date_info

    def read_gps_from_metadata_exiftool(self, metadata):
          gps = metadata[0].get('Composite:GPSPosition', None)
          if gps is None:
              return {}
          gps_latitude = metadata[0].get('Composite:GPSLatitude', None)
          gps_longitude = metadata[0].get('Composite:GPSLongitude', None)
          gps = (gps_latitude, gps_longitude)
          geolocator = Nominatim(user_agent="omniquery")
          location = geolocator.reverse(f"{gps_latitude}, {gps_longitude}")
          address = location.address
          address_split = address.split(', ')
          address_split.reverse()

          location_info = {}
          location_info['gps'] = gps
          location_info['address'] = address

          label_list = ['country', 'zip', 'state', 'county', 'city']
          for i, label in enumerate(label_list):
              if i >= len(address_split):
                  break
              location_info[label] = address_split[i]
          return location_info

    def read_capture_method_from_metadata_exiftool(self, metadata):
          meta = metadata[0]
          if 'image' in meta.get('File:MIMEType', ''):
              if 'EXIF:Model' in meta:
                  model = meta['EXIF:Model']
                  return 'photo'
              elif 'EXIF:UserComment' in meta:
                  user_comment = meta['EXIF:UserComment']
                  if 'Screenshot' in user_comment:
                      return 'screenshot'
                  else:
                      return 'unknown'
              return 'unknown'
          else:
              return 'video'


    def read_metadata_from_image_exiftool(self, image_path, latitude=None, longitude=None):
          with ExifToolHelper() as et:
              metadata = et.get_metadata(image_path)
              date = metadata[0].get('EXIF:DateTimeOriginal', None)
              if date is None:
                  date = metadata[0].get('EXIF:DateTime', None)
              if date is None:
                  date = metadata[0].get('File:FileModifyDate', None)

              date_info = self.parse_date_time_exiftool(date)

              try:
                  location_info = self.read_gps_from_metadata_exiftool(metadata)
                  #################################################
                  if location_info == {} and longitude and latitude:
                      location_info = self.__read_location_given_lat_long(latitude, longitude)
                      
              except Exception as e:
                  print(e)
                  location_info = {}
              capture_method = self.read_capture_method_from_metadata_exiftool(metadata)

              metadata_result = {
                  'temporal_info': date_info,
                  'location': location_info,
                  'capture_method': capture_method
              }
              return metadata_result

    def read_metadata_from_video(self, video_path):
          with ExifToolHelper() as et:
              metadata = et.get_metadata(video_path)
              date = metadata[0].get('QuickTime:CreationDate', None)

              if date is None:
                  date = metadata[0].get('File:FileModifyDate', None)

              date_info = self.parse_date_time_exiftool(date)
              location_info = self.read_gps_from_metadata_exiftool(metadata)
              capture_method = self.read_capture_method_from_metadata_exiftool(metadata)

              duration = metadata[0].get('QuickTime:Duration', None)
              fps = metadata[0].get('QuickTime:VideoFrameRate', None)

              metadata_result = {
                  'temporal_info': date_info,
                  'location': location_info,
                  'capture_method': capture_method,
                  'duration': duration,
                  'fps': fps,
              }
              return metadata_result
          
    def __read_location_given_lat_long(self, latitude, longitude):
        gps = (latitude, longitude)
        # Getting address
        geolocator = Nominatim(user_agent="omniquery")
        location = geolocator.reverse(f"{latitude}, {longitude}")
        address = location.address
        address_split = address.split(', ')
        address_split.reverse()

        location_info = {}
        location_info['gps'] = gps
        location_info['address'] = address

        label_list = ['country', 'zip', 'state', 'county', 'city']
        for i, label in enumerate(label_list):
            if i >= len(address_split):
                break
            location_info[label] = address_split[i]
        return location_info

