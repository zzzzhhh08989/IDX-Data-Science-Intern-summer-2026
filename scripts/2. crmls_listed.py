#change export file name
#change date range

import csv
import requests
from datetime import datetime

# Define the API endpoint
url = 'https://api-trestle.corelogic.com/trestle/odata/Property'

# Define the client ID and client secret
client_id = 'trestle_IDXExchangeCRMLSRECore20240122014147'
client_secret = 'e579677f6297447aa794739558011d06'

# Define the authentication endpoint
auth_endpoint = 'https://api-trestle.corelogic.com/trestle/oidc/connect/token'

# Define the authentication payload
auth_payload = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}

# Define headers
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Make a POST request to the authentication endpoint to obtain the token
response = requests.post(auth_endpoint, data=auth_payload, headers=headers)

# Parse the response to extract the token
if response.status_code == 200:
    token = response.json().get('access_token')

    # Define the headers with the token
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Define the parameters for the API request
    params = {
        '$select': 'OriginalListPrice, ListingKey,ListAgentEmail,CloseDate,ClosePrice,ListAgentFirstName,ListAgentLastName,Latitude,Longitude,UnparsedAddress,PropertyType,LivingArea,ListPrice,DaysOnMarket,ListOfficeName,BuyerOfficeName,CoListOfficeName,ListAgentFullName,CoListAgentFirstName,CoListAgentLastName,BuyerAgentMlsId,BuyerAgentFirstName,BuyerAgentLastName,FireplacesTotal,AssociationFeeFrequency,AboveGradeFinishedArea,ListingKeyNumeric,MLSAreaMajor,TaxAnnualAmount,CountyOrParish,PropertyType,MlsStatus,ElementarySchool,ListAgentFirstName,AttachedGarageYN,ParkingTotal,BuilderName,PropertySubType,LotSizeAcres,SubdivisionName,BuyerOfficeAOR,YearBuilt,DaysOnMarket,StreetNumberNumeric,LivingArea,ListingId,BathroomsTotalInteger,City,TaxYear,BuildingAreaTotal,BedroomsTotal,ContractStatusChangeDate,Longitude,ElementarySchoolDistrict,CoBuyerAgentFirstName,PurchaseContractDate,ListingContractDate,BelowGradeFinishedArea,BusinessType,Latitude,ListPrice,StateOrProvince,CoveredSpaces,MiddleOrJuniorSchool,FireplaceYN,Stories,HighSchool,Levels,ListAgentLastName,CloseDate,LotSizeDimensions,LotSizeArea,MainLevelBedrooms,NewConstructionYN,GarageSpaces,HighSchoolDistrict,PostalCode,BuyerOfficeName,AssociationFee,LotSizeSquareFeet,MiddleOrJuniorSchoolDistrict,UnparsedAddress',
      
        '$filter': f"ListingContractDate ge {datetime(2025, 2, 1).isoformat(timespec='milliseconds')}Z and ListingContractDate lt {datetime(2025, 3, 1).isoformat(timespec='milliseconds')}Z",


        '$top': 1000  # Extracting up to 1000 observations
    }

    # Send a GET request to the API endpoint with the token and parameters
    total_records = 0
    csv_file = 'CRMLSListing202502.csv'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['OriginalListPrice','ListingKey', 'ListAgentEmail', 'CloseDate', 'ClosePrice', 'ListAgentFirstName', 'ListAgentLastName', 'Latitude', 'Longitude', 'UnparsedAddress', 'PropertyType', 'LivingArea', 'ListPrice', 'DaysOnMarket', 'ListOfficeName', 'BuyerOfficeName', 'CoListOfficeName', 'ListAgentFullName', 'CoListAgentFirstName', 'CoListAgentLastName', 'BuyerAgentMlsId', 'BuyerAgentFirstName', 'BuyerAgentLastName', 'FireplacesTotal', 'AssociationFeeFrequency', 'AboveGradeFinishedArea', 'ListingKeyNumeric', 'MLSAreaMajor', 'TaxAnnualAmount', 'CountyOrParish', 'PropertyType', 'MlsStatus', 'ElementarySchool', 'ListAgentFirstName', 'AttachedGarageYN', 'ParkingTotal', 'BuilderName', 'PropertySubType', 'LotSizeAcres', 'SubdivisionName', 'BuyerOfficeAOR', 'YearBuilt', 'DaysOnMarket', 'StreetNumberNumeric', 'LivingArea', 'ListingId', 'BathroomsTotalInteger', 'City',  'TaxYear', 'BuildingAreaTotal', 'BedroomsTotal', 'ContractStatusChangeDate', 'Longitude', 'ElementarySchoolDistrict', 'CoBuyerAgentFirstName', 'PurchaseContractDate', 'ListingContractDate', 'BelowGradeFinishedArea', 'BusinessType', 'Latitude', 'ListPrice', 'StateOrProvince', 'CoveredSpaces', 'MiddleOrJuniorSchool', 'FireplaceYN', 'Stories', 'HighSchool', 'Levels', 'ListAgentLastName', 'CloseDate', 'LotSizeDimensions', 'LotSizeArea', 'MainLevelBedrooms', 'NewConstructionYN', 'GarageSpaces', 'HighSchoolDistrict', 'PostalCode', 'BuyerOfficeName', 'AssociationFee', 'LotSizeSquareFeet', 'MiddleOrJuniorSchoolDistrict', 'UnparsedAddress'])
        writer.writeheader()

        while True:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                observations = data.get('value', [])
                for observation in observations:
                    writer.writerow({
                      'OriginalListPrice': observation.get('OriginalListPrice', ''),
                        'ListingKey': observation.get('ListingKey', ''),
                        'ListAgentEmail': observation.get('ListAgentEmail', ''),
                        'CloseDate': observation.get('CloseDate', ''),
                        'ClosePrice': observation.get('ClosePrice', ''),
                        'ListAgentFirstName': observation.get('ListAgentFirstName', ''),
                        'ListAgentLastName': observation.get('ListAgentLastName', ''),
                        'Latitude': observation.get('Latitude', ''),
                        'Longitude': observation.get('Longitude', ''),
                        'UnparsedAddress': observation.get('UnparsedAddress', ''),
                        'PropertyType': observation.get('PropertyType', ''),
                        'LivingArea': observation.get('LivingArea', ''),
                        'ListPrice': observation.get('ListPrice', ''),
                        'DaysOnMarket': observation.get('DaysOnMarket', ''),
                        'ListOfficeName': observation.get('ListOfficeName', ''),
                        'BuyerOfficeName': observation.get('BuyerOfficeName', ''),
                        'CoListOfficeName': observation.get('CoListOfficeName', ''),
                        'ListAgentFullName': observation.get('ListAgentFullName', ''),
                        'CoListAgentFirstName': observation.get('CoListAgentFirstName', ''),
                        'CoListAgentLastName': observation.get('CoListAgentLastName', ''),
                        'BuyerAgentMlsId': observation.get('BuyerAgentMlsId', ''),
                        'BuyerAgentFirstName': observation.get('BuyerAgentFirstName', ''),
                        'BuyerAgentLastName': observation.get('BuyerAgentLastName', ''),
                        'FireplacesTotal': observation.get('FireplacesTotal', ''),
                        'AssociationFeeFrequency': observation.get('AssociationFeeFrequency', ''),
                        'AboveGradeFinishedArea': observation.get('AboveGradeFinishedArea', ''),
                        'ListingKeyNumeric': observation.get('ListingKeyNumeric', ''),
                        'MLSAreaMajor': observation.get('MLSAreaMajor', ''),
                        'TaxAnnualAmount': observation.get('TaxAnnualAmount', ''),
                        'CountyOrParish': observation.get('CountyOrParish', ''),
                        'MlsStatus': observation.get('MlsStatus', ''),
                        'ElementarySchool': observation.get('ElementarySchool', ''),
                        'ListAgentFirstName': observation.get('ListAgentFirstName', ''),
                        'AttachedGarageYN': observation.get('AttachedGarageYN', ''),
                        'ParkingTotal': observation.get('ParkingTotal', ''),
                        'BuilderName': observation.get('BuilderName', ''),
                        'PropertySubType': observation.get('PropertySubType', ''),
                        'LotSizeAcres': observation.get('LotSizeAcres', ''),
                        'SubdivisionName': observation.get('SubdivisionName', ''),
                        'BuyerOfficeAOR': observation.get('BuyerOfficeAOR', ''),
                        'YearBuilt': observation.get('YearBuilt', ''),
                        'DaysOnMarket': observation.get('DaysOnMarket', ''),
                        
                        'StreetNumberNumeric': observation.get('StreetNumberNumeric', ''),
                        'LivingArea': observation.get('LivingArea', ''),
                        'ListingId': observation.get('ListingId', ''),
                        'BathroomsTotalInteger': observation.get('BathroomsTotalInteger', ''),
                        'City': observation.get('City', ''),

                        'TaxYear': observation.get('TaxYear', ''),
                        'BuildingAreaTotal': observation.get('BuildingAreaTotal', ''),
                        'BedroomsTotal': observation.get('BedroomsTotal', ''),
                        'ContractStatusChangeDate': observation.get('ContractStatusChangeDate', ''),
                        'Longitude': observation.get('Longitude', ''),
                        'ElementarySchoolDistrict': observation.get('ElementarySchoolDistrict', ''),
                        'CoBuyerAgentFirstName': observation.get('CoBuyerAgentFirstName', ''),
                        'PurchaseContractDate': observation.get('PurchaseContractDate', ''),
                        'ListingContractDate': observation.get('ListingContractDate', ''),
                        'BelowGradeFinishedArea': observation.get('BelowGradeFinishedArea', ''),
                        'BusinessType': observation.get('BusinessType', ''),
                        'Latitude': observation.get('Latitude', ''),
                        'ListPrice': observation.get('ListPrice', ''),
                        'StateOrProvince': observation.get('StateOrProvince', ''),
                        'CoveredSpaces': observation.get('CoveredSpaces', ''),
                        'MiddleOrJuniorSchool': observation.get('MiddleOrJuniorSchool', ''),
                        'FireplaceYN': observation.get('FireplaceYN', ''),
                        'Stories': observation.get('Stories', ''),
                        'HighSchool': observation.get('HighSchool', ''),
                        'Levels': observation.get('Levels', ''),
                        'ListAgentLastName': observation.get('ListAgentLastName', ''),
                        'CloseDate': observation.get('CloseDate', ''),
                        'LotSizeDimensions': observation.get('LotSizeDimensions', ''),
                        'LotSizeArea': observation.get('LotSizeArea', ''),
                        'MainLevelBedrooms': observation.get('MainLevelBedrooms', ''),
                        'NewConstructionYN': observation.get('NewConstructionYN', ''),
                        'GarageSpaces': observation.get('GarageSpaces', ''),
                        'HighSchoolDistrict': observation.get('HighSchoolDistrict', ''),
                        'PostalCode': observation.get('PostalCode', ''),
                        'BuyerOfficeName': observation.get('BuyerOfficeName', ''),
                        'AssociationFee': observation.get('AssociationFee', ''),
                        'LotSizeSquareFeet': observation.get('LotSizeSquareFeet', ''),
                        'MiddleOrJuniorSchoolDistrict': observation.get('MiddleOrJuniorSchoolDistrict', ''),
                        'UnparsedAddress': observation.get('UnparsedAddress', '')
                    })
                    total_records += 1

                # Check if there are more records to fetch
                if '@odata.nextLink' in data:
                    next_link = data['@odata.nextLink']
                    params = None  # Clear params to avoid appending to the existing query string
                    url = next_link
                else:
                    break
            else:
                print(f"Error: {response.status_code}")
                print(f"Error Message: {response.text}")
                break

    print(f"Total {total_records} records exported to {csv_file}")
else:
    # Print an error message if the token retrieval request was unsuccessful
    print(f"Error retrieving token: {response.status_code}")
