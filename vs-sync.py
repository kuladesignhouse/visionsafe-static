import os
import requests
import filecmp
import difflib

# Define directories
server_url = 'http://visionsafe.com/'  # Replace with your server URL
server_files_list = [
    'warranty-RENAME-index.html',
    'faqs.html',
    'videos.html',
    'index.html',
    'testimonials.html',
    'about.html', 
    'contact.html',
    'gulfstream.html',
    'terms.html',
    'cargo-search.html', 
    'corporate.html',
    'cargo.html',
    'military.html',
    'smoke-in-the-cockpit.html', 
    'evas360.html',
    'holiday-closure.html',
    'thankyou.html',
    'smokescope.html', 
    'buy.html',
    'about-us.html',
    'search.html',
    'embraer.html',
    'training.html', 
    'algolia.html',
    'legislation.html',
    'faa-lithium-batteries.html',
    'vr.html', 
    'passenger.html',
    'privacy.html',
    'bombardier.html'
]
local_directory = './dist/'  # Replace with the path to your local Gulp build directory

# Define a temporary directory for storing downloaded files
temp_directory = './temp_server_files/'
if not os.path.exists(temp_directory):
    os.makedirs(temp_directory)

# Function to download a file from the server
def download_file(file_name):
    url = os.path.join(server_url, file_name)
    if file_name == 'warranty-RENAME-index.html':
        url = os.path.join(server_url, 'warranty', 'index.html')
    local_path = os.path.join(temp_directory, file_name)
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_name} from server.")
    else:
        print(f"Failed to download {file_name}. Status code: {response.status_code}")

# Function to compare local and server files and show differences
def compare_files(file_name):
    local_file = os.path.join(local_directory, file_name)
    server_file = os.path.join(temp_directory, file_name)
    
    if not os.path.exists(local_file):
        print(f"Local file {file_name} does not exist.")
        return
    
    if filecmp.cmp(local_file, server_file, shallow=False):
        print(f"Files {file_name} are identical.")
    else:
        print(f"Files {file_name} differ. Showing differences:")
        with open(local_file, 'r') as lf, open(server_file, 'r') as sf:
            local_lines = lf.readlines()
            server_lines = sf.readlines()
            diff = difflib.unified_diff(local_lines, server_lines, fromfile='local', tofile='server')
            for line in diff:
                print(line, end='')

# Function to filter out hidden files like .DS_Store
def filter_hidden_files(files_list):
    return [file for file in files_list if not file.startswith('.')]

# Check if the number of files matches
local_files_list = filter_hidden_files(os.listdir(local_directory))
if len(local_files_list) != len(server_files_list):
    print(f"Number of files in {local_directory} ({len(local_files_list)}) does not match the server files list ({len(server_files_list)}).")

    # Print discrepancies
    local_files_set = set(local_files_list)
    server_files_set = set(server_files_list)
    
    missing_in_local = server_files_set - local_files_set
    missing_in_server = local_files_set - server_files_set
    
    if missing_in_local:
        print(f"Files missing in local directory: {missing_in_local}")
    if missing_in_server:
        print(f"Files missing in server files list: {missing_in_server}")
else:
    print(f"Number of files in {local_directory} matches the server files list.")

    # Main script
    for file_name in server_files_list:
        print('\r\n')
        download_file(file_name)
        compare_files(file_name)

    # Cleanup: Remove downloaded files after comparison
    for file_name in server_files_list:
        os.remove(os.path.join(temp_directory, file_name))
    os.rmdir(temp_directory)
