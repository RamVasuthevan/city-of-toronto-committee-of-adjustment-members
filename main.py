import requests
from bs4 import BeautifulSoup
import json

# Function to get the biography of a member
def get_biography(member_id):
    url = f'https://secure.toronto.ca/pa/member/{member_id}.do'
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure the response is treated as UTF-8
    soup = BeautifulSoup(response.text, 'html.parser')
    biography_div = soup.select_one('.biography')
    
    # Remove h1 tags from the biography div if biography_div exists
    if biography_div:
        for h1 in biography_div.find_all('h1'):
            h1.decompose()
            
        # Get the text from the biography div
        biography_text = biography_div.get_text(separator=' ', strip=True)
        return biography_text
    
    return ''

# Function to get additional member data
def get_additional_member_data(member_id):
    url = 'https://secure.toronto.ca/pa/appointment/aptForMemberJtable.json'
    data = {
        'memberId': member_id,
        'membership': 'All'
    }
    
    response = requests.post(url, data=data)
    response.encoding = 'utf-8'  # Ensure the response is treated as UTF-8
    additional_data = response.json()

    # Filter the additional data to include only the required fields
    filtered_additional_data = [
        {
            'role': record.get('role', ''),
            'decisionBodyName': record.get('decisionBodyName', ''),
            'appointmentEndDate': record.get('appointmentEndDate', ''),
            'appointmentStartDate': record.get('appointmentStartDate', ''),
            'panelName': record.get('panelName', '')
        }
        for record in additional_data.get('Records', [])
    ]
    
    return filtered_additional_data

# Main function to get appointment data and biographies
def main():
    url = 'https://secure.toronto.ca/pa/appointment/aptForDecisionJtable.json'
    data = {
        'decisionBodyId': '49',
        'membership': 'Current',
        'panel': '0'
    }

    response = requests.post(url, data=data)
    response.encoding = 'utf-8'  # Ensure the response is treated as UTF-8
    response_data = response.json()

    # Extract relevant columns and add biography and additional data
    filtered_records = []
    for record in response_data['Records']:
        member_id = record['memberId']
        biography = get_biography(member_id)
        additional_data = get_additional_member_data(member_id)
        filtered_record = {
            'memberName': record['memberName'],
            'memberId': member_id,
            'biography': biography,
            'additionalData': additional_data
        }
        filtered_records.append(filtered_record)

    # Write the filtered records to a JSON file
    with open('text.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_records, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
