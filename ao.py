#!/usr/bin/env python3

LOAD_TIME=1.0
REFRESH_TIME=0.2
HEADLESS=False

ERR_NOT_IN_NORWAY=1

import json
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
import time

with open('settings.json','r') as fd:
  settings = json.load(fd)

options = webdriver.chrome.options.Options()
if HEADLESS:
  options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def logon():
  driver.get('https://artsobservasjoner.no/Logon')

  time.sleep(LOAD_TIME)

  fields = driver.find_elements_by_xpath('//input')
  for f in fields:
    if f.get_attribute('id') == 'AuthenticationViewModel_UserName':
      f.send_keys(settings['ao_user'])
    if f.get_attribute('id') == 'AuthenticationViewModel_Password':
      f.send_keys(settings['ao_pass'])
    if f.get_attribute('id') == 'submitbutton':
      f.click()

  time.sleep(LOAD_TIME)
  #TODO: check success
  return


def get_taxons_for_date(date):
  date=date.strftime('%Y-%m-%d')
  print(f"Fetching {date}")
  driver.get(f'https://artsobservasjoner.no/FieldDiaryByDate/{date}')

  time.sleep(LOAD_TIME)

  entries=[]
  fields = driver.find_elements_by_xpath("//div[@class='sightings']//span/b")
  for f in fields:
      if f.text[-1]=="?":
        entries.append(f.text.lower()[:-1])
      else:
        entries.append(f.text.lower())

  return entries

def nominatim(lat, lon):
  place = requests.get(f'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lon={lon}&lat={lat}')
  #print(place)
  data = place.json()
  return data.get('display_name','Ukjent')

def submit_sighting(data):
  # data format still subject to change
  taxon     = data['taxon']
  startdate = data['date'].strftime('%d.%m.%Y')
  enddate   = data['date']
  lat       = f"{data['lat']:.{6}f}"
  lon       = f"{data['lon']:.{6}f}"
  placename = nominatim(lat, lon)
  placename = "-".join(map(lambda x:x.strip(),placename.split(",")))

  if not "Norge" in placename:
      print(f"NOT IN NORWAY, SKIPPING: {placename}")
      return ERR_NOT_IN_NORWAY

  if len(placename) > 75:
    placename = placename[:74]

  print(f"Place: {placename}")

  print(f"Sumbitting entry: {taxon} {lat} {lon}")
  driver.get(f'https://artsobservasjoner.no/SubmitSighting/Report')

  time.sleep(LOAD_TIME)

  fields = driver.find_elements_by_xpath('//a')
  for f in fields:
      if f.get_attribute('id') == 'new-site':
        f.click()

  time.sleep(REFRESH_TIME)

  fields = driver.find_elements_by_xpath('//select')
  for f in fields:
      if f.get_attribute('id') == 'SiteViewModel_NewSite_Site_AccuracyDisplay':
        webdriver.support.ui.Select(f).select_by_index(3)

  fields = driver.find_elements_by_xpath('//input')
  for f in fields:
      if f.get_attribute('id') == 'SightingViewModel_TemporarySighting_Sighting_Taxon_Name':
        f.send_keys(taxon+Keys.ENTER)
        time.sleep(LOAD_TIME)
        f.send_keys(Keys.ENTER)
        time.sleep(REFRESH_TIME)

      if f.get_attribute('id') == 'SightingViewModel_TemporarySighting_Sighting_StartDate':
        f.send_keys(startdate)
      #auto-filled
      #if f.get_attribute('id') == 'SightingViewModel_TemporarySighting_Sighting_EndDate':
      #  f.send_keys(enddate)
      if f.get_attribute('id') == 'SiteViewModel_NewSite_Site_Name':
        f.send_keys(placename)
      if f.get_attribute('id') == 'SiteViewModel_NewSite_NewSiteCoordinate_Latitude':
        f.send_keys(str(lat))
        f.send_keys(Keys.TAB)
      if f.get_attribute('id') == 'SiteViewModel_NewSite_NewSiteCoordinate_Longitude':
        f.send_keys(str(lon))
        f.send_keys(Keys.TAB)

  if len(data['sounds'])>0:
      fields = driver.find_elements_by_xpath('//textarea')
      for f in fields:
        if f.get_attribute('id') == 'SightingViewModel_TemporarySighting_Sighting_PublicComment_Comment':
          value = ""
          for sound_url in data['sounds']:
              value += f"Lydfil: {sound_url}\n"
          f.send_keys(value)

  time.sleep(REFRESH_TIME)

  fields = driver.find_elements_by_xpath('//button')
  for f in fields:
      if f.get_attribute('id') == 'submitbutton':
        f.send_keys(Keys.ENTER)
        time.sleep(LOAD_TIME*5)
        break

  if len(data['images'])>0:
      for image in data['images']:
          dl = requests.get(image)
          with open("photo.jpg", "wb") as fd:
              fd.write(dl.content)

          fields = driver.find_elements_by_xpath('//a')
          for f in fields:
            if f.get_attribute('original-title') == 'Last opp bilde':
              f.send_keys(Keys.ENTER)

          fields = driver.find_elements_by_xpath('//input')
          for f in fields:
            if f.get_attribute('name') == 'UploadImageViewModel.Image':
              path = os.getcwd() + "/photo.jpg"
              f.send_keys(path)
              print(path)

          fields = driver.find_elements_by_xpath('//input')
          for f in fields:
            if f.get_attribute('value') == 'Last opp':
              f.send_keys(Keys.ENTER)
      pass

  fields = driver.find_elements_by_xpath('//input')
  for f in fields:
      if f.get_attribute('value') == 'Kontroller funn':
          f.send_keys(Keys.ENTER)
          time.sleep(LOAD_TIME)
          break

  fields = driver.find_elements_by_xpath('//input')
  for f in fields:
      if f.get_attribute('value') == 'Publiser alle funn':
          f.send_keys(Keys.ENTER)
          time.sleep(LOAD_TIME)
          break

  return True

def ao_close():
  driver.close()

logon()
