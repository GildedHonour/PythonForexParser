import urllib2
from BeautifulSoup import BeautifulSoup
import MySQLdb
import re
import sys, getopt
import datetime

base_url = 'http://www.dailyfx.com/calendar'
request_url_pattern = 'http://www.dailyfx.com/calendar?tz=&sort=date&week={0}%2F{1}&eur=true&usd=true&jpy=true&gbp=true&chf=true&aud=true&cad=true&nzd=true&cny=true&high=true&medium=true&low=true'

class EST(datetime.tzinfo):
    def utcoffset(self, dt):
      return datetime.timedelta()

    def dst(self, dt):
        return datetime.timedelta(0)

def get_current_date_time_est():
  datetime.datetime.now(EST()) 

def main():
  
  if '--up_till_now' in sys.argv:
    if '--year' in sys.argv:
      year = sys.argv[3]
    else:
      year = 2012
    
    soup = get_soup(request_url_pattern.format(year, '0101'))
    this_week_link = soup.find('div', {'id': 'e-cal-control-top'}).findAll('span')[1].find('a').get('href', '')
    next_week_link = None
    
    while True:
      week_data_array = scrape_week_data(soup)
      insert_data_up_till_now(week_data_array)
      if next_week_equals_this_week(soup, this_week_link):
        break

      soup = get_soup(parse_next_week_url(next_week_link))
      print 'parse_next_week_url(next_week_link)-----', parse_next_week_url(next_week_link) # DEBUG!!!!!!!!!!!!

    print '---------done for "up till now"---------------' # DEBUG!!!!!!!!!!!!
  
  elif '--clear' in sys.argv:
    clear_db()
    print 'Database has been cleaned up.'

  else:
    soup = get_soup(base_url)
    current_week_data_array = scrape_week_data(soup)
    current_time = parse_current_date_time()
    clear_current_week_data()
    upsert_current_week_data(current_week_data_array)

def scrape_week_data(soup):
  last_date = None
  i = 0 # DEBUG!!!!!!!!!!!!
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
    if notes_raw:
      notes = notes_raw.find('td')[1].find('div').text
    else:
      notes = ''

    print('notes', notes)
    item['notes'] = notes

    item_list.append(item)
    i += 1 # DEBUG!!!!!!!!!!!!
    print i # DEBUG!!!!!!!!!!!!

def parse_next_week_url(next_week_link):
  next_week_url_raw = re.search("javascript:setWeek\(\'(.*)\'\)", next_week_link)
  return request_url_pattern.format(next_week_url_raw.group(1)[:4], next_week_url_raw.group(1)[5:])

def insert_data_up_till_now(data_array):
  def insert_data_up_till_now0(cursor):
    sql_pattern = 'INSERT INTO ForexCurrencies(Date, Time, Currency, Event, Importance, Actual, Forecast, Previous, Notes) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})'
    for item in data_array:
      sql = sql_pattern.format(item['date'], item['time'], item['currency'], item['event'], item['importance'], item['actual'], item['forecast'], item['previous'], item['notes'])
      cursor.execute(sql)
  
  execute_db_statement(insert_data_up_till_now0)
  

def insert_data_array(data_array):
  def insert_data_array0(cursor):
    sql_pattern = 'INSERT INTO ForexCurrencies(Date, Time, Currency, Event, Importance, Actual, Forecast, Previous, Notes) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})'
    for item in data_array:
      sql = sql_pattern.format(item['date'], item['time'], item['currency'], item['event'], item['importance'], item['actual'], item['forecast'], item['previous'], item['notes'])
      cursor.execute(sql)

  execute_db_statement(insert_data_array0)

def scrape_current_week_data(soup):
  soup = get_soup(base_url)
  this_week_link = soup.find('div', {'id': 'e-cal-control-top'}).findAll('span')[1].find('a').get('href', '')

def upsert_current_week_data(data_array):
  def upsert_current_week_data0(cursor):
    current_date_time = get_current_date_time_est()
    for item in data_array:
      if not record_exists(cursor, item):
        insert_record(cursor, item)
      elif item.date < current_date_time and item.time < current_date_time:
        continue
      else:
        sql = sql_pattern.format(item['date'], item['time'], item['currency'], item['event'], item['importance'], item['actual'], item['forecast'], item['previous'], item['notes'])
        cursor.execute(sql)

  execute_db_statement(upsert_current_week_data0)

def clear_db():
  execute_db_statement(lambda cursor: cursor.execute('DELETE FROM ForexCurrencies'))

def get_soup(url):
  html_page = urllib2.urlopen(url)
  return BeautifulSoup(html_page.read())

def next_week_equals_current_week(soup, this_week_link):
  next_week_link = soup.find('div', {'id': 'e-cal-control-top'}).findAll('span')[3].find('a').get('href', '')
  print 'next_week_link ', next_week_link # DEBUG!!!!!!!!!!!!
  return this_week_link == next_week_link

def record_exists(cursor, item):
  sql_pattern = 'SELECT COUNT(1) FROM ForexCurrencies WHERE Date={0} AND Time={1}'
  sql = sql_pattern.format(item['date'], item['time'], item['currency'], item['event'], item['importance'], item['actual'], item['forecast'], item['previous'], item['notes'])
  cursor.execute(sql)
  return cursor.fetchone()[0]

def insert_record(cursor, item):
  sql_pattern = 'INSERT INTO ForexCurrencies(Date, Time, Currency, Event, Importance, Actual, Forecast, Previous, Notes) VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})'
  sql = sql_pattern.format(item['date'], item['time'], item['currency'], item['event'], item['importance'], item['actual'], item['forecast'], item['previous'], item['notes'])
  cursor.execute(sql)

def execute_db_statement(code_block):
  db = MySQLdb.connect(host='localhost', user='alex', passwd='', db='test')
  cursor = db.cursor()
  code_block(cursor)
  db.close()

if __name__ == "__main__":
  main()