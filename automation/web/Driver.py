import os, time
from seleniumwire import webdriver as wwebdrv
from seleniumwire.utils import decode
from selenium import webdriver as webdrv
from selenium.webdriver.support.ui import WebDriverWait as DW
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By as BY
from selenium.common.exceptions import TimeoutException
from tkinter import Tk


class Driver:
    
    
    def __init__(self, browser, **kwargs):
        
        _drv = None
        _mod = None
        
        if browser == 'chrome':
            _drv = wwebdrv.Chrome
            _mod = webdrv.chrome
        elif browser == 'firefox':
            _drv = wwebdrv.Firefox
            _mod = webdrv.firefox
        else:
            raise RuntimeError('browser not supported.')
        
        service = None
        if 'driver' in kwargs:
            os.chmod(kwargs['driver'], 0o755)
            service = _mod.service.Service(executable_path=kwargs['driver'])
        
        options = _mod.options.Options()
        if 'binary' in kwargs:
            os.chmod(kwargs['binary'], 0o755)
            options.binary_location = kwargs['binary']
        if 'headless' in kwargs:
            options.headless = kwargs['headless']
            
        self.drv = _drv(options=options, service=service)
        
        tk = Tk()
        self.drv.set_window_size(tk.winfo_screenwidth(), tk.winfo_screenheight())
        self.drv.set_page_load_timeout(30)
        if 'timeout' in kwargs:
            self.drv.set_page_load_timeout(kwargs['timeout'])


    def __del__(self):
        try:
            self.drv.close()
        except:
            pass


    def _get(self, url, repeat=False, sleep=0):
        if repeat:
            while True:
                try:
                    self.drv.get(url)
                    break
                except TimeoutException:
                    time.sleep(60)
                    continue
        else:
            try:
                self.drv.get(url)
            except TimeoutException:
                return False
        if sleep > 0:
            time.sleep(sleep)
        return True


    def _css(self, selector, timeout=30, parent=None):
        if not parent:
            parent = self.drv
        try:
            return DW(parent, timeout).until(EC.presence_of_element_located(
                (BY.CSS_SELECTOR, selector)))
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


    def _xhr(self, reset=False):
        out = []
        for r in self.drv.requests:
            tmp = {
                'req.url':r.url,
                'req.headers':r.headers,
                'req.body': decode(r.body, r.headers.get('Content-Encoding', 'identity')),
                'res.headers':None,
                'res.body':None
            }
            r = r.response
            if r is not None:
                tmp['res.headers'] = r.headers
                tmp['res.body'] = decode(r.body, r.headers.get('Content-Encoding', 'identity'))
            out.append(tmp)
        if reset:
            del self.drv.requests
        return out
