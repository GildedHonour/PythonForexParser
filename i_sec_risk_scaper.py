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
  tr_all = soup.findAll('tr', {'class': 'e-cal-row empty'})[0] 
  # print(len(tr_all))
  
  date = tr_all.find('td').find('div').find('span').text[3:]
  print('date: ', date)

  time = tr_all.findAll('td')[1].text
  print('time: ', time)

  currency = tr_all.findAll('td')[2].find('img').get('alt', '')[10:]
  print('currency: ', currency)

  event = tr_all.findAll('td')[3].text
  print('event: ', event)

  importance_raw = tr_all.findAll('td')[4].get('class')
  importance = re.search('\s\w+$', importance_raw) 
  print('importance: ', importance.group(0))

  actual = tr_all.findAll('td')[5].find('span').text
  print('actual: ', actual)

  forecast = tr_all.findAll('td')[6].text
  print('forecast: ', forecast)

  previous = tr_all.findAll('td')[7].find('span').text
  print('previous: ', previous)

  # notes = tr_all.findAll('td')[8].find('div').text
  # print('notes: ', notes)

  print('done!')

if __name__ == "__main__":
  main()