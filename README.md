# ssclient
A quick, dirty, and hopefully-not-terribly-brittle **UNOFFICIAL** Python client for Simplisafe's new [webapp](https://webapp.simplisafe.com) API.

## Dependencies
* certifi==2018.1.18
* chardet==3.0.4
* HTMLParser==0.0.2
* idna==2.6
* requests==2.18.4
* urllib3==1.22

## Configuration
The client requires a JSON file with your Simplisafe username and password. An example is provided. Aside from that, it should work out of the box. If it breaks you might be able to click around in the [official app](https://webapp.simplisafe.com) while you watch the requests fly by in your favorite browser's Developer Tools to spot what has changed. If you're feeling particularly generous you might even consider shooting me a PR with those changes.

## Basic Usage
Here are sample invocations for all the methods you'll probably be interested in.
```
>>> from ssclient import SSClient
>>> ssc = SSClient("ssclient-config.json")
>>> ssc.token
u'/34f34f398fNOTAREALTOKENBUTYOUGETTHEIDEA6g7hj89f7hj8='
>>> ssc.getAlarmState()
u'home'
>>> ssc.getAlarmStateLastChange()
1522206642
>>> ssc.setAlarmState("off")
{u'requestedState': u'off', u'reason': None, u'lastUpdated': 1522207069, u'success': True}
>>> ssc.refreshAlarmData()
>>> ssc.getAlarmState()
u'off'
>>> ssc.getAlarmStateLastChange()
1522207076
>>> ssc.invalidateToken(ssc.token)
```

## Disclaimer
**This client is not maintained or otherwise supported by Simplisafe, Inc., nor is this project affiliated with that company in any way.**


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


If you're interested in this client, you're presumably using a Simplisafe system to protect something of value (which may [not be a good idea](http://blog.ioactive.com/2016/02/remotely-disabling-wireless-burglar.html)...) and aware of the security implications of running a script that can manipulate your alarm system. If you have any doubts, please only operate your Simplisafe system through the numerous officially-supported mechanisms. This client is a tool (hey! no remarks about its author...) and you are solely responsible for what you do with it.
