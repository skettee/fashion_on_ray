import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from datetime import timedelta

# moabot 컴포넌트를 가져온다.
import moabot_database as moabot
from moabot_id import *

# 사이트 이름
site_name = 'ray'
# 사이트에서 가져올 내용
section_name = 'fashion'
# 사이트 주소
site_url = 'https://ray-web.jp/fashion'
print('site url is: ', site_url)

# 사이트의 HTML을 가져온다.
try:
    response = requests.get(site_url)
    # 에러가 발생 했을 경우 에러 내용을 출력하고 종료한다.
    response.raise_for_status()
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
        print(f'Other error occurred: {err}')
else:
    html_source = response.text
    #print(response.status_code)
    #print(html_source)
    
    # BeautifulSoup 오브젝트를 생성한다.
    soup = BeautifulSoup(html_source, 'html.parser')
    
    # 디버그를 위해서 page의 소스를 파일로 저장한다.
    # 봇으로 등록하기 위해서는 주석처리를 해야한다.
    #import os.path
    #file_name = site_name + '_requests.html'
    #if not os.path.isfile(file_name):
    #    print('file save: ', file_name)
    #    with open(file_name, 'w') as f:
    #        f.write(soup.prettify())
    
    # 데이터를 저장할 데이터베이스를 연다. 
    # bot_id는 moabot_id에서 가져오는 변수값이다.
    # 프로그램을 종료하기 전에 데이터 베이스를 닫아야 한다.
    db_name = section_name + '_on_' + site_name 
    my_db = moabot.Dbase(db_name, bot_id)
    
    soup = soup.find('ul', class_='topic_list')
    # 반복해서 리스트의 목록을 하나씩 검색하고 데이터를 수집한다.
    for post in soup.find_all('li', class_='ray'):
        href = post.find('a', href=True)['href']
        #print('href: ', href)
        href_url = 'https://ray-web.jp' + href + '?page=1'
        #print('url: ', href_url)
        
        # 1. 작성일
        moa_createdAt = post.find('time').text.strip()
        # 2019/04/03
        moa_createdAt = datetime.strptime(moa_createdAt, '%Y/%m/%d')
        # UTC 값으로 변경하기 위해서 9시간을 뺀다. 
        # datetime.timedelta([days,] [seconds,] [microseconds,] [milliseconds,] [minutes,] [hours,] [weeks])
        moa_createdAt = moa_createdAt - timedelta(hours=9)
        #print('createdAt: ', moa_createdAt)
        
        # 2. 타이틀
        moa_title = post.find('p').text.strip()
        #print('title: ', moa_title)
        
        # 포스트의 주소로 이동한다.
        try:
            response =  requests.get(href_url)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
                print(f'Other error occurred: {err}')
        else:
            subhtml_source = response.text
            subsoap = BeautifulSoup(subhtml_source, 'html.parser')
            #with open(f'{site_name}_section_request.html', 'w') as f:
            #    f.write(subsoap.prettify())
            #break
            
            # 3. 이미지
            moa_image = subsoap.find('meta', property="og:image")
            if moa_image:
                moa_image = moa_image['content']
            # 4. 사이트 이름
            moa_site_name = subsoap.find('meta', property="og:site_name")
            if moa_site_name:
                moa_site_name = moa_site_name['content']
            # 6. URL
            moa_url = subsoap.find('meta', property="og:url")
            if moa_url:
                moa_url = moa_url['content']
            # 8. 현재 날짜와 시간을 수집한다.
            moa_timeStamp = datetime.now()
            # 9. 만든사람 정보를 수집한다.
            for item in subsoap.find('div', class_='post_cont').find_all('p'):
                if item.text.find('撮影') != -1:
                    moa_createdBy = item.text.strip()
                    break
            
            # 데이터베이스에 있는 포스트와 중복되는지를 확인하고 
            # JSON형식으로 수집한 데이터를 변환한다.
            if my_db.isNewItem('title', moa_title):
                # 데이터 타입을 확인한다.
                assert type(moa_title) == str, 'title: type error'
                assert type(moa_url) == str, 'url: type error'
                assert type(moa_image) == str, 'image: type error'
                assert type(moa_site_name) == str, 'siteName: type error'
                assert type(moa_createdBy) == str, 'createdBy: type error'
                assert type(moa_createdAt) == datetime, 'createdAt: type error'
                assert type(moa_timeStamp) == datetime, 'timeStamp: type error'

                db_data = { 'title': moa_title, 
                    'url': moa_url,
                    'image': moa_image,
                    'siteName': moa_site_name,
                    'createdBy': moa_createdBy,
                    'createdAt': moa_createdAt,
                    'timeStamp': moa_timeStamp
                }

                # 디버그를 위해서 수집한 데이터를 출력한다.
                temp_data = db_data.copy()
                print(json.dumps(temp_data, indent=4, ensure_ascii=False, default=str))

                # 수집한 데이터를 데이터베이스에 전송한다.
                my_db.insertTable(db_data) 

                # one stop break
                break
                
    # 데이터 베이스를 닫는다.
    my_db.close()
        