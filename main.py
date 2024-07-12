import requests
from bs4 import BeautifulSoup
import json

# Function to get the biography of a member
def fetch_member_biography(member_id):
    url = f'https://secure.toronto.ca/pa/member/{member_id}.do'
    response = requests.get(url)
    response.encoding = 'utf-8'  # Ensure the response is treated as UTF-8
    soup = BeautifulSoup(response.text, 'html.parser')
    biography_div = soup.select_one('.biography')
    
    if not biography_div:
        raise ValueError(f"Biography not found for member {member_id}")
    
    # Remove h1 tags from the biography div if biography_div exists
    for h1 in biography_div.find_all('h1'):
        h1.decompose()
        
    # Get the text from the biography div
    biography_text = biography_div.get_text(separator=' ', strip=True)
    return biography_text

# Function to get additional member data
def fetch_member_appointments(member_id):
    url = 'https://secure.toronto.ca/pa/appointment/aptForMemberJtable.json'
    data = {
        'memberId': member_id,
        'membership': 'All'
    }
    
    response = requests.post(url, data=data)
    response.encoding = 'utf-8'  # Ensure the response is treated as UTF-8
    appointments_data = response.json()

    # Filter the additional data to include only the required fields
    filtered_appointments = []
    for record in appointments_data.get('Records', []):
        appointment = {
            'role': record['role'],
            'decisionBodyName': record['decisionBodyName'],
            'appointmentEndDate': record['appointmentEndDate'],
            'appointmentStartDate': record['appointmentStartDate']
        }
        if 'panelName' in record:
            appointment['panelName'] = record['panelName']
        filtered_appointments.append(appointment)
    
    return filtered_appointments

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
    members = []
    for record in response_data['Records']:
        member_id = record['memberId']
        try:
            biography = fetch_member_biography(member_id)
            appointments = fetch_member_appointments(member_id)
            member_info = {
                'memberName': record['memberName'],
                'memberId': member_id,
                'biography': biography,
                'appointments': appointments
            }
            members.append(member_info)
        except (ValueError, KeyError) as e:
            print(f"Error processing member {member_id}: {e}")

    # Write the members' records to a JSON file
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(members, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
