from BeautifulSoup import BeautifulSoup 
import urllib2
import json

ORG_URL = 'https://phonebook.mozilla.org/tree.php'

def install_auth_handler(username, password):
    pw_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    pw_manager.add_password(realm=None,
                            uri=ORG_URL,
                            user=username,
                            passwd=password)
    auth_handler = urllib2.HTTPBasicAuthHandler(pw_manager)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

def direct_reports(content, email):
    direct_reports = []
    # if 'leaf' in the class for person entry they do not have reports
    person = content.find(id="%s" % email.replace('@', '-at-'))
    if "leaf" in person['class']:
        print "%s has no direct reports" % person['id'].replace('-at-', '@')
        direct_reports.append(person['id'].replace('-at-', '@'))
    else:
        print "%s has direct reports" % person['id'].replace('-at-', '@')
        reports = person.findNext("ul").findAll("li")
        for report in reports:
            direct_reports.append(report['id'].replace('-at-', '@'))
    print direct_reports

def main():
    config = json.load(open('config.json', 'r'))
    install_auth_handler(config['username'], config['password'])
    url = urllib2.urlopen(ORG_URL)
    content = url.read()
    soup = BeautifulSoup(content)
    orgchart = soup.find(id="orgchart")

    direct_reports(orgchart, "lsblakk@mozilla.com")
    direct_reports(orgchart, "mitchell@mozilla.com")

#TODO
# accept an email address, get the direct reports, return the list of bugmail
# Then in the main dash can build a query from someone's user account with either what's assigned to their reports
# OR if no reports, assigned to self
# filter by tracking/approvals/security/need-info

if __name__ == '__main__':
    main()