import pandas as pd
from io import BytesIO
from zipfile import ZipFile
import urllib
from urllib.request import urlopen, Request
import io

'''
This script reads raw ISR data and drops duplicates by keeping the maximum
MODIFIED_DATE for each CARD_NO, dropping all REDACTED fields and then randomly
dropping any other duplicate ISRs as identified in CARD_NO. This should be
modified if we figure out how to identify the row of data with the most recent
information.
'''

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

urls = ['http://home.chicagopolice.org/wp-content/uploads/2019/06/ISR-Data-2016-2017.zip',
'http://home.chicagopolice.org/wp-content/uploads/2019/06/ISR-Data-2018.zip']
for url in urls:
	req = Request(url=url, headers=headers)
	html=urllib.request.urlopen(req)
	zipfile = ZipFile(BytesIO(html.read()))
	zipfile.extractall()

ISR_2018 = pd.read_csv("01-JAN-18 thru 01-JAN-19 - ISR- JUV Redacted.csv")
ISR_2016 = pd.read_csv("01-JAN-2016 to 28-FEB-2017 - ISR - JUV Redacted.csv")
ISR_2017 = pd.read_csv("29-FEB-2016 thru 16-JAN-2018 - ISR - JUV Redacted.csv")
ALL_ISRS = [ISR_2018, ISR_2017, ISR_2016]

def run():
	try:
		return pd.read_csv("isrs_16-18.csv")
	except:
		isrs_all = pd.concat(ALL_ISRS, sort=True)
		isrs_all.drop_duplicates(inplace=True)
		isrs_all = isrs_all.loc[isrs_all.CARD_NO != 'REDACTED']
		isrs_all['CONTACT_DATE'] = pd.to_datetime(isrs_all.CONTACT_DATE,
											      format='%m/%d/%y %H:%M',
											      infer_datetime_format=True)
		isrs_all['year'] = isrs_all.apply(lambda x: x['CONTACT_DATE'].year, axis=1)
		isrs_all['month'] = isrs_all.apply(lambda x: x['CONTACT_DATE'].month, axis=1)

		#DROPPING DUPLICATE CONTACT_CARD BASED ON MODIFIED_DATE FIELD
		isrs_all['MODIFIED_DATE'] = pd.to_datetime(isrs_all.MODIFIED_DATE, 
												   format='%m/%d/%y %H:%M',
												   infer_datetime_format=True)
		max_dates = pd.DataFrame(
			isrs_all.groupby('CARD_NO')['MODIFIED_DATE'].max()).reset_index()
		isrs_max = isrs_all.merge(max_dates, on=['CARD_NO', 'MODIFIED_DATE'])
		isrs_unique = isrs_max.drop_duplicates('CARD_NO')
		isrs_unique['month_year'] = \
			pd.to_datetime(isrs_unique['CONTACT_DATE']).dt.to_period('M')
		isrs_unique.to_csv("isrs_16-18.csv")
		return isrs_unique