import json, time
from vlib.automation.web.Driver import Driver



class Browser(Driver):


    def __init__(self, browser, **kwargs):
        super().__init__(browser, **kwargs)

        
    def get(self, url, repeat=False, sleep=0):
        return super()._get(url, repeat, sleep)


    def scroll(self, until=-1, speed=25):
        max_scroll = self._exe(
                'return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight,'
                  'document.body.offsetHeight, document.documentElement.offsetHeight,'
                  'document.body.clientHeight, document.documentElement.clientHeight);'
              )
        if until < max_scroll:
            if until < 0:
                until = max_scroll
            pp = super()._exe('return window.pageYOffset')
            while pp < until:
                super()._exe(f'window.scrollBy(0, {speed});')
                np = super()._exe('return window.pageYOffset')
                if np > pp:
                    pp = np
                    time.sleep(0.1)
                else:
                    break


    def wait(self, selector, timeout=-1):
        if timeout < 0:
            while True:
                e = super()._css(selector)
                if e:
                    return e
        else:
            return super()._css(selector, timeout=timeout)


    def send(self, selector, keys, clear=False, sleep=0):
        e = super()._css(selector)
        if not e:
            return False
        if clear:
            e.clear()
        e.send_keys(keys)
        if sleep > 0:
            time.sleep(sleep)
        return True
    
    
    def click(self, selector, sleep=0):
        e = super()._css(selector)
        if not e:
            return False
        e.click()
        if sleep > 0:
            time.sleep(sleep)
        return True
    
    
    def get_text(self, selector):
        e = super()._css(selector, timeout=1)
        if not e:
            return None
        return e.text


    def get_xhr(self, reset=False):
        return super()._xhr(reset)


    def set_cookie(self, cookie_dct):
        self.drv.add_cookie(cookie_dct)

    def get_info(self, name):
        if name == 'ua':
            return self._exe('return navigator.userAgent')
        elif name == 'cookies':
            return self.drv.get_cookies()
        return None
