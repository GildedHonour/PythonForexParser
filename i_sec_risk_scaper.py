import urllib2
from BeautifulSoup import BeautifulSoup
import MySQLdb
import re
import sys, getopt
import datetime
import time

DB_USER = 'alex'
DB_PASSWORD = ''
DB_HOST = 'localhost'
DB_NAME = 'test'
BASE_URL = 'http://www.dailyfx.com/calendar'
URL_PATTERN = 'http://www.dailyfx.com/calendar?tz=&sort=date&week={0}%2F{1}&eur=true&usd=true&jpy=true&gbp=true&chf=true&aud=true&cad=true&nzd=true&cny=true&high=true&medium=true&low=true'

def main():
  if '--up_till_now' in sys.argv:
    insert_data_up_till_now()
  elif '--clear' in sys.argv:
    clear_all_db()
  else:
    insert_data_from_now_on()

def scrape_weekly_data(soup, year):
  last_date = None
  item_list = []
  for tr_item in soup.findAll('tr', {'class': re.compile(r'\be-cal-row\b')}):
    date_raw = tr_item.find('td').find('div')
    if date_raw:
      date = date_raw.find('span').text[3:]
      last_date = date
    else:
      date = last_date

    item = {}
    time_str_raw = tr_item.findAll('td')[1].text
    time_str = parse_time_str(time_str_raw)
    item['date_time'] = datetime.datetime.strptime(date + ' ' + year + ' ' + time_str, "%b %d %Y %H:%M")
    item['currency'] = tr_item.findAll('td')[2].find('img').get('alt', '')[10:]
    item['event'] = tr_item.findAll('td')[3].text
    importance_raw = tr_item.findAll('td')[4].get('class')
    item['importance'] = re.search('\s\w+$', importance_raw).group(0)
    item['actual'] = tr_item.findAll('td')[5].find('span').text
    item['forecast'] = tr_item.findAll('td')[6].text
    item['previous'] = tr_item.findAll('td')[7].find('span').text
    notes_raw = tr_item.findAll('td')[8].get('class')
    item['notes'] = notes_raw.find('td')[1].find('div').text if notes_raw else ''

    item_list.append(item)

  return item_list

def insert_data_up_till_now():
  year = sys.argv[3] if '--year' in sys.argv else '2012'
  month_day = sys.argv[5] if '--month_day'in sys.argv else '0101'

  print_formated_string('Inserting data from %s-%s till now' % (year, month_day))
  soup = get_soup(URL_PATTERN.format(year, month_day))
  this_week_link = soup.find('div', {'id': 'e-cal-control-top'}).findAll('span')[1].find('a').get('href', '')
  
  while True:
    week_data_array = scrape_weekly_data(soup, year)
    insert_data_array(week_data_array)
    next_week_link = parse_next_week_link(soup)
    if this_week_link == next_week_link:
      print_formated_string('Data from %s-%s till now has been inserted' % (year, month_day))
      break
    
    url, year = parse_next_week_url(next_week_link)
    soup = get_soup(url)

def insert_data_from_now_on():
  soup = get_soup(BASE_URL)
  current_time = get_current_date_time_est()
  
  print_formated_string('Inserting data from now on %s ...' % current_time)
  current_week_data_array = scrape_weekly_data(soup, str(current_time.year))
  clear_db_from_now_on()
  insert_data_array(current_week_data_array)
  
  while True:
    next_week_link = parse_next_week_link(soup)
    url, year = parse_next_week_url(next_week_link)
    soup = get_soup(url)
    week_data_array = scrape_weekly_data(soup, year)
    if not week_data_array:
      print_formated_string('Data from now on has been inserted')
      break

    insert_data_array(week_data_array)

def parse_next_week_url(next_week_link):
  next_week_url_raw = re.search("javascript:setWeek\(\'(.*)\'\)", next_week_link)
  year = next_week_url_raw.group(1)[:4]
  month_day = next_week_url_raw.group(1)[5:]
  return URL_PATTERN.format(year, month_day), year

def insert_data_array(data_array):
  def insert_data_array0(cursor):
    sql_pattern = 'INSERT INTO ForexCurrencies(Date, Currency, Event, Importance, Actual, Forecast, Previous, Notes) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
    for item in data_array:
      cursor.execute(sql_pattern, (item['date_time'].strftime('%Y-%m-%d %H:%M:%S'), item['currency'], item['event'], item['importance'], item['actual'], item['forecast'], item['previous'], item['notes']))
      print_formated_string('An item has been inserted: ' + str(item))

  execute_db_statement(insert_data_array0)

def clear_all_db():
  execute_db_statement(lambda cursor: cursor.execute('DELETE FROM ForexCurrencies'))
  print_formated_string('Database has been totally cleaned up.')

def clear_db_from_now_on():
  current_date_time_est = get_current_date_time_est_formated()
  execute_db_statement(lambda cursor: cursor.execute("DELETE FROM ForexCurrencies WHERE Date >='{0}'".format(current_date_time_est)))
  print_formated_string('Records from now on %s has been removed.' % current_date_time_est)

def get_soup(url):
  html_page = urllib2.urlopen(url)
  return BeautifulSoup(html_page.read())

def execute_db_statement(code_block):
  db = MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASSWORD, db = DB_NAME, use_unicode = True, charset = 'utf8')
  cursor = db.cursor()
  code_block(cursor)
  db.commit()
  db.close()

def parse_time_str(time_str):
  if time_str == '':
    return '00:00'
  elif time_str.endswith('LIVE'):
    return time_str[:-4]

  return time_str

def parse_next_week_link(soup):
  return soup.find('div', {'id': 'e-cal-control-top'}).findAll('span')[3].find('a').get('href', '')

def get_current_date_time_est():
  return datetime.datetime.now(EST())

def get_current_date_time_est_formated():
  return get_current_date_time_est().strftime('%Y-%m-%d %H:%M:%S')

def print_formated_string(output):
  print '--------------------------------------------'
  print output
  print '--------------------------------------------'

class EST(datetime.tzinfo):
  def utcoffset(self, dt):
    return datetime.timedelta()

  def dst(self, dt):
    return datetime.timedelta(0)

if __name__ == "__main__":
  main()