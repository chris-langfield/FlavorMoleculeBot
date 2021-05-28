import tweepy as tw
from PIL import Image
from PIL import ImageOps
import requests
from io import BytesIO
import random 
import json
import csv
import time
#### KEYS
# twitter keys
CustomerApiKey = ""
CustomerApiKeySecret = ""
AccessToken = ""
AccessTokenSecret = ""


# Authenticate to Twitter
auth = tw.OAuthHandler(CustomerApiKey, CustomerApiKeySecret)
auth.set_access_token(AccessToken, AccessTokenSecret)

# Create API object
api = tw.API(auth,wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)

## run this ONCE

numPages = 512
baseUrl = 'https://cosylab.iiitd.edu.in/flavordb/molecules?common_name=&functional_group=&flavor_profile=&fema_flavor=&molecular_weight_from=&h_bond_donors=&h_bond_acceptors=&type=&smile=&page='
##for x in range(numPages):
##    p = x + 1
##    url = baseUrl + str(p)
##    print('page ' + str(p))
##    r = requests.get(url)
##    with open('pages/page{}.txt'.format(str(p)),'w') as f:
##        f.write(r.text)

##PubChemIds = open('PubChemIds.txt','w')
##
##for x in range(numPages):
##    p = x + 1
##    with open('pages/page{}.txt'.format(str(p),'r') )as f:
##        lines = f.readlines()
##        for l in lines:
##            if '<td><button id="' in l:
##                l = l.split('"')
##                Id = l[1]
##                PubChemIds.write(Id + '\n')
##        
##    
##PubChemIds.close()

jsonBaseUrl = 'https://cosylab.iiitd.edu.in/flavordb/molecules_json?id='
imgBaseUrl = 'https://cosylab.iiitd.edu.in/flavordb/static/molecules_images/'

imageFileName = str(int(time.time()))

badList = []

Ids = []
with open('PubChemIds.txt','r') as PubChemIds:
    Ids = PubChemIds.readlines()

count = 0
badChem = True
while badChem:
    count += 1
    if count > 30:
        break
    PCI = random.choice(Ids).strip()
    Done = []
    with open('Done.txt','r') as DoneFile:
        Done = [d.strip() for d in DoneFile.readlines()]
    if PCI in Done:
        print('{} already done'.format(PCI))
        continue
    
    try:
        chemJson = requests.get(jsonBaseUrl + PCI).json()
    except requests.HTTPError as h:
        print('HTTP Error: ' + str(h))
        break
    except Exception as e:
        print('Error: ' + str(e))
        break
    
    commonName = chemJson["common_name"]
    print(PCI)
    print(commonName)
    flavors = chemJson["fooddb_flavor_profile"].split('@')
    for b in badList:
        if b in flavors:
            flavors.remove(b)
    if (len(flavors)==1 and flavors[0] == '') or not flavors:
        continue
    
    print(flavors)
    iupacName = chemJson["iupac_name"]
    print(iupacName)

    chemImg = requests.get(imgBaseUrl + PCI + '.png')
    print (chemImg)
    if '200' not in str(chemImg):
        print('not found')
        continue
    print(chemImg)
    img = Image.open(BytesIO(chemImg.content))
    img.save('images/{}.png'.format(imageFileName))

    flavorText = ''
    if len(flavors) == 1:
        flavorText = flavors[0]
    elif len(flavors) == 2:
        flavorText = flavors[0] + ' and ' + flavors[1]
    else:
        for x in range(len(flavors)-1):
            flavorText += flavors[x]
            flavorText += ', '
        flavorText += 'and '
        flavorText += flavors[-1]
        
    Done.append(PCI)
    with open('Done.txt','w') as DoneFile:
        for d in Done:
            DoneFile.write('{}\n'.format(d.strip()))
    StatusText = '{0} (officially known as {1}) tastes like {2}.'.format(commonName,iupacName,flavorText)
    api.update_with_media('images/{}.png'.format(imageFileName), status=StatusText) 
    badChem = False
    



## a challenge for another day
## pubchem PUG-REST api
##imageUrl = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/' + PCI + '/PNG?record_type=3d&image_size=large'
##chemImage = requests.get(imageUrl,stream=True)
##print(chemImage)
##print(chemImage.content)







