import requests
import json
import time
from bs4 import BeautifulSoup
import re
import random

#setting up the session
BASE_URL = 'https://www.instagram.com/accounts/login/'
LOGIN_URL = BASE_URL + 'ajax/'

headers_list = [
        "Mozilla/5.0 (Windows NT 5.1; rv:41.0) Gecko/20100101"\
        " Firefox/41.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2)"\
        " AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2"\
        " Safari/601.3.9",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0)"\
        " Gecko/20100101 Firefox/15.0.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"\
        " (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"\
        " Edge/12.246"
        ]


USERNAME = ""
PASSWD = ""
USER_AGENT = headers_list[random.randrange(0,4)]

session = requests.Session()
session.headers = {'user-agent': USER_AGENT}
session.headers.update({'Referer': BASE_URL})    
req = session.get(BASE_URL)    
soup = BeautifulSoup(req.content, 'html.parser')    
body = soup.find('body')

pattern = re.compile('window._sharedData')
script = body.find("script", text=pattern)

script = script.get_text().replace('window._sharedData = ', '')[:-1]
data = json.loads(script)

csrf = data['config'].get('csrf_token')
login_data = {'username': USERNAME, 'password': PASSWD}
session.headers.update({'X-CSRFToken': csrf})
login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)



#getting profile id
profileURL = "https://www.instagram.com/{}/".format(USERNAME)

profile = session.get(profileURL)
soup = BeautifulSoup(profile.text, 'html.parser')

script = soup.find('script', text=re.compile('window\.\_sharedData'))
json_text = re.search(r'^\s*window\.\_sharedData\s*=\s*({.*?})\s*;\s*$', script.string, flags=re.DOTALL | re.MULTILINE).group(1)
data = json.loads(json_text)

ID = data['entry_data']['ProfilePage'][0]['graphql']['user']['id']


#getting first query_hash 
q1 = session.get('https://www.instagram.com/static/bundles/es6/Consumer.js/213e8a7c4ec2.js')
query_hash1 = re.search('const t=\"(.+?)\",n=', q1.text).group(1)

#getting second query_hash
q2 = session.get('https://www.instagram.com/static/bundles/es6/Consumer.js/213e8a7c4ec2.js') 
query_hash2 = re.search('SUL\_QUERY\_ID=\"(.+?)\",', q2.text).group(1)

#getting people I follow that I don't follow back
followerURL = "https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22id%22%3A%22{}%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Atrue%2C%22first%22%3A24%7D".format(query_hash1, ID)
f1 = session.get(followerURL).text
followerRaw = json.loads(f1)
hasNext = True
while(hasNext == True and followerRaw):
	time.sleep(1.5)
	for user in followerRaw['data']['user']['edge_followed_by']['edges']:
		if(user['node']['followed_by_viewer'] == False):
			print(user['node']['username'])
			


	hasNext = followerRaw['data']['user']['edge_followed_by']['page_info']['has_next_page']
	
	followerCount = followerRaw['data']['user']['edge_followed_by']['count']
	
	after = re.sub('=', '', followerRaw['data']['user']['edge_followed_by']['page_info']['end_cursor'])
	
	
	followerURL = "https://www.instagram.com/graphql/query/?query_hash={}&variables=%7B%22id%22%3A%22{}%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Afalse%2C%22first%22%3A12%2C%22after%22%3A%22{}%3D%3D%22%7D".format(query_hash1, ID, after)

	f1 = session.get(followerURL).text

	followerRaw = json.loads(f1)




