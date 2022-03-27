import time
import json
from collections import deque
from urllib.parse import quote_plus
from vlib.automation.web.Browser import Browser
from vlib.utils.JSONBox import JSONBox


class Redbubble:
    

    def __init__(self, browser, **kwargs):
        self.bname = browser
        self.out = '.'
        if 'out_folder' in kwargs:
            self.out = kwargs['out_folder']
        self.brs = Browser(self.bname, **kwargs)
    
    
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
        with open(f'{self.out}/rb_search_{base}', 'w') as f:
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
                            time.sleep(60)
                            continue
                            
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


    def get_search_info(self, tag):
        url = f'https://www.redbubble.com/shop/?query={quote_plus(tag)}&ref=search_box'
        self.brs.get(url)
        count = self.brs.get_text('div.styles__paddingLeft-xs--oc_Ov:nth-child(2) > span:nth-child(1)')
        rel = self.brs.get_text('.styles__carouselContainer--3_gKC > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)')
        count = count.split(' ')[0]
        rel = [] if rel is None else rel.strip().split('\n')
        return int(count.replace(',','')), [x.lower() for x in rel] 
        
        #data = []
        #try:
        #    for log in self.brs.get_xhr(reset=False):
        #        if 'graphql' in log['req.url']:
        #            req = json.loads(log['req.body'])
        #            print(req)
        #            if 'Search' in req['operationName']:
        #                data = json.loads(log['res.body'])
        #                break
        #    data = data['data']['searchResults']['metadata']
        #except (KeyError, TypeError):
        #    return None        
        #return [data['resultCount'], [x['title'] for x in data['relatedTopics']]]


    def batch_get_search_info(self, lst):
        base = int(time.time())
        with open(f'{self.out}/rb_info_{base}', 'w') as f:
            f.write(f'b\t{base}\n')
            for tag in lst:
                print(tag)
                count, rel = self.get_search_info(tag)
                f.write(f'{tag}\t{count}\t{",".join(rel)}\t{int(time.time()) - base}\n')
                f.flush()
                
        
