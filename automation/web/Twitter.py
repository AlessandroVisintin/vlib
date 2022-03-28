from urllib.parse import quote_plus
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
    
    
    def __init__(self, browser, **kwargs):
        
        self.bname = browser
        self.out = '.'
        if 'out_folder' in kwargs:
            self.out = kwargs['out_folder']
        
        #self.db = SQLite(self.out, 'Twitter.db')
        #self.db.create_table(
        #    name='Users',
        #    cols=[('uid','INTEGER'),('uname','TEXT'),('cdate','INTEGER')],
        #    key=('uid',)
        #)
        #self.db.create_table(
        #    name='Info',
        #    cols=[('uid','INTEGER'),('stamp','INTEGER'),('fng','INTEGER'),('fws','INTEGER'),('twt','INTEGER'),('img','INTEGER'),('nam','TEXT'),('dsc','TEXT'),('loc','TEXT')],
        #    key=('uid','stamp')
        #)
        #self.db.create_table(
        #    name='Followers',
        #    cols=[('uid1','INTEGER'),('uid2','INTEGER'),('top','INTEGER'),('btm','INTEGER'),('idx','INTEGER')],
        #    key=('uid1','uid2')
        #)
        
        self.brs = Browser(self.bname, **kwargs)


    def load_session(self, email, username, password):
        SESSION = 'twitter_session.json'
        if os.path.exists(f'{self.out}/{SESSION}'):
            with open(f'{self.out}/{SESSION}', 'r') as f:
                out = json.load(f)    
                if (time.time() - out['t']) < 86400:
                    self.brs.get('https://twitter.com')
                    for cookie in out['c']:
                        self.brs.set_cookie(cookie)
                    self.brs.get('https://twitter.com')
                    return
        
        self.brs.get('https://twitter.com/i/flow/login')
        self.brs.send('input[autocomplete="username"]', email)
        self.brs.click('#layers > div > div > div > div > div > div > div.css-1dbjc4n.r-1awozwy.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv > div.css-1dbjc4n.r-1867qdf.r-1wbh5a2.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1.r-htvplk.r-1udh08x > div > div > div.css-1dbjc4n.r-14lw9ot.r-6koalj.r-16y2uox.r-1wbh5a2 > div.css-1dbjc4n.r-16y2uox.r-1wbh5a2.r-1jgb5lz.r-1ye8kvj.r-13qz1uu > div.css-1dbjc4n.r-16y2uox.r-1wbh5a2.r-1dqxon3 > div > div > div:nth-child(6) > div > span > span',
                       sleep=2)

        if self.brs.wait('input[data-testid="ocfEnterTextTextInput"]', timeout=3):
            self.brs.send('input[data-testid="ocfEnterTextTextInput"]', username)
            self.brs.click('#layers > div > div > div > div > div > div > div.css-1dbjc4n.r-1awozwy.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv > div.css-1dbjc4n.r-1867qdf.r-1wbh5a2.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1.r-htvplk.r-1udh08x > div > div > div.css-1dbjc4n.r-14lw9ot.r-6koalj.r-16y2uox.r-1wbh5a2 > div.css-1dbjc4n.r-16y2uox.r-1wbh5a2.r-1jgb5lz.r-1ye8kvj.r-13qz1uu > div.css-1dbjc4n.r-hhvx09.r-1dye5f7.r-ttdzmv > div > div > span',
                           sleep=2)
        
        self.brs.send('input[name="password"]', password)
        self.brs.click('span.css-bfa6kz:nth-child(1) > span:nth-child(1)',
                       sleep=2)
        
        os.makedirs(self.out, exist_ok=True)
        with open(f'{self.out}/{SESSION}', 'w') as f:
            out = {'t': int(time.time()), 'c' : self.brs.get_info('cookies')}
            f.write(json.dumps(out))
            f.flush()


    def user_info(self, uname):
        out, data = {}, {}
        self.brs.get(f'https://www.twitter.com/{uname}', sleep=2)
        
        while True:
            try:
                for log in self.brs.get_xhr(reset=True):
                    if 'UserByScreenName' in log['req.url']:
                        data = json.loads(log['res.body'])
                        break
                data = data['data']['user']['result']
                break
            except KeyError:
                time.sleep(5)
                continue
            
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


    def crawl_followers(self, uname, crs=None, verbose=True, res=3600):
        with open(f'{self.out}/fwers_{uname}', 'a+') as f:

            ui = self.user_info(uname)
            f.write(f'u\t{int(time.time())}\t{ui["uid"]}\t{ui["uname"]}\t{ui["cdate"]}')
            f.write(f'\t{ui["fng"]}\t{ui["fws"]}\t{ui["twt"]}\t{ui["img"]}')
            f.write(f'\t{quote_plus(ui["nam"])}\n')
            #f.write(f'\t{quote_plus(ui["dsc"])}\t{quote_plus(ui["loc"])}')
            
            self.brs.get(f'https://www.twitter.com/{uname}/followers', sleep=2)
            self.brs.wait('section.css-1dbjc4n:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1)')
        
            pos, flag = 500, True
            while flag:
                self.brs.scroll(pos)
                pos += 500
                headers, url = {}, None
                for log in self.brs.get_xhr(reset=True):
                    if 'Followers' in log['req.url'] and 'cursor' in log['req.url']:
    
                        headers = {k.lower():v for k,v in log['req.headers'].items()}
                        url = unquote_plus(log['req.url'])
                        flag = False
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
            variables['count'] = 100
            if crs is not None:
                variables['cursor'] = crs
            
            xratelim = None
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
                
                try:
                    data = json.loads(response.text)
                    data = data['data']['user']['result']['timeline']['timeline']['instructions'][0]['entries']
                    tmp = [e['content']['itemContent']['user_results']['result'] for e in data if 'user' in e['entryId']]
                except KeyError:
                    time.sleep(60)
                    continue
    
                top = variables['cursor']
                btm = [e['content'] for e in data if 'cursor-bottom' in e['entryId']][0]['value']
                prv = int(top.split('|')[0])
                prv = current_time if prv < 0 else int(Twitter.crs2stamp(prv))
                nxt = int(btm.split('|')[0])
                nxt = ui['cdate'] if nxt == 0 else int(Twitter.crs2stamp(nxt))
                
                f.write(f'c\t{prv}\t{nxt}\n')
                
                count = variables['count']
                if (prv - nxt) > res and count > 1:
                    count = 1 if (count - 5) < 1 else (count - 5)
                    variables['count'] = count
                    if verbose:
                        print(f'count reduced to {count}')
                    continue
                elif (prv - nxt) < (res / 2) and count < 100:
                    count = 100 if (count + 5) > 100 else (count + 5)
                    variables['count'] = count
                    if verbose:
                        print(f'count augmented to {count}')
                
                for e in tmp:
                    f.write(f'f\t{e["rest_id"]}\t{e["legacy"]["screen_name"]}\t')
                    f.write(f'{Twitter.tostamp(e["legacy"]["created_at"])}\t')
                    f.write(f'{e["legacy"]["friends_count"]}\t{e["legacy"]["followers_count"]}\t')
                    f.write(f'{e["legacy"]["statuses_count"]}\t')
                    
                    img = 0 if 'default' in e['legacy']['profile_image_url_https'] else 1
                    f.write(f'{img}\t')
                    
                    f.write(f'{quote_plus(e["legacy"]["name"])}\n')
                    #f.write(f'{quote_plus(e["legacy"]["description"])}\t')
                    #f.write(f'{quote_plus(e["legacy"]["location"])}\n')
                
                if nxt > ui['cdate']:
                    variables['cursor'] = btm
                    try:
                        xratelim = int(response.headers['x-rate-limit-remaining'])
                    except KeyError:
                        xratelim -= 1
                    s = f'{uname} {len(tmp)} {variables["cursor"]}\n{stamp2str(prv)} - {stamp2str(nxt)} - {xratelim}'
                    with open(f'{self.out}/status', 'w') as g:
                        g.write(s)
                    if verbose:
                        print(s)
                    if xratelim < 15:
                        time.sleep(60 * (15 - xratelim))
                    else:
                        time.sleep(1)
                else:
                    return True
