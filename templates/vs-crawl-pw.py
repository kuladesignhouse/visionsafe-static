import requests
from bs4 import BeautifulSoup
import re
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import base64
from jinja2 import Environment, FileSystemLoader
from slugify import slugify

# Function to check if a URL is a WordPress URL
def is_wordpress_url(url):
    wordpress_patterns = [
        r'/wp-content/',
        r'/wp-admin/',
        r'/wp-json/',
        r'/\d{4}/\d{2}/\d{2}/',  # Date-based permalinks
        r'/category/',
        r'/tag/',
        r'/page/',
        r'/\?p=\d+',  # Query-based permalinks
        r'/\d{4}/\d{2}/',  # Year/Month permalinks
    ]
    return any(re.search(pattern, url) for pattern in wordpress_patterns)

# Function to login to WordPress
def login_to_wordpress(session, login_url, username, password):
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    # Find the login form and its hidden input fields
    login_form = soup.find('form', id='loginform')
    if not login_form:
        print("Could not find the login form. Check the login URL or the form ID.")
        return False
    hidden_inputs = login_form.find_all('input', type='hidden')
    login_data = {input['name']: input['value'] for input in hidden_inputs}
    # Add the login credentials
    login_data['log'] = username
    login_data['pwd'] = password
    login_data['rememberme'] = 'forever'
    # Post the login form
    response = session.post(login_url, data=login_data)
    response_soup = BeautifulSoup(response.content, 'html.parser')
    #print(response.text)
    # Check for login success indicators
    if response_soup.find('div', id='login_error'):
        print("Login error: Incorrect username or password.")
        return False
    elif 'Dashboard' in response.text or 'Log Out' in response.text:
        print('Login successful!')
        return True
    else:
        print("Login failed for unknown reasons.")
        return False

def save_to_markdown(page_title, text_content, html_content, links, page_pw):
    formated_page_title = page_title.replace("Manuals and documents pertaining to ", "")
    page_title_url = slugify(formated_page_title)  # Convert to URL-safe string

    # Define the markdown filename and path directly in Visionsafe-STC-Pages directory
    markdown_filename = f'../../git/Visionsafe-STC-Pages/{formated_page_title}.md'
    
    # Save markdown content
    with open(markdown_filename, 'w', encoding='utf-8') as file:
        file.write(f"# {page_title}\n\n")
        if page_pw:
            #print(f"pw: {page_pw}\n\n")
            template = env.get_template('password-page.njk')
            encrypted_content = encrypt_html(page_pw, html_content)
            pw_html = template.render(
                html_title=f"{formated_page_title} - VisionSafe",
                page_title=page_title,
                encrypted_content=encrypted_content
            )

            # Save the HTML file as index.html in the ../dist/{formated_page_title} folder
            dist_folder = "../dist/wp"
            html_folder = f"{dist_folder}/{page_title_url}"
            os.makedirs(html_folder, exist_ok=True)
            html_filename = f"{html_folder}/index.html"
            with open(html_filename, 'w', encoding='utf-8') as html_file:
                html_file.write(pw_html)

        file.write(text_content)
        file.write("\n\n")

        # Group links by header text
        link_groups = {}
        for link in links:
            header_text = link.find_previous('h3').get_text() if link.find_previous('h3') else 'Other Links'
            if header_text not in link_groups:
                link_groups[header_text] = []
            href = link.get('href')
            link_text = link.get_text()
            link_groups[header_text].append(f"- [{link_text}]({href})")

        # Write links grouped by header
        for header, link_list in link_groups.items():
            file.write(f"## {header}\n")
            file.write('\n'.join(link_list))
            file.write("\n\n")

        print(f"Saved {page_title} to {markdown_filename}")

def encrypt_html(password, html_content):
    # Derive a key from the password
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    # Encrypt the HTML content
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(html_content.encode()) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    encrypted_content = base64.b64encode(salt + iv + encrypted_data).decode()
    return encrypted_content

# Set up the Jinja2 environment
template_dir = os.path.dirname(os.path.abspath(__file__))  # Or specify the path to your templates directory
env = Environment(loader=FileSystemLoader(template_dir))

# Main script
login_url = 'https://www.visionsafe.com/wp-login.php'
username = 'bgrainger'
password = ''
pw_pages = []

session = requests.Session()
if login_to_wordpress(session, login_url, username, password):
    for page in pw_pages:

        page_pw = ''
        page_pw = page['password']

        response = session.get(page['url'])
        page_content = response.content
        # Parse content with Beautiful Soup
        soup = BeautifulSoup(page_content, 'html.parser')

        # Find the container div
        container_div = soup.find('div', {'id': 'portal-item'})
        if container_div:
            # Extract the page title
            page_title = container_div.find('h2', {'class': 'portal-item'}).get_text()

            # Extract the text content
            text_content = container_div.find('div', {'class': 'portal-content'}).get_text()

            # Extract the html content
            html_content = container_div.find('div', {'class': 'portal-content'}).prettify()

            # Extract the links
            links = container_div.find('div', {'class': 'portal-content'}).find_all('a', href=True)

            # Save content to Markdown
            save_to_markdown(
                page_title,
                text_content,
                html_content,
                links,
                page_pw
            )
        else:
            print(f"Failed to find container div for {page['url']}")
else:
    print("Unable to login to WordPress")