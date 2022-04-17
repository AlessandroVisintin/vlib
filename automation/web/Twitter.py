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
        self.brs = None
        self.headers = None
        self.graphql = {
                'userinfo':None,
                'followers': None
            }
        
        self.kwargs = kwargs


    def load_session(self, email, username, password):
        SESSION = 'twitter_session.json'
        if os.path.exists(f'{self.out}/{SESSION}'):
            with open(f'{self.out}/{SESSION}', 'r') as f:
                out = json.load(f)    
                if (time.time() - out['t']) < (7 * 86400):
                    #self.brs.get('https://twitter.com', sleep=5)
                    #for cookie in out['c']:
                    #    self.brs.set_cookie(cookie)
                    self.graphql = out['g']
                    self.headers = out['h']
                    self.headers['cookie'] = '; '.join([f'{c["name"]}={c["value"]}' for c in out['c']])
                    #self.headers['cookie'] = '; '.join([f'{c["name"]}={c["value"]}' for c in self.brs.get_info('cookies')])
                    #self.brs.get('https://twitter.com')
                    return
        
        if self.brs is None:
            self.brs = Browser(self.bname, self.kwargs)
        
        self.brs.get('https://twitter.com/i/flow/login')
        self.brs.send('input[autocomplete="username"]', email)
        self.brs.click('#layers > div > div > div > div > div > div > div.css-1dbjc4n.r-1awozwy.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv > div.css-1dbjc4n.r-1867qdf.r-1wbh5a2.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1.r-htvplk.r-1udh08x > div > div > div.css-1dbjc4n.r-14lw9ot.r-6koalj.r-16y2uox.r-1wbh5a2 > div.css-1dbjc4n.r-16y2uox.r-1wbh5a2.r-1jgb5lz.r-1ye8kvj.r-13qz1uu > div.css-1dbjc4n.r-16y2uox.r-1wbh5a2.r-1dqxon3 > div > div > div:nth-child(6) > div > span > span',
                       sleep=2)

        if self.brs.wait('input[data-testid="ocfEnterTextTextInput"]', timeout=3):
            self.brs.send('input[data-testid="ocfEnterTextTextInput"]', username)
            self.brs.click('.r-1m3jxhj > div:nth-child(1)',
                           sleep=2)
        
        self.brs.send('input[name="password"]', password)
        self.brs.click('span.css-bfa6kz:nth-child(1) > span:nth-child(1)',
                       sleep=2)
        
        self.brs.get(f'https://twitter.com/{username}', sleep=2)
        while self.graphql['userinfo'] is None:
            try:
                for log in self.brs.get_xhr(reset=True):
                    if 'UserByScreenName' in log['req.url']:
                        self.headers = {k.lower():v for k,v in log['req.headers'].items()}
                        tmp = log['req.url'].split('graphql/')[1]
                        print(tmp)
                        self.graphql['userinfo'] = tmp.split('/UserByScreenName')[0]
                        break
            except KeyError:
                
                print('keyerror')
                
                time.sleep(5)
                continue

        self.brs.get(f'https://twitter.com/{username}/followers', sleep=2)
        while self.graphql['followers'] is None:
            try:
                for log in self.brs.get_xhr(reset=True):
                    if 'Followers' in log['req.url']:
                        tmp = log['req.url'].split('graphql/')[1]
                        self.graphql['followers'] = tmp.split('/Followers')[0]
                        break
            except KeyError:
                
                print('keyerror')
                
                time.sleep(5)
                continue
        
        os.makedirs(self.out, exist_ok=True)
        with open(f'{self.out}/{SESSION}', 'w') as f:
            out = {'t':int(time.time()), 'c':self.brs.get_info('cookies'), 'h':self.headers, 'g':self.graphql}
            f.write(json.dumps(out))
            f.flush()


    def user_info(self, uname):
        url = f'https://twitter.com/i/api/graphql/{self.graphql["userinfo"]}/UserByScreenName'
        params = {
            'variables': {
                    'screen_name':uname,
                    'withSafetyModeUserFields':True,
                    'withSuperFollowsUserFields':True
                }
            }
        params['variables'] = json.dumps(params['variables'])
        
        c = 0
        while True:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                data = json.loads(response.text)
                if not data['data']:
                    c += 1
                    if c > 3:
                        return {}
                    else:
                        time.sleep(5)
                        continue
                    
                data = data['data']['user']['result']
                return {
                    'uid': int(data['rest_id']),
                    'uname': str(data['legacy']['screen_name']),
                    'cdate': Twitter.tostamp(data['legacy']['created_at']),
                    'fng': int(data['legacy']['friends_count']),
                    'fws': int(data['legacy']['followers_count']),
                    'twt': int(data['legacy']['statuses_count']),
                    'img': 0 if 'default' in data['legacy']['profile_image_url_https'] else 1,
                    'nam': str(data['legacy']['name']),
                    'dsc': str(data['legacy']['description']),
                    'loc': str(data['legacy']['location']),
                    'pro': data['legacy']['protected']
                }
            except KeyError:
                time.sleep(5)
                continue


    def crawl_followers(self, uname, crs='-1', verbose=True, res=3600, out=None):
        
        if out is None:
            out = f'fwers_{uname}'
        
        with open(f'{self.out}/{out}', 'a+') as f:

            ui = self.user_info(uname)
            if not ui or ui['pro']:
                return True
            
            f.write(f'u\t{int(time.time())}\t{ui["uid"]}\t{ui["uname"]}\t{ui["cdate"]}')
            f.write(f'\t{ui["fng"]}\t{ui["fws"]}\t{ui["twt"]}\t{ui["img"]}')
            f.write(f'\t{quote_plus(ui["nam"])}\n')
            #f.write(f'\t{quote_plus(ui["dsc"])}\t{quote_plus(ui["loc"])}\n')
            

            url = f'https://twitter.com/i/api/graphql/{self.graphql["followers"]}/Followers'
            xratelim = None
            variables ={
                'userId':ui['uid'], 'count':100, 'cursor':crs,
                'includePromotedContent':False, 'withSuperFollowsUserFields':True,
                'withDownvotePerspective':False, 'withReactionsMetadata':False,
                'withReactionsPerspective':False, 'withSuperFollowsTweetFields': True,
                '__fs_dont_mention_me_view_api_enabled':True, '__fs_interactive_text_enabled':True,
                '__fs_responsive_web_uc_gql_enabled':False
            }
            
            
            while True:
                try:
                    current_time = int(round(time.time()))
                    response = requests.get(url, headers=self.headers, params=(('variables', json.dumps(variables)),))
                except BaseException as e:
                    print(e, variables['cursor'])
                    time.sleep(60)
                    continue
                
                try:
                    data = json.loads(response.text)
                    data = data['data']['user']['result']['timeline']['timeline']['instructions'][-1]['entries']
                    users, btm = [], None
                    for e in data:
                        if 'user' in e['entryId']:
                            users.append(e['content']['itemContent']['user_results']['result'])
                        elif 'cursor-bottom' in e['entryId']:
                            btm = e['content']['value']
                    idx = len(users) - variables['count'] 
                    if idx > 0:
                        users = users[idx:]
                except (KeyError, json.decoder.JSONDecodeError):
                    print(e, variables['cursor'])
                    time.sleep(60)
                    continue
                
                
                prv = int(variables['cursor'].split('|')[0])
                nxt = int(btm.split('|')[0])
                prv = current_time if prv < 0 else int(Twitter.crs2stamp(prv))
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
                
                for e in users:
                    try:
                        f.write(f'f\t{e["rest_id"]}\t{e["legacy"]["screen_name"]}\t')
                        f.write(f'{Twitter.tostamp(e["legacy"]["created_at"])}\t')
                        f.write(f'{e["legacy"]["friends_count"]}\t{e["legacy"]["followers_count"]}\t')
                        f.write(f'{e["legacy"]["statuses_count"]}\t')
                        img = 0 if 'default' in e['legacy']['profile_image_url_https'] else 1
                        f.write(f'{img}\t')
                        f.write(f'{quote_plus(e["legacy"]["name"])}\n')
                        #f.write(f'{quote_plus(e["legacy"]["description"])}\t')
                        #f.write(f'{quote_plus(e["legacy"]["location"])}\n')
                    except KeyError:
                        pass
                
                variables['cursor'] = btm
                try:
                    xratelim = int(response.headers['x-rate-limit-remaining'])
                except KeyError:
                    if xratelim is None:
                        xratelim = 15
                    else:
                        xratelim -= 1
                s = f'{uname} {len(users)} {variables["cursor"]}\n{stamp2str(prv)} - {stamp2str(nxt)} - {xratelim}'
                with open(f'{self.out}/status', 'w') as g:
                    g.write(s)
                if verbose:
                    print(s)
                
                if nxt > ui['cdate']:
                    if xratelim < 15:
                        time.sleep(60 * (15 - xratelim))
                    else:
                        time.sleep(1)
                else:
                    return True
