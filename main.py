import base64

import none as none
import requests
import json
import uuid
######################

#system = 'DEV'
system = 'PRD'
#system = 'DEV'
company = '00000000000000111'
environment = 'console'
######################
company = company + system


def rejigData(source):
    # rejig the data
    serviceResponse = json.loads(source)
    WCListObject = serviceResponse[0]
    WCDescList = WCListObject['JCWorkCentres']
    listItem = []
    for entry in WCDescList:
        tempEntry = {}
        tempEntry['Title'] = entry['Code']
        tempEntry['Description'] = entry['Description']
        tempEntry['Value1'] = None
        tempEntry['Value2'] = None
        tempEntry['Value3'] = None
        tempEntry['Value4'] = None
        tempEntry['Value5'] = None
        tempEntry['Value6'] = None
        tempEntry['ID'] = str(uuid.uuid4())
        listItem.append(tempEntry)

    listItem.sort(key=lambda x: x["Title"])
    return listItem

def deltaCheck(gtData, genData):
    genLoop = 0
    genDataTemp = genData.copy()
    gtLoop = 0
    foundGT = False
    while genLoop < len(genData):
        foundGT = False
        gtLoop = 0
        while gtLoop < len(gtData):
            print(gtData[gtLoop]['Title'] + ' compare with ' + genData[genLoop]['Title'])
            if (gtData[gtLoop]['Title'] == genData[genLoop]['Title']):
                del gtData[gtLoop]
                foundGT = True
                break
            gtLoop = gtLoop + 1
        if foundGT:
            #remove the GenData entry
            del genData[genLoop]
        else:
            genLoop = genLoop + 1

    for entry in genData:
        genLoop = 0
        while genLoop < len(genDataTemp):
            if genDataTemp[genLoop]['Title'] == entry['Title']:
                del genDataTemp[genLoop]
                break
            genLoop = genLoop + 1

    for entry in gtData:
        genDataTemp.append(entry)

    print('Sort result')
    genDataTemp.sort(key=lambda x: x["Title"])
    return genDataTemp

def getGenDataList():
    getResponse = requests.get(url=toknsource, params=toknparams, headers=toknheaders)
    jsonResponse = json.loads(getResponse.text)
    jsonResponse = base64.b64decode(jsonResponse[0]['data'])
    return json.loads(jsonResponse.decode('utf-8'))

upstreamurl = "https://api-ups2-live.greentree.io/UPS/JCWorkCentre?pageSize=9999"
#url = "https://api-ups2-test.greentree.io/UPS/JCWorkCentre?pageSize=9999"

if environment == "console":
    toknsource = 'https://console.tokntechnology.com:50001/Connect/api/genDataService?'
if environment == "demo":
    toknsource = 'http://demo.tokntechnology.com:50000/Connect/api/genDataService?'

if system == "PRD":
    urlHeaders = {'ApiKey': '500418', 'Authorization': 'Basic YXBpdG9rbjoyTVVTaHRCcmRtQzIzR3ZV', 'Accept': 'application/json'}
    toknheaders = {'Authorization':'Bearer MDAwMDAwMDAwMDAwMDAxMTFQUkQ=:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUT0tOIn0.XVRBilmk0EL0mWo_VX1dH4cYa37ohYmONbdvwGRSbHw','replaceListManager':'Y'}
elif system == 'DEV':
    urlHeaders = {'ApiKey': '500418', 'Authorization': 'Basic YXBpdG9rbjpUMGtuQVBJVDBrbkFQSQ==', 'Accept': 'application/json'}
    toknheaders = {'Authorization': 'Bearer MDAwMDAwMDAwMDAwMDAxMTFERVY=:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUT0tOIn0.VlsxzVMfPCIN0Q3XEe-69xi84pfXPe9a9Q14aR4CZsI','replaceListManager':'Y'}
else:
    urlHeaders = {'ApiKey':'500418', 'Authorization':'Basic YXBpdG9rbjpUMGtuQVBJVDBrbkFQSQ==','Accept':'application/json'}
    toknheaders = {'Authorization': 'Bearer MDAwMDAwMDAwMDAwMDAxMTFRQVM=:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJUT0tOIn0.DgVLqLG__EMwoAmm6mlxaeMTR5Zo6YhbJp2k08l5xRg','replaceListManager':'Y'}


toknparams = {'company':company,'appName':'ListManager', 'objectName':'ListManager'}
toknparams['keyID'] = "='{}'".format('ca789682-fcb1-4773-b2ea-11fc90141fd8')

payload={}

#get all the Upstream Work Centre Descriptions
print('Process starting')
print('Get Upstream Work Centre Descriptions')
response = requests.request("GET", upstreamurl, headers=urlHeaders, data=payload)

print('Reformat data to the same format as gendata list manager')
gtData = rejigData(response.text)

print('Compare Upstream to Gendata looking for differences')
genDataBefore = getGenDataList()['listItem']
genDataBefore.sort(key=lambda x: x["Title"])
gtData.sort(key=lambda x: x["Title"])
genDataAfter = deltaCheck(gtData.copy(), genDataBefore.copy())

if (genDataBefore != genDataAfter):
    print('Change detected, post updated entries to gendata')
    #post the data to the gendatastore list manager
    sendPayload = {}
    jsData = {}
    jsData['listItem'] = genDataAfter
    sendPayload['company'] = company
    sendPayload['appName'] = 'ListManager'
    sendPayload['objectName'] = 'ListManager'
    sendPayload['keyID'] = 'ca789682-fcb1-4773-b2ea-11fc90141fd8'
    sendPayload['data'] = jsData
    #print('Before' + str(gtDataBefore))
    #print('After ' + str(jsData))
    sendPayload['index1'] = 'WCDescription'
    sendPayload['index2'] = 'WCDescriptionList'
    sendPayload['index3'] = None
    sendPayload['index4'] = '{"Title":{"placeholder":"WorkCentre","value":null,"required":true},"Description":{"placeholder":"Description","value":null,"required":false},"Value1":{"placeholder":"Value1","value":null,"required":false},"Value2":{"placeholder":"Value2","value":null,"required":false},"Value3":{"placeholder":"Value3","value":null,"required":false},"Value4":{"placeholder":"Value4","value":null,"required":false},"Value5":{"placeholder":"Value5","value":null,"required":false},"Value6":{"placeholder":"Value6","value":null,"required":false}}'
    sendPayload['index5'] = None
    sendPayload['index6'] = None
    sendPayload['createdUser'] = 'UpstreamScript@tokntechnology.com'
    sendPayload['index7'] = None
    sendPayload['index8'] = None
    sendPayload['index9'] = None
    sendPayload['index10'] = None
    sendPayload['index11'] = None
    sendPayload['index12'] = None
    sendPayload = json.dumps(sendPayload)
    postResponse = requests.post(url=toknsource,data=sendPayload,headers=toknheaders)
    if postResponse.status_code != 200:
        print("Error: " + toknsource + " Failed with status code " + str(postResponse.status_code))
else:
    print('No changes, nothing to do')

