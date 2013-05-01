import urllib2
from BeautifulSoup import BeautifulSoup
import MySQLdb
import re
import sys, getopt

base_url = 'http://www.dailyfx.com/calendar'
request_url_pattern = 'http://www.dailyfx.com/calendar?tz=&sort=date&week={0}%2F{1}&eur=true&usd=true&jpy=true&gbp=true&chf=true&aud=true&cad=true&nzd=true&cny=true&high=true&medium=true&low=true'

def main():
  if '--up_till_now' in sys.argv:
    html_page = urllib2.urlopen(request_url_pattern.format('2012', '0101'))
    soup = BeautifulSoup(html_page.read())
    this_week_link = soup.find('div', {'id': 'e-cal-control-top'}).findAll('span')[1].find('a').get('href', '')
    next_week_link = None
    
    while True:
      week_data_array = scrape_week_data_up_till_now(soup)
      insert_data_up_till_now(week_data_array)
      
      next_week_link = soup.find('div', {'id': 'e-cal-control-top'}).findAll('span')[3].find('a').get('href', '')
      print 'next_week_link ', next_week_link
      if this_week_link == next_week_link:
        break

      html_page = urllib2.urlopen(parse_next_week_url(next_week_link))
      print 'parse_next_week_url(next_week_link)-----', parse_next_week_url(next_week_link)
      soup = BeautifulSoup(html_page.read())

    current_week_data_array = scrape_current_week_data(soup)
    upsert_current_week_data(current_week_data_array)

    print 'done!!!!!'

def scrape_week_data_up_till_now(soup):
  last_date = None
  i = 0
  item_list = []
  for tr_item in soup.findAll('tr', {'class': 'e-cal-row empty'}):
    date_raw = tr_item.find('td').find('div')
    if date_raw:
      date = date_raw.find('span').text[3:]
      last_date = date
    else:
      date = last_date

    print('date: ', date)
    item = {'date': date}

    time = tr_item.findAll('td')[1].text
    print('time: ', time)
    item['time'] = time

    currency = tr_item.findAll('td')[2].find('img').get('alt', '')[10:]
    print('currency: ', currency)
    item['currency'] = currency

    event = tr_item.findAll('td')[3].text
    print('event: ', event)
    item['event'] = event

    importance_raw = tr_item.findAll('td')[4].get('class')
    importance = re.search('\s\w+$', importance_raw) 
    print('importance: ', importance.group(0))
    item['importance'] = importance

    actual = tr_item.findAll('td')[5].find('span').text
    print('actual: ', actual)
    item['actual'] = actual

    forecast = tr_item.findAll('td')[6].text
    print('forecast: ', forecast)
    item['forecast'] = forecast

    previous = tr_item.findAll('td')[7].find('span').text
    print('previous: ', previous)
    item['previous'] = previous

    notes_raw = tr_item.findAll('td')[8].get('class')
    notes = if notes_raw:
      notes_raw.find('td')[1].find('div').text
    else:
      ''
    print('notes', notes)
    item['notes'] = notes

    item_list.append(item)
    i += 1
    print i

def parse_next_week_url(next_week_link):
  next_week_url_raw = re.search("javascript:setWeek\(\'(.*)\'\)", next_week_link)
  a = request_url_pattern.format(next_week_url_raw.group(1)[:4], next_week_url_raw.group(1)[5:])
  print 'date: ', next_week_url_raw.group(1)[:4], next_week_url_raw.group(1)[5:]
  print ' -----------------------------------'
  return a 

def insert_data_up_till_now(data_array):
  db = MySQLdb.connect(host="localhost", user="alex", passwd="", db="test")
  cursor = db.cursor()
  sql_pattern = 'INSERT INTO ForexCurrencies(Date, Time, Currency, Event, Importance, Actual, Forecast, Previous, Notes) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})'
  for item in data_array:
    sql = sql_pattern.format(item['date'], item['time'], item['currency'], item['event'], item['importance'], item['actual'], item['forecast'], item['previous'], item['notes'])
    cursor.execute(sql)

  db.close()

def insert_data_array(data_array):
  db = MySQLdb.connect(host="localhost", user="alex", passwd="", db="test")
  cursor = db.cursor()
  sql_pattern = 'INSERT INTO ForexCurrencies(Date, Time, Currency, Event, Importance, Actual, Forecast, Previous, Notes) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})'
  for item in data_array:
    sql = sql_pattern.format(item['date'], item['time'], item['currency'], item['event'], item['importance'], item['actual'], item['forecast'], item['previous'], item['notes'])
    cursor.execute(sql)

  db.close()

def scrape_current_week_data(soup):
  pass

def upsert_current_week_data(data_array):
  pass


if __name__ == "__main__":
  main()