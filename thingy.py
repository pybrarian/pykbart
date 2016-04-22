import requests

from selenium import webdriver
br = webdriver.PhantomJS()
br.get('http://lib.westfield.ma.edu/go.php?c=14469223')
br.save_screenshot('screenshot.png')
br.quit

'''
r = requests.get('http://lgapi.libapps.com/1.1/assets?site_id=1761&key=82719699635fb57e2d192757924a7318&asset_types=10')
as_json = r.json()
#thing = json.loads(as_json)

for entry in as_json:
    print(entry['url'])
    if 'informaworld' in entry['url']:
        print('{}: {}'.format(entry['name'], entry['url']))
else:
    print('none')
'''
