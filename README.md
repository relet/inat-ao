# inat-ao

A simple, somewhat stupid converter from inaturalist observations into artsobservasjoner using Selenium.

### usage

create a settings.json file with three dictionary entries, `inat_user`, `ao_user` and `ao_pass`. Run convert.py to copy all research grade observations, images and audio files into artsobservasjoner. 

Just keep an eye on the selenium browser in case something goes wrong.

### Known issues

* AO does not support classification below species level, so some names are misinterpreted (eg. alvus alvus alvus comes up with just 'alvus')
* It currently creates a new location per GPS coordinate.
* If the browser loads too slowly, elements may not be available. You can increase the LOAD_TIME and REFRESH_TIME in the source code, or just try again if it fails.
* Some taxons just don't exist in artsdatabanken yet.
