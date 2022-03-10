import os, json, selenium, time
from selenium.webdriver.support.ui import WebDriverWait as DW
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By as BY
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import DesiredCapabilities


class Browser:


    def __init__(self, drv_path=None, **kwargs):

        cap = DesiredCapabilities.CHROME
        cap['goog:loggingPrefs'] = {"performance": "ALL"}

        opt = selenium.webdriver.ChromeOptions()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_experimental_option(
            'prefs', {
                'profile.default_content_setting_values.notifications': 2
                }
        )

        if 'proxy' in kwargs:
            opt.add_argument(f'--proxy-server={kwargs["proxy"]}')
            opt.add_argument('--ignore-ssl-errors=yes')
            opt.add_argument('--ignore-certificate-errors')
            opt.add_argument('--disable-web-security')

        if 'headless' in kwargs and kwargs['headless'] == True:
            opt.add_argument("--headless")
        
        if drv_path is None:
            self.drv = selenium.webdriver.Chrome(
                options=opt, desired_capabilities=cap)
        else:
            try:
                os.chmod(drv_path, 0o755)    
            except FileNotFoundError:
                raise FileNotFoundError('PATH not pointing to driver location')
            self.drv = selenium.webdriver.Chrome(
                drv_path, options=opt, desired_capabilities=cap)

        if 'timeout' in kwargs:
            self.drv.set_page_load_timeout(kwargs['timeout'])
        else:
            self.drv.set_page_load_timeout(30)


    def __del__(self):
        self.drv.close()


    def _css(self, selector, timeout=30, parent=None):
        if not parent:
            parent = self.drv
        try:
            return DW(parent, timeout).until(
                    EC.presence_of_element_located(
                        (BY.CSS_SELECTOR, selector)
                ))
        except TimeoutException:
            return None


    def _css_all(self, selector, timeout=30, parent=None):
        if not parent:
            parent = self.drv
        for dummy in range(int(timeout / 0.1)):
            res = parent.find_elements_by_css_selector(selector)
            if res:
                return res
        return []


    def _exe(self, script, node=None):
        if node:
            return self.drv.execute_script(script, node)
        return self.drv.execute_script(script)


    def get(self, url, sleep=0):
        try:
            self.drv.get(url)
        except TimeoutException:
            raise RuntimeError('Timeout loading webpage')
        if sleep > 0:
            time.sleep(sleep)


    def scroll(self, until=-1, speed=25):
        max_scroll = self._exe(
                'return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight,'
                  'document.body.offsetHeight, document.documentElement.offsetHeight,'
                  'document.body.clientHeight, document.documentElement.clientHeight);'
              )
        if until < max_scroll:
            if until < 0:
                until = max_scroll
            pp = self._exe('return window.pageYOffset')
            while pp < until:
                self._exe(f'window.scrollBy(0, {speed});')
                np = self._exe('return window.pageYOffset')
                if np > pp:
                    pp = np
                    time.sleep(0.1)
                else:
                    break

    def wait(self, selector, timeout=-1):
        if timeout < 0:
            while True:
                e = self._css(selector)
                if e:
                    return e
        else:
            return self._css(selector, timeout=timeout)


    def send(self, selector, keys, clear=False, sleep=0):
        e = self._css(selector)
        if not e:
            raise RuntimeError('Selector not found.')
        if clear:
            e.clear()
        e.send_keys(keys)
        if sleep > 0:
            time.sleep(sleep)
    
    
    def click(self, selector, sleep=0):
        e = self._css(selector)
        if not e:
            raise RuntimeError('Selector not found.')
        e.click()
        if sleep > 0:
            time.sleep(sleep)
    
    
    def get_text(self, selector):
        e = self._css(selector)
        if not e:
            return None
        return e.text


    def get_xhr(self, **kwargs):
        out = []
        for m in self.drv.get_log('performance'):
            m = json.loads(m['message'])['message']
            if 'type' in m['params'] and m['params']['type'] == 'XHR':
                rid, r = m['params']['requestId'], None
                try:    
                    if m['method'] == 'Network.requestWillBeSent':
                        r = self.drv.execute_cdp_cmd('Network.getRequestPostData',{'requestId': rid})
                    elif m['method'] == 'Network.responseReceived':
                        r = self.drv.execute_cdp_cmd('Network.getResponseBody',{'requestId': rid})
                except WebDriverException:
                    pass
                out.append((m,r))
        return out


    def get_info(self, name):
        if name == 'ua':
            return self._exe('return navigator.userAgent')
        elif name == 'cookies':
            return self.drv.get_cookies()
        return None


    def set_cookie(self, cookie_dct):
        self.drv.add_cookie(cookie_dct)