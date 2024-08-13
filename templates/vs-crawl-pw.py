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
password = '^N68%N(n7fKJ8**qpm#$@O6E'
pw_pages = [ { "url": "https://www.visionsafe.com/107p-015-016/", "password": "nwZLLPuE" }, { "url": "https://www.visionsafe.com/107p-019-020/", "password": "7g2t8jLc" }, { "url": "https://www.visionsafe.com/107p-027-028/", "password": "xTYJhz5h" }, { "url": "https://www.visionsafe.com/107p-043-044/", "password": "BakMPZEH" }, { "url": "https://www.visionsafe.com/107p-045-046/", "password": "pq6WuFd5" }, { "url": "https://www.visionsafe.com/107p-047-048/", "password": "W4xBZWvC" }, { "url": "https://www.visionsafe.com/107p-049-050/", "password": "P2zSpKW3" }, { "url": "https://www.visionsafe.com/107p-065-066/", "password": "TzS97GGH" }, { "url": "https://www.visionsafe.com/107p-067-068/", "password": "abMGqTyy" }, { "url": "https://www.visionsafe.com/107p-069-070/", "password": "JzjM4kJ8" }, { "url": "https://www.visionsafe.com/107p-071-072/", "password": "5npqXpsC" }, { "url": "https://www.visionsafe.com/107p-075-076/", "password": "u4RdMNs7" }, { "url": "https://www.visionsafe.com/107p-099-100/", "password": "FqrD5edT" }, { "url": "https://www.visionsafe.com/107p-101-102/", "password": "dWgaU5HA" }, { "url": "https://www.visionsafe.com/107p-109-110/", "password": "wseWqCt3" }, { "url": "https://www.visionsafe.com/107p-119-120/", "password": "Tt9aPkFq" }, { "url": "https://www.visionsafe.com/107p-121-122/", "password": "Q737F2wu" }, { "url": "https://www.visionsafe.com/107p-139-140/", "password": "HHj5sVsH" }, { "url": "https://www.visionsafe.com/107p-167-168/", "password": "dJ8krGN7" }, { "url": "https://www.visionsafe.com/107p-191-192/", "password": "v44sFjQB" }, { "url": "https://www.visionsafe.com/107p-197-198/", "password": "SJktfF82" }, { "url": "https://www.visionsafe.com/107p-015-016-copy/", "password": "kxUD7aSK" }, { "url": "https://www.visionsafe.com/107p-215-216/", "password": "sW4zwcxS" }, { "url": "https://www.visionsafe.com/107p-225-226/", "password": "nxK6uzWT" }, { "url": "https://www.visionsafe.com/107p-231-232/", "password": "4e8rxtR7" }, { "url": "https://www.visionsafe.com/107p-233-234/", "password": "Ls4E6DmA" }, { "url": "https://www.visionsafe.com/107p-235-236/", "password": "eLZgsZ6v" }, { "url": "https://www.visionsafe.com/107p-241-242/", "password": "8gb4fSt8" }, { "url": "https://www.visionsafe.com/107p-243-244/", "password": "mhzFfztT" }, { "url": "https://www.visionsafe.com/107p-247-248/", "password": "YXBbpe24" }, { "url": "https://www.visionsafe.com/107p-259-260/", "password": "wwduKy29" }, { "url": "https://www.visionsafe.com/107p-273-274/", "password": "iezNY7AX" }, { "url": "https://www.visionsafe.com/107p-285-286/", "password": "uoWQjuzv" }, { "url": "https://www.visionsafe.com/107stc-015-016/", "password": "" }, { "url": "https://www.visionsafe.com/107stc-015-016-copy/", "password": "" }, { "url": "https://www.visionsafe.com/107stc-015-016-la/", "password": "W17y1U00" }, { "url": "https://www.visionsafe.com/107stc-015-016-ny/", "password": "HDgoNzmR" }, { "url": "https://www.visionsafe.com/107stc-019-020/", "password": "o06S7i4Q" }, { "url": "https://www.visionsafe.com/107stc-025-026/", "password": "jKyM9VNx" }, { "url": "https://www.visionsafe.com/107stc-049-050/", "password": "m1n8OHtA" }, { "url": "https://www.visionsafe.com/107stc-057-058/", "password": "R0W0wb51" }, { "url": "https://www.visionsafe.com/107stc-065-066/", "password": "L70Qh7hY" }, { "url": "https://www.visionsafe.com/107stc-067-068/", "password": "Kk6psQOl" }, { "url": "https://www.visionsafe.com/107stc-075-076/", "password": "8e61F72z" }, { "url": "https://www.visionsafe.com/107stc-095-096/", "password": "dWB4jzNR" }, { "url": "https://www.visionsafe.com/107stc-099-100/", "password": "c7mJ9n26" }, { "url": "https://www.visionsafe.com/107stc-101-102/", "password": "6JNm15r9" }, { "url": "https://www.visionsafe.com/107stc-105-106/", "password": "K7gA50hb" }, { "url": "https://www.visionsafe.com/107stc-109-110/", "password": "644n1C6G" }, { "url": "https://www.visionsafe.com/107stc-119-120/", "password": "g465DSsE" }, { "url": "https://www.visionsafe.com/107stc-121-122/", "password": "" }, { "url": "https://www.visionsafe.com/107stc-121-122-copy/", "password": "" }, { "url": "https://www.visionsafe.com/107stc-121-122-la/", "password": "K697j13J" }, { "url": "https://www.visionsafe.com/107stc-121-122-ny/", "password": "Z1Htdbcs" }, { "url": "https://www.visionsafe.com/107stc-139-140/", "password": "tPCO428J" }, { "url": "https://www.visionsafe.com/107stc-147-148/", "password": "YExbyDEm" }, { "url": "https://www.visionsafe.com/107stc-167-168/", "password": "p8O5oXZg" }, { "url": "https://www.visionsafe.com/107stc-191-192/", "password": "Wf3v8UmX" }, { "url": "https://www.visionsafe.com/107stc-195-196/", "password": "g2810R3c" }, { "url": "https://www.visionsafe.com/107stc-197-198/", "password": "2e2r2kM1" }, { "url": "https://www.visionsafe.com/107stc-209-210/", "password": "SfY9PgsZ" }, { "url": "https://www.visionsafe.com/107stc-211-212/", "password": "64jJ3935" }, { "url": "https://www.visionsafe.com/107stc-215-216/", "password": "8lTM38kV" }, { "url": "https://www.visionsafe.com/107stc-221-222/", "password": "gDrb2oF3" }, { "url": "https://www.visionsafe.com/107stc-225-226/", "password": "L8uUWP60" }, { "url": "https://www.visionsafe.com/107stc-231-232/", "password": "QxEJp9rT" }, { "url": "https://www.visionsafe.com/107stc-231-232-set-2/", "password": "BH2jnUTj" }, { "url": "https://www.visionsafe.com/107stc-231-232-set-3/", "password": "z43X2KVh" }, { "url": "https://www.visionsafe.com/107stc-231-232-set-4/", "password": "kUAaKcL5" }, { "url": "https://www.visionsafe.com/107stc-233-234/", "password": "52f7A61A" }, { "url": "https://www.visionsafe.com/107stc-235-236/", "password": "OCdt194u" }, { "url": "https://www.visionsafe.com/107stc-241-242/", "password": "66rwenbW" }, { "url": "https://www.visionsafe.com/107stc-243-244/", "password": "8yn7Cnh9" }, { "url": "https://www.visionsafe.com/107stc-251-252/", "password": "vy4MLy25" }, { "url": "https://www.visionsafe.com/107stc-265-266/", "password": "pn2jVVHe" }, { "url": "https://www.visionsafe.com/107stc-267-268/", "password": "Hg8rX928" }, { "url": "https://www.visionsafe.com/107stc-271-272/", "password": "Ks2fG267" }, { "url": "https://www.visionsafe.com/107stc-277-278/", "password": "Lt8sH573" }, { "url": "https://www.visionsafe.com/107stc-287-288/", "password": "lmy8TYsF" }, { "url": "https://www.visionsafe.com/107tc-049-050/", "password": "KW3z5hTg" }, { "url": "https://www.visionsafe.com/about/", "password": "" }, { "url": "https://www.visionsafe.com/addtional-smoke-in-the-cockpit/", "password": "" }, { "url": "https://www.visionsafe.com/all-smoke-in-the-cockpit-events/", "password": "" }, { "url": "https://www.visionsafe.com/blog/", "password": "" }, { "url": "https://www.visionsafe.com/client-login/", "password": "" }, { "url": "https://www.visionsafe.com/client-portal/", "password": "lollipop" }, { "url": "https://www.visionsafe.com/client-portal-2/", "password": "" }, { "url": "https://www.visionsafe.com/client-signup/", "password": "123456" }, { "url": "https://www.visionsafe.com/contact/", "password": "" }, { "url": "https://www.visionsafe.com/forget-password/", "password": "" }, { "url": "https://www.visionsafe.com/forgot-password/", "password": "" }, { "url": "https://www.visionsafe.com/incidents-blog/", "password": "" }, { "url": "https://www.visionsafe.com/navtest/", "password": "" }, { "url": "https://www.visionsafe.com/product/", "password": "" }, { "url": "https://www.visionsafe.com/recent-posts/", "password": "" }, { "url": "https://www.visionsafe.com/recent-smoke-in-the-cockpit-events/", "password": "" }, { "url": "https://www.visionsafe.com/", "password": "" }, { "url": "https://www.visionsafe.com/post-search/", "password": "" }, { "url": "https://www.visionsafe.com/training/", "password": "" } ]


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