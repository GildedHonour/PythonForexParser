import urllib2
from BeautifulSoup import BeautifulSoup
import MySQLdb
import re

db = MySQLdb.connect(host="localhost", user="alex", passwd="", db="test")
cur = db.cursor()

def main():
  url = 'http://www.dailyfx.com/calendar?cmp=SFS-70160000000E4zK'
  html_page = urllib2.urlopen(url)
  soup = BeautifulSoup(html_page.read())
  last_date = None
  i = 0
  for tr_item in soup.findAll('tr', {'class': 'e-cal-row empty'}):
    # print('tr_item: ', tr_item)
    date_raw = tr_item.find('td').find('div')
    # print 'date_raw:', date_raw
    if date_raw:
      date = date_raw.find('span').text[3:]
      last_date = date
    else:
      date = last_date

    print('date: ', date)

    time = tr_item.findAll('td')[1].text
    print('time: ', time)

    currency = tr_item.findAll('td')[2].find('img').get('alt', '')[10:]
    print('currency: ', currency)

    event = tr_item.findAll('td')[3].text
    print('event: ', event)

    importance_raw = tr_item.findAll('td')[4].get('class')
    importance = re.search('\s\w+$', importance_raw) 
    print('importance: ', importance.group(0))

    actual = tr_item.findAll('td')[5].find('span').text
    print('actual: ', actual)

    forecast = tr_item.findAll('td')[6].text
    print('forecast: ', forecast)

    previous = tr_item.findAll('td')[7].find('span').text
    print('previous: ', previous)

    notes_raw = tr_item.findAll('td')[8].get('class')
    if notes_raw:
      notes = notes_raw.find('td')[1].find('div').text
      print('notes', notes)
    else:
      print('no notes')

    i += 1
    print(i, ' -----------------------------------')

if __name__ == "__main__":
  main()