import time
from collections import deque
from urllib.parse import quote_plus
from vlib.automation.web.Browser import Browser
from vlib.utils.JSONBox import JSONBox


class Redbubble:
    

    def __init__(self, drv_path, out_path):
        self.out = out_path
        self.drv = drv_path
        self.brs = Browser(self.drv, headless=True)
    
    
    def search_results(self, key):
        url = f'https://www.redbubble.com/typeahead/?term={quote_plus(key)}'
        self.brs.get(url)
        j, out = JSONBox(self.brs.get_text('pre')), []
        data = j['completions']
        if data:
            out.extend([('c',x.lower()) for x in data])
        data = j['data.popular_searches']
        if data:
            out.extend([('p',x['label'].lower()) for x in data])
        data = j['data.trending_searches']
        if data:
            out.extend([('t',x['label'].lower()) for x in data])
        data = j['data.artists']
        if data:
            out.extend([('a',x['artist_id'],x['artist_name'],x['artist_works']) for x in data])
        data = j['data.fan_art_properties']
        if data:
            out.extend([('f',x['agreement_id'],x['label']) for x in data])
        return out


    def batch_search(self, itr):
        base = int(time.time())
        with open(f'{self.out}/log', 'a') as f:
            f.write(f'b\t{base}\n')
            out = deque(['_'])
            cache = set()
            while out:
                term = out.popleft()
                flag = False
                if len(term) > 1:
                    lst = []
                    while True:
                        try:
                            lst = self.search_results(term[1:])
                            break
                        except Exception as e:
                            print(e)
                            del self.brs
                            time.sleep(60)
                            self.brs = Browser(self.drv, headless=True)
                    for e in [tuple(x) for x in lst]:
                        if not e in cache:
                            flag = True
                            cache.add(e)
                            f.write('\t'.join([str(x) for x in e]))
                            f.write(f'\t{int(time.time()) - base}\n')
                    f.flush()
                if flag or len(term) == 1:
                    out.extend([term+c for c in itr])
                print(f'{term} {len(out)}')
   