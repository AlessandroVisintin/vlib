from datetime import datetime as dt
import os, json, requests, time
from urllib.parse import urlparse, unquote_plus
from vlib.automation.web.Browser import Browser
from vlib.database.SQLite import SQLite
from vlib.utils.time import stamp2str


class Twitter:

    
    @staticmethod
    def tostamp(twitter_date):
        t = dt.strptime(twitter_date, '%a %b %d %H:%M:%S %z %Y')
        return int(round(t.timestamp()))
    
    
    @staticmethod
    def crs2stamp(cursor):
        return round((cursor >> 22) / 250, 3)
    
    
    def __init__(self, drv_path, out_path):
        
        self.out = out_path 
        self.drv = drv_path
        
        self.db = SQLite(self.out, 'Twitter.db')
        self.db.create_table(
            name='Users',
            cols=[('uid','INTEGER'),('uname','TEXT'),('cdate','INTEGER')],
            key=('uid',)
        )
        self.db.create_table(
            name='Info',
            cols=[('uid','INTEGER'),('stamp','INTEGER'),('fng','INTEGER'),('fws','INTEGER'),('twt','INTEGER'),('img','INTEGER'),('nam','TEXT'),('dsc','TEXT'),('loc','TEXT')],
            key=('uid','stamp')
        )
        self.db.create_table(
            name='Followers',
            cols=[('uid1','INTEGER'),('uid2','INTEGER'),('top','INTEGER'),('btm','INTEGER'),('idx','INTEGER')],
            key=('uid1','uid2')
        )
        
        self.brs = Browser(self.drv, headless=False)


    def login(self, email, username, password):
        if os.path.exists(f'{self.out}/session.json'):
            with open(f'{self.out}/session.json', 'r') as f:
                out = json.load(f)    
                if (time.time() - out['t']) < 86400:
                    self.brs.get('https://twitter.com')
                    for cookie in out['c']:
                        self.brs.set_cookie(cookie)
                    self.brs.get('https://twitter.com')
                    return
        
        self.brs.get('https://twitter.com/i/flow/login')
        self.brs.send('input[autocomplete="username"]', email)
        self.brs.click(
            '#layers > div > div > div > div > div > div > div.css-1dbjc4n.r-1'
            'awozwy.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv '
            '> div.css-1dbjc4n.r-1867qdf.r-1wbh5a2.r-kwpbio.r-rsyp9y.r-1pjcn9w'
            '.r-1279nm1.r-htvplk.r-1udh08x > div > div > div.css-1dbjc4n.r-14l'
            'w9ot.r-6koalj.r-16y2uox.r-1wbh5a2 > div.css-1dbjc4n.r-16y2uox.r-1'
            'wbh5a2.r-1jgb5lz.r-1ye8kvj.r-13qz1uu > div.css-1dbjc4n.r-16y2uox.'
            'r-1wbh5a2.r-1dqxon3 > div > div > div:nth-child(6) > div > span >'
            ' span', sleep=2)

        if self.brs.wait('input[data-testid="ocfEnterTextTextInput"]', timeout=3):
            self.brs.send('input[data-testid="ocfEnterTextTextInput"]', username)
            self.brs.click(
                '#layers > div > div > div > div > div > div > div.css-1dbjc4n'
                '.r-1awozwy.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r'
                '-g6jmlv > div.css-1dbjc4n.r-1867qdf.r-1wbh5a2.r-kwpbio.r-rsyp'
                '9y.r-1pjcn9w.r-1279nm1.r-htvplk.r-1udh08x > div > div > div.c'
                'ss-1dbjc4n.r-14lw9ot.r-6koalj.r-16y2uox.r-1wbh5a2 > div.css-1'
                'dbjc4n.r-16y2uox.r-1wbh5a2.r-1jgb5lz.r-1ye8kvj.r-13qz1uu > di'
                'v.css-1dbjc4n.r-hhvx09.r-1dye5f7.r-ttdzmv > div > div > span', sleep=2)
        
        self.brs.send('input[name="password"]', password)
        self.brs.click(
            '#layers > div > div > div > div > div > div > div.css-1dbjc4n.r-'
            '1awozwy.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv'
            ' > div.css-1dbjc4n.r-1867qdf.r-1wbh5a2.r-kwpbio.r-rsyp9y.r-1pjcn9'
            'w.r-1279nm1.r-htvplk.r-1udh08x > div > div > div.css-1dbjc4n.r-14'
            'lw9ot.r-6koalj.r-16y2uox.r-1wbh5a2 > div.css-1dbjc4n.r-16y2uox.r-'
            '1wbh5a2.r-1jgb5lz.r-1ye8kvj.r-13qz1uu > div.css-1dbjc4n.r-hhvx09.'
            'r-1dye5f7.r-ttdzmv > div > div.css-18t94o4.css-1dbjc4n.r-1m3jxhj.'
            'r-sdzlij.r-1phboty.r-rs99b7.r-ywje51.r-usiww2.r-peo1c.r-1ps3wis.r'
            '-1ny4l3l.r-1guathk.r-o7ynqc.r-6416eg.r-lrvibr.r-13qz1uu > div > '
            'span > span', sleep=2)
        
        os.makedirs(self.out, exist_ok=True)
        with open(f'{self.out}/session.json', 'w') as f:
            out = {'t': int(time.time()), 'c' : self.brs.get_info('cookies')}
            f.write(json.dumps(out))
            f.flush()


    def user_info(self, uname):
        self.brs.get(f'https://www.twitter.com/{uname}', sleep=2)
        out = {}
        data = {}
        for m, p in self.brs.get_xhr():
            if m['method'] == 'Network.responseReceived' and 'UserByScreenName' in m['params']['response']['url']:
                data = json.loads(p['body'])
                break
        data = data['data']['user']['result']
        out['uid'] = int(data['rest_id'])
        out['uname'] = str(data['legacy']['screen_name'])
        out['cdate'] = Twitter.tostamp(data['legacy']['created_at'])
        out['fng'] = int(data['legacy']['friends_count'])
        out['fws'] = int(data['legacy']['followers_count'])
        out['twt'] = int(data['legacy']['statuses_count'])
        out['img'] = 0 if 'default' in data['legacy']['profile_image_url_https'] else 1
        out['nam'] = str(data['legacy']['name'])
        out['dsc'] = str(data['legacy']['description'])
        out['loc'] = str(data['legacy']['location'])
        return out


    def crawl_followers(self, uname, count=20, crs=None, verbose=True):
        ui = self.user_info(uname)
        user = (ui['uid'], ui['uname'], ui['cdate'])
        cday = int(int(time.time() / 86400) * 86400)
        info = (ui['uid'], cday, ui['fng'], ui['fws'], ui['twt'], ui['img'], ui['nam'], ui['dsc'], ui['loc'])
        self.db.insert_rows(name='Users', rows=[user])
        self.db.insert_rows(name='Info', rows=[info])
        
        self.brs.get(f'https://www.twitter.com/{uname}/followers', sleep=2)
        self.brs.scroll(2000)
        headers = {}
        url = None
        for m, p in self.brs.get_xhr():
            if m['method'] == 'Network.requestWillBeSent' and'/followers' in m['params']['documentURL']:
                if 'Followers' in m['params']['request']['url'] and 'cursor' in m['params']['request']['url']:
                    for k,v in m['params']['request']['headers'].items():
                        headers[k.lower()] = v
                    url = unquote_plus(m['params']['request']['url'])
                    break
        headers['accept-language'] = 'en-GB,en-US;q=0.9,en;q=0.8,it;q=0.7'
        headers['authority'] = 'twitter.com'
        headers['content-type'] = 'application/json'
        headers['accept'] = '*/*'
        headers['sec-fetch-site'] = 'same-origin'
        headers['sec-fetch-mode'] = 'cors'
        headers['sec-fetch-dest'] = 'empty'
        headers['cookie'] = '; '.join([f'{c["name"]}={c["value"]}' for c in self.brs.get_info('cookies')])
        variables = json.loads(urlparse(url).query.split('variables=')[1])
        variables['count'] = count
        if crs is not None:
            variables['cursor'] = crs
        
        while True:
            try:
                current_time = int(round(time.time()))
                params = (('variables', json.dumps(variables)),)
                response = requests.get(url.split('?variables')[0], headers=headers, params=params)
            except BaseException as e:
                print(e)
                print(variables['cursor'])
                time.sleep(60)
                continue
            
            data = json.loads(response.text)
            data = data['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries']
            tmp = [e['content']['itemContent']['user_results']['result'] for e in data if 'user' in e['entryId']]
            users = [
                (
                    int(e['rest_id']),
                    str(e['legacy']['screen_name']),
                    Twitter.tostamp(e['legacy']['created_at'])
                ) for e in tmp]
            info = [
                (
                    int(e['rest_id']),
                    int(int(current_time / 86400) * 86400),
                    int(e['legacy']['friends_count']),
                    int(e['legacy']['followers_count']),
                    int(e['legacy']['statuses_count']),
                    0 if 'default' in e['legacy']['profile_image_url_https'] else 1,
                    str(e['legacy']['name']),
                    str(e['legacy']['description']),
                    str(e['legacy']['location']),
                 ) for e in tmp]
            
            top = variables['cursor']
            btm = [e['content'] for e in data if 'cursor-bottom' in e['entryId']][0]['value']
            prv = int(top.split('|')[0])
            prv = current_time if prv < 0 else int(Twitter.crs2stamp(prv))
            nxt = int(btm.split('|')[0])
            nxt = ui['cdate'] if nxt == 0 else int(Twitter.crs2stamp(nxt))
            followers = [(int(variables['userId']), e[0], prv, nxt, idx)
                    for idx,e in enumerate(users)]
        
            self.db.insert_rows(name='Users', rows=users)
            self.db.insert_rows(name='Info', rows=info)
            self.db.insert_rows(name='Followers', rows=followers)
            
            if nxt > ui['cdate']:
                variables['cursor'] = btm
                remaining = int(response.headers['x-rate-limit-remaining'])
                if verbose:
                    print(f'{stamp2str(prv)} - {stamp2str(nxt)} - {remaining}\n')
                if remaining < 15:
                    time.sleep(60 * (15 - remaining))
                else:
                    time.sleep(1)
            else:
                return