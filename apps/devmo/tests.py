from nose.tools import eq_
import test_utils

import shlex
import urllib2

from devmo.helpers import devmo_url

def parse_robots(base_url):
    """ Given a base url, retrieves the robot.txt file and
        returns a list of rules. A rule is a tuple. 
        Example:
        [("User-Agent", "*"), ("Crawl-delay", "5"),
         ...
         ("Disallow", "/template")]

        Tokenizes input to whitespace won't break
        these acceptance tests.
    """
    rules = []
    robots = shlex.shlex(urllib2.urlopen("%s/robots.txt" % base_url))
    robots.whitespace_split = True
    token = robots.get_token()
    while token:
        rule = None
        if token[-1] == ':':
            rule = (token[0:-1], robots.get_token())
        if rule:
            rules.append(rule)
        token = robots.get_token()
    return rules

class TestDevMoRobots(test_utils.TestCase):
    """ These are really acceptance tests, but we seem to lump
        together unit, integration, regression, and 
        acceptance tests """
    def test_production(self):
        rules = [
            ("User-Agent", "*"),
            ("Crawl-delay", "5"), 
            ("Sitemap", "sitemap.xml"), 
            ("Request-rate", "1/5"), 
            ("Disallow", "/@api/deki/*"), 
            ("Disallow", "/*feed=rss"),
            ("Disallow", "/*type=feed"),
            ("Disallow", "/skins"),
            ("Disallow", "/template:"),
        ]
        eq_(parse_robots('http://developer.mozilla.org'),  rules)
        eq_(parse_robots('https://developer.mozilla.org'), rules)

    def test_stage_bug607996(self):
        rules = [
            ("User-agent", "*"),
            ("Disallow", "/"),
        ]

        #No https://mdn.staging.mozilla.com, this serves up Sumo
        eq_(parse_robots('http://mdn.staging.mozilla.com'), rules)

        eq_(parse_robots('https://developer-stage.mozilla.org'), rules)
        eq_(parse_robots('http://developer-stage.mozilla.org'),  rules)

        eq_(parse_robots('https://developer-stage9.mozilla.org'), rules) 
        eq_(parse_robots('http://developer-stage9.mozilla.org'),  rules) 

class TestDevMoHelpers(test_utils.TestCase):
    def test_devmo_url(self):
        en_only_page = '/en/HTML/HTML5'
        localized_page = '/en/HTML'
        req = test_utils.RequestFactory().get('/')
        context = {'request':req}

        req.locale = 'en-US'
        eq_(devmo_url(context, en_only_page), en_only_page)
        req.locale = 'de'
        eq_(devmo_url(context, localized_page), '/de/HTML')
        req.locale = 'zh-TW'
        eq_(devmo_url(context, localized_page), '/zh_tw/HTML')