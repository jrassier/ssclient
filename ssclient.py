from HTMLParser import HTMLParser
import requests
import re
import json
import sys
import io

class SSClient:

  app_url = 'https://webapp.simplisafe.com/'
  base_url = 'https://api.simplisafe.com/v1'
  app_name = 'WebApp.simplisafe.com'
  token_path = '/api/token'
  authcheck_path = '/api/authCheck'
  users_path = '/users'
  subscriptions_path = '/subscriptions'
  
  useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'

  # I haven't tested to see if the backend cares about our user-agent
  # string. Feel free to change it and see what happens.

  std_headers = \
  {
    'Origin': 'https://webapp.simplisafe.com',
    'Referer': 'https://webapp.simplisafe.com/',
    'User-Agent': useragent,
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.5'
  }

  cfg = []
  appinfo = {}
  token = ""
  userid = ""
  sub = {}

  def __init__(self, cfgfile):
    with open(cfgfile) as config_file:
      self.cfg = json.load(config_file)

    self.appinfo = self.getWebappInfo()
    self.token = self.getToken(self.appinfo)
    self.userid = self.getUserId(self.token)
    self.sub = self.getSubscription(self.userid, self.token)
  
  def getWebappInfo(self):
    # This method scrapes the user-facing login page for the uuid and
    # version values we'll need to inject into the 'user' field of the
    # 'Authorization' header and request body of a token request.
 
    # As of this writing, the 'user' value we're after looks like this:
    # 4df55627-46b2-4e2c-866b-1521b395ded2.1-4-0.WebApp.simplisafe.com

    # The version and uuid will likely change when the Simplisafe devs
    # update their app.

    # As of this writing, all the necessary information is in a comment
    # at the very beginning of the 'login' response body so it's pretty
    # easy to scrape.

    appinfo = dict()
    comments = []

    class ssHTMLParser(HTMLParser):
      def handle_comment(self, tag):
        comments.append(tag)
        return

    parser = ssHTMLParser()

    html_result = requests.get(self.app_url, headers = self.std_headers)
    parser.feed(html_result.text)
    parser.close()

    pat = re.compile(' Version (.+) \| (.+) ')
    
    for c in comments:
      m = pat.match(c)

      if(m != None):
        appinfo['version'] = m.group(1)
        appinfo['uuid'] = m.group(2)

        ss_version_string = m.group(1).replace('.','-')
        ss_uuid = m.group(2)
        ss_auth_string = ss_uuid +'.'+ss_version_string+'.'+self.app_name

        appinfo['authstring'] = ss_auth_string

      return appinfo
    
  def getToken(self, webAppInfo):
    # This method submits the username and password provided in the
    # configuration file using the Authorization header value from
    # getWebappInfo
    token_url = self.base_url + self.token_path
    token_req_payload = \
    {
      'grant_type': 'password',
      'username': self.cfg['username'],
      'password': self.cfg['password'],
      'device_id': "WebApp; useragent=\""+self.useragent+"\"; uuid=\""+webAppInfo['uuid']+"\""
    }

    token_resp = requests.post(token_url, auth=(webAppInfo['authstring'],''), headers=self.std_headers, data=token_req_payload)

    json_token = token_resp.json()
    token = json_token['access_token']
    
    return token

  def invalidateToken(self, token):
    # This method issues a HTTP DELETE on the token endpoint with the
    # provided token, invalidating it.
    token_url = self.base_url + self.token_path
    tokendel_headers = self.std_headers
    tokendel_headers['Authorization'] = 'Bearer '+token
    tokendel_resp = requests.delete(token_url, headers=tokendel_headers)
    tokendel_resp.raise_for_status()

  def getUserId(self, token):
    # This method uses the provided token to obtain a numeric user ID,
    # which is the key to subscription data, which contains the readable
    # alarm state value and subscription id, which is the key to
    # manipulating the alarm state.

    authCheck_url = self.base_url + self.authcheck_path

    authCheck_headers = self.std_headers
    authCheck_headers['Authorization'] = 'Bearer '+token

    authcheck_resp = requests.get(authCheck_url, headers = authCheck_headers)
    authcheck_resp.raise_for_status()
    authcheck_resp_json = authcheck_resp.json()

    return authcheck_resp_json['userId']

  def getSubscription(self, userid, token):
    # This method uses the provided userid and token to obtain the
    # collection of subscriptions corresponding to that user.
    
    subscriptions_url = self.base_url + self.users_path + "/" + str(userid) + "/subscriptions?activeOnly=false"
    subscriptions_headers = self.std_headers
    subscriptions_headers['Authorization'] = 'Bearer '+token
    subscriptions_resp = requests.get(subscriptions_url, headers = subscriptions_headers)
    subscriptions_resp.raise_for_status()
    
    return subscriptions_resp.json()

  def getSubscriptionRaw(self, userid, token):
    # If you want the subscription data in its raw JSON instead of a
    # Python object, here's your method.
    
    subscriptions_url = self.base_url + self.users_path + "/" + str(userid) + "/subscriptions?activeOnly=false"
    subscriptions_headers = self.std_headers
    subscriptions_headers['Authorization'] = 'Bearer '+token
    subscriptions_resp = requests.get(subscriptions_url, headers = subscriptions_headers)
    subscriptions_resp.raise_for_status()
    
    return subscriptions_resp.text()

  def getAlarmState(self):
    # Shortcut method: Returns 'off', 'home', or 'away' from the first
    # subscription/location element.
    return self.sub['subscriptions'][0]['location']['system']['alarmState']

  def getAlarmStateLastChange(self):
    # Shortcut method: Returns the UNIX timestamp for the last time the
    # alarm state changed.
    return self.sub['subscriptions'][0]['location']['system']['alarmStateTimestamp']
  
  def refreshAlarmData(self):
    # Exposes a simpler way for implementing code to call
    # getSubscription() after making a change
    self.sub = self.getSubscription(self.userid, self.token)
  
  def setAlarmState(self, state):
    # Sets the state of the alarm corresponding to the first 
    # subscription/location element.
    
    sid = self.sub['subscriptions'][0]['sid']
    state_url = self.base_url + self.subscriptions_path + "/" + str(sid) + "/state?state=" + state
    state_headers = self.std_headers
    state_headers['Authorization'] = 'Bearer '+self.token
    state_resp = requests.post(state_url, headers = state_headers)
    state_resp.raise_for_status()
    
    return state_resp.json()
