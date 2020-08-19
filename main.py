'''
ESA  Astro Pi Mission Space Lab Challenge 2019/2020

"Life on Earth" Experiment - Astro Pi Izzy

Team Name: Space Kludgers
Mentor: Eleni Kaldoudi
Students: Nefeli Zikou, Melina Zikou, George Stouraitis, Vissarion Christodoulou

Space Kludgers to Investigate Correlations of Astro Pi Izzy Image Datasets 
and a Variety of Atmospheric and Anthropogenic Parameters Provided by ESA and NASA.
'''

from picamera import PiCamera
import os
from sense_hat import SenseHat

import time
import datetime
from time import sleep
from datetime import timedelta
from datetime import datetime

import ephem
from ephem import degree

import logging
import logzero
from logzero import logger
import csv

#-------------------------------#

def is_the_sun_up(lat, lon, time): 
    '''
    Calculates if it's day or night in the region where 
    the ISS is according to its location and time.

    Using pyephem library, it creates an Observer standing at the location where ISS is,
    and then checks the altitute of the Sun. If it is above surface, then it is day, else night.

    Code attribution: 1. https://gis.stackexchange.com/questions/270764/calculate-if-day-night-time-for-point-dataset
                      2. https://rhodesmill.org/pyephem/quick.htm
    '''
    iss_observer = ephem.Observer()
    iss_observer.pressure = 0
    iss_observer.horizon = "-0.34"

    iss_observer.long = lon
    iss_observer.lat = lat
    iss_observer.date = time

    sun = ephem.Sun()
    sun.compute(iss_observer)

    # If sun.alt > 0 => The sun is above the horizon so it's day
    # If sun.alt < 0 => The sun is below the horizon so it's night
    return sun.alt > 0 

def photo_capture_delay(day):
    '''
    This function sets a slower caprute rythm if it's night because the photos 
    could be totaly dark and non-viable for processing.
    This helps us achieve a greater density of useful data in the used memory 
    and capture the whole course of ISS.

    After conducting some experiments we concluded that 
    a good photo size to assume for the day is 3077 KB,
    and during the night 1000 KB.
    We used those numbers to calculate the capture rates 
    which we are using, in order to get as many photos as possible
    while not exceeding the memory space.

    The program runs for a total of 180 minutes, 90 minutes in the day and 90 minutes at night, or 5.400s each.
    We take a photo every 7 seconds in the day (~771 day-photos) and 20 seconds in the night (~270 night-photos).
    So the photos will take up approximately 771*3077 + 270*1000 = 2,642,367 KB ~ 2.6 GB < 3 GB

    The remaining memory space is sufficient enough for our log and CSV files and any photos larger than predicted. 
    '''
    if day == True:
        delay = 7

    else:    
        delay = 20

    logger.info("Delay till next photo %s", delay)
    sleep(delay)

def write_photo_metadata():
    '''
    Adds the longitude and latitude as GPS exif details to the photo's metadata, analysis at a later date.
    '''
    global camera

    try:
        #Longitude exif data
        lon = [float(i) for i in str(iss.sublong).split(":")]

        if lon[0] < 0:

            lon[0] = abs(lon[0])
            camera.exif_tags['GPS.GPSLongitudeRef'] = "W"

        else:
            camera.exif_tags['GPS.GPSLongitudeRef'] = "E"

        camera.exif_tags['GPS.GPSLongitude'] = '%d/1,%d/1,%d/10' % (lon[0], lon[1], lon[2]*10)

        #Latitude exif data
        lat = [float(i) for i in str(iss.sublat).split(":")]

        if lat[0] < 0:

            lat[0] = abs(lat[0])
            camera.exif_tags['GPS.GPSLatitudeRef'] = "S"

        else:
            camera.exif_tags['GPS.GPSLatitudeRef'] = "N"

        camera.exif_tags['GPS.GPSLatitude'] = '%d/1,%d/1,%d/10' % (lat[0], lat[1], lat[2]*10) 

    except Exception as e:
        logger.error('{}: {})'.format(e.__class__.__name__, e))
        logger.error("Error: " + str(e))   

