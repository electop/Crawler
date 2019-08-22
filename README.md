## Crawler
> https://tariat.tistory.com/100

## Prerequites
>
```
import re
import math
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import sys
import datetime
import dateutil.relativedelta
import mysql.connector
from sqlalchemy import create_engine
from mysql.connector import errorcode
```
## How to use
>
```
python main.py --user xxxx --password 'xxxx' --host 'xx.xx.xx.xx' --port xxxx --structure xxxx --table xxxx --key 'xxxx' --structure xxxx --auction xxxx --cost xxxx
```
## Help for options
>
```
--user : user name of MySQL (e.g.: root)
--password : password of username
--host : host of MySQL (e.g.: 127.0.0.1)
--port : port of mySQl (e.g.: 3306)
--key : OPen API key (e.g.: 9ActTOxJHu43bYcBJRqA3rM4nzaC4k...)
--structure : structure name (e.g.: wordpress)
--auction : auction table name (e.g.: wp_custom_xxx)
--cost : cost table name (e.g.: wp_custom_xxx)
```
