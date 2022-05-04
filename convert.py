#!/usr/bin/env python3

from pyinaturalist import *
import json
import sys

from ao import *

def format_photos(photos):
  for p in photos:
    print("    "+p['url'].replace('square','original'))

def format_sounds(sounds):
  for s in sounds:
    print("    "+s['file_url'])

page=1
PHOTOS=True
QUALITY='research'

with open("settings.json","r") as fd:
  settings = json.load(fd)

with open("transferred.json","r") as fd:
  transferred = json.load(fd)

while True:
  observations = get_observations(user_id=settings.get('inat_user'), hrank='species', quality_grade=QUALITY, page=page)

  for obs in observations['results']:

    uuid = obs['uuid']
    if uuid in transferred:
      continue
    print(f"UUID: {uuid}")

    date = obs['observed_on']

    if date is None:
        continue

    taxon = obs['taxon']['name']
    latitude = obs['location'][0]
    longitude = obs['location'][1]
    images = []

    for blob in obs.get('photos',[]):
        url = blob.get('url')
        images.append(url.replace('square', 'original'))

    sounds = []
    for blob in obs.get('sounds',[]):
        url = blob.get('file_url')
        sounds.append(url)

    print("looking for {} on {}".format(taxon, date))
    taxons = get_taxons_for_date(date)
    print(json.dumps(taxons,indent=2))

    # if we have a matching entry for that date, just add it to the list of transferred items
    if taxon.lower() in taxons:
      transferred[uuid]=True
      with open("transferred.json","w") as fd:
        json.dump(transferred, fd, indent=2)
      continue

    # else create a new entry with the data we have

    #TBD

    postdata = {
      "taxon": taxon,
      "date": date,
      "lat": latitude,
      "lon": longitude,
      "images": images,
      "sounds": sounds
    }

    errcode = submit_sighting(postdata)

    # double checking
    taxons = get_taxons_for_date(date)
    print(json.dumps(taxons,indent=2))

    if (errcode == ERR_NOT_IN_NORWAY) or (taxon in taxons):
      transferred[uuid]=True
      with open("transferred.json","w") as fd:
        json.dump(transferred, fd, indent=2)

      #ao_close()
      #sys.exit(1)

  page += 1