def write_photo(photo_num):
    '''
    captures current photo to disk using provided filename number
    '''
    global camera

    #Turns the photo number into a string so as to fit in the filename of the photo
    photo_num_str = str(photo_num)

    #Saves info to the log file
    logger.info("Capturing photo number: %s", photo_num)

    #Takes photo with Izzy's camera 
    #jpeg quality: Sets the compression of the image - Auto is 85/100 - set to 100 => The photo is lossless
    photo_file = path + "/image_"+ photo_num_str.zfill(3) + ".jpg"
    camera.capture(photo_file, "jpeg", quality = 100)

    #Saves info to the log file
    logger.info("captured photo using file %s", photo_file)



def collect_sensehat_data(datetime_now, day, lontitude, latitude, photo_num):
    '''
    Collects interesting Sense Hat data, such as temperature, humidity, pressure, compass, orientation, gyroscope, accelerometer.
    Returns a vector of all the data.

    They are not really needed for our experiement but we collect them in case that these prove useful, or that they prove useful
    as a data set to somebody else.
    '''
    try:
        temperature = sense.get_temperature()
        humidity = sense.get_humidity()
        pressure = sense.get_pressure()

        orientation_rad = sense.get_orientation_radians()
        roll_rad = orientation_rad['roll']
        pitch_rad = orientation_rad['pitch']
        yaw_rad = orientation_rad['yaw']

        orientation_degrees = sense.get_orientation_degrees()
        roll_deg = orientation_degrees['roll']
        pitch_deg = orientation_degrees['pitch']
        yaw_deg = orientation_degrees['yaw']

        orientation = sense.get_orientation()
        roll_orientation = orientation['roll']
        pitch_orientation = orientation['pitch']
        yaw_orientation = orientation['yaw']

        compass_raw = sense.get_compass_raw()
        x_compass_raw = compass_raw['x']
        y_compass_raw = compass_raw['y']
        z_compass_raw = compass_raw['z']

        gyro_only = sense.get_gyroscope()
        roll_gyro_only = gyro_only['roll']
        pitch_gyro_only = gyro_only['pitch']
        yaw_gyro_only = gyro_only['yaw']

        gyro_raw = sense.get_gyroscope_raw()
        x_gyro_raw = gyro_raw['x']
        y_gyro_raw = gyro_raw['y']
        z_gyro_raw = gyro_raw['z']

        accel_only = sense.get_accelerometer()
        roll_accel_only = accel_only['roll']
        pitch_accel_only = accel_only['pitch']
        yaw_accel_only = accel_only['yaw']

        accel_raw = sense.get_accelerometer_raw()
        x_accel_raw = accel_raw['x']
        y_accel_raw = accel_raw['y']
        z_accel_raw = accel_raw['z']

        calculations = (datetime_now, day, lontitude, latitude, photo_num, temperature, 
                    humidity, 
                    pressure, 
                    roll_rad, 
                    pitch_rad, 
                    yaw_rad, 
                    roll_deg,
                    pitch_deg, 
                    yaw_deg, 
                    roll_orientation, 
                    pitch_orientation, 
                    yaw_orientation, 
                    x_compass_raw, 
                    y_compass_raw, 
                    z_compass_raw, 
                    roll_gyro_only, 
                    pitch_gyro_only, 
                    yaw_gyro_only,
                    x_gyro_raw, 
                    y_gyro_raw, 
                    z_gyro_raw, 
                    roll_accel_only, 
                    pitch_accel_only, 
                    yaw_accel_only, 
                    x_accel_raw, 
                    y_accel_raw, 
                    z_accel_raw)

    #If the Sense Hat fails to calculate the data the CSV file will be filled with 0
    #Hence, the program won't crash and the error will be visible.
    except Exception as e:
        logger.error('{}: {})'.format(e.__class__.__name__, e))
        logger.error("Error: " + str(e))

        calculations = (datetime_now, day, lontitude, latitude, photo_num, temperature, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

    return calculations
   

def create_csv_file(data_file):
    '''
    Creates a CSV file and adds labels to the columns
    '''

    with open(data_file, 'w') as file:
        writer = csv.writer(file)
        labels = ("Date/time",
                  "Day or Night", 
                  "Longtitude", 
                  "Lattitude", 
                  "Photo Number", 
                  "Temperature", 
                  "Humidity",
                  "Pressure", 
                  "Orientatin Rad Roll", 
                  "Orientatin Rad Pitch", 
                  "Orientatin Rad Yaw", 
                  "Orientatin Degrees Roll",
                  "Orientatin Degrees Pitch", 
                  "Orientatin Degrees Yaw", 
                  "Orientatin Roll",
                  "Orientatin Pitch", 
                  "Orientatin Yaw", 
                  "Compass Raw X", 
                  "Compass Raw Y", 
                  "Compass Raw Z",
                  "Gyro Only Roll", 
                  "Gyro Only Pitch",
                  "Gyro Only Yaw",
                  "Gyro Raw X",
                  "Gyro Raw Y", 
                  "Gyro Raw Z",
                  "Acceleration Only Roll", 
                  "Acceleration Only Pitch", 
                  "Acceleration Only Yaw",
                  "Acceleration Raw X", 
                  "Acceleration Raw Y", 
                  "Acceleration Raw Z")
                  
        writer.writerow(labels)

def add_csv_data(data_file, data):
    '''
    Adds data to the CSV file
    '''

    #Makes sure to always open / close the file
    with open(data_file, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(data)

#######################

#Start counting the duration of the program
start = datetime.now()

#Path of the file in which data is stored
path = os.path.dirname(os.path.realpath(__file__))

#Name of the CSV data file
data_file = path + "/spacekludgers.csv"
create_csv_file(data_file)

#Name of the log file - Shows details about the program while it's running
logzero.logfile(path + "/spacekludgers.log")
formatter = logging.Formatter('%(name)s - %(asctime)-15s - %(levelname)s: %(message)s');
logzero.formatter(formatter)

#Connect to the Sense HAT
sense = SenseHat()

#Find location of ISS 
name = "ISS (ZARYA)"
line1 = "1 25544U 98067A   20041.35648148  .00000452  00000-0  16324-4 0  9997"
line2 = "2 25544  51.6446 260.9599 0004888 249.2039  92.3149 15.49151626212198"

iss = ephem.readtle(name, line1, line2)

#Variable to check if it's day or night
day = False

#Connect to the camera - Set resolution
camera = PiCamera() 
res1 = 2592
res2 = 1944
camera.resolution = (res1, res2)

#Photo number / Gives different names to the images
photo_num = 0 

#Second variable to check the duration of the program 
now = datetime.now()

#Saves info to the log file
logger.info("Starting Space kludgers job at: %s", start)

#Time when the program is supposed to exit 
#Runs for 178 minutes, 2 minutes before the expected end of the program 
endtime = start + timedelta(minutes=178)

#Run program until calculated endtime
while (now < endtime):

    try:
        #Gets the coordinates of ISS
        iss.compute()

        #Longtitude & latitude in degrees
        lontitude = iss.sublong / degree
        latitude = iss.sublat / degree

        #Saves info to the log file
        logger.info("ISS at %s is at Lontitude: %s Latitude: %s", now, lontitude, latitude)

        #Input for is_the_sun_up function
        lontitude_str = str(lontitude)
        latitude_str = str(latitude)
        time = datetime.utcnow() 

        #Calculates if it's day or night
        day = is_the_sun_up(lontitude_str, latitude_str, time)

        #Saves info to the log file
        logger.info("ISS is in day = %s", day)

        #Calculates and writes the metadata to add them to the photo details
        write_photo_metadata()
        
        # save photo using current number
        write_photo(photo_num)

        #Calculates data and adds them to the CSV file
        data_from_sensehat = collect_sensehat_data(now, day, lontitude, latitude, photo_num)
        add_csv_data(data_file, data_from_sensehat)
 
        #Makes the program wait for a few seconds before capturing another photo.
        photo_capture_delay(day)

    #Helps the program to keep running if an error occurs - States the error
    except Exception as e:
        logger.error('{}: {})'.format(e.__class__.__name__, e))
        logger.error("Error: " + str(e))
        sleep(5)

    #Gives a diffrent name to the next photo
    photo_num = photo_num + 1 
        
    #Change value in order to update the duration of the program
    now = datetime.now()

logger.info("Succesfully completed Space kludgers ISS Job at %s ", now)


