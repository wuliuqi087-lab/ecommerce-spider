"""
基础爬虫类 - 所有爬虫的父类
"""
import requests
import logging
import time
import random
from typing import Dict, List, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from config import SPIDER_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BaseSpider:
    """基础爬虫类"""
    
    def __init__(self, name: str = 'BaseSpider'):
        self.name = name
        self.session = self._create_session()
        self.headers = SPIDER_CONFIG['headers']
        self.timeout = SPIDER_CONFIG['timeout']
        self.retry_count = SPIDER_CONFIG['retry_count']
        
    def _create_session(self) -> requests.Session:
        """
        创建带重试机制的 Session
        
        Returns:
            requests.Session: 配置好的会话对象
        """
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.retry_count,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=['GET', 'POST'],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        return session
    
    def _random_delay(self):
        """随机延迟，模拟真人行为"""
        delay = random.uniform(
            SPIDER_CONFIG['min_delay'],
            SPIDER_CONFIG['max_delay']
        )
        time.sleep(delay)
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        发送 GET 请求
        
        Args:
            url: 请求 URL
            **kwargs: 其他请求参数
            
        Returns:
            响应对象或 None
        """
        try:
            self._random_delay()
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            logger.info(f'✓ GET {url} - Status: {response.status_code}')
            return response
        except requests.RequestException as e:
            logger.error(f'✗ GET {url} failed: {e}')
            return None
    
    def post(self, url: str, data: Dict = None, **kwargs) -> Optional[requests.Response]:
        """
        发送 POST 请求
        
        Args:
            url: 请求 URL
            data: 请求数据
            **kwargs: 其他请求参数
            
        Returns:
            响应对象或 None
        """
        try:
            self._random_delay()
            response = self.session.post(
                url,
                headers=self.headers,
                data=data,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            logger.info(f'✓ POST {url} - Status: {response.status_code}')
            return response
        except requests.RequestException as e:
            logger.error(f'✗ POST {url} failed: {e}')
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        解析 HTML
        
        Args:
            html: HTML 内容
            
        Returns:
            BeautifulSoup 对象
        """
        return BeautifulSoup(html, 'html.parser')
    
    def extract_text(self, element, selector: str, default: str = '') -> str:
        """
        从元素中提取文本
        
        Args:
            element: BeautifulSoup 元素
            selector: CSS 选择器
            default: 默认值
            
        Returns:
            提取的文本
        """
        try:
            result = element.select_one(selector)
            return result.get_text(strip=True) if result else default
        except Exception as e:
            logger.debug(f'Extract text error: {e}')
            return default
    
    def extract_attr(self, element, selector: str, attr: str, default: str = '') -> str:
        """
        从元素中提取属性
        
        Args:
            element: BeautifulSoup 元素
            selector: CSS 选择器
            attr: 属性名
            default: 默认值
            
        Returns:
            提取的属性值
        """
        try:
            result = element.select_one(selector)
            return result.get(attr, default) if result else default
        except Exception as e:
            logger.debug(f'Extract attribute error: {e}')
            return default
    
    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info(f'{self.name} session closed')


class DynamicSpider(BaseSpider):
    """动态爬虫类 - 用于处理 JavaScript 渲染的页面"""
    
    def __init__(self, name: str = 'DynamicSpider', use_playwright: bool = True):
        """
        初始化动态爬虫
        
        Args:
            name: 爬虫名称
            use_playwright: 是否使用 Playwright（True）或 Selenium（False）
        """
        super().__init__(name)
        self.use_playwright = use_playwright
        self.driver = None
        
    def _init_playwright(self):
        """初始化 Playwright"""
        try:
            from playwright.sync_api import sync_playwright
            from config import PLAYWRIGHT_CONFIG
            
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=PLAYWRIGHT_CONFIG['headless']
            )
            logger.info('Playwright initialized')
        except ImportError:
            logger.error('Playwright not installed. Run: pip install playwright')
            raise
    
    def _init_selenium(self):
        """初始化 Selenium"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from config import SELENIUM_CONFIG
            
            chrome_options = Options()
            if SELENIUM_CONFIG['headless']:
                chrome_options.add_argument('--headless')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info('Selenium initialized')
        except ImportError:
            logger.error('Selenium not installed. Run: pip install selenium')
            raise
    
    def get_with_js(self, url: str, wait_selector: str = None) -> Optional[str]:
        """
        获取渲染后的页面内容
        
        Args:
            url: 页面 URL
            wait_selector: 等待加载的选择器
            
        Returns:
            页面 HTML 或 None
        """
        if self.use_playwright:
            return self._get_with_playwright(url, wait_selector)
        else:
            return self._get_with_selenium(url, wait_selector)
    
    def _get_with_playwright(self, url: str, wait_selector: str = None) -> Optional[str]:
        """使用 Playwright 获取页面"""
        try:
            if not self.browser:
                self._init_playwright()
            
            page = self.browser.new_page()
            page.goto(url, wait_until='networkidle')
            
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=10000)
            
            content = page.content()
            page.close()
            logger.info(f'✓ Playwright: {url}')
            return content
        except Exception as e:
            logger.error(f'✗ Playwright error: {e}')
            return None
    
    def _get_with_selenium(self, url: str, wait_selector: str = None) -> Optional[str]:
        """使用 Selenium 获取页面"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from config import SELENIUM_CONFIG
            
            if not self.driver:
                self._init_selenium()
            
            self.driver.get(url)
            
            if wait_selector:
                wait = WebDriverWait(self.driver, SELENIUM_CONFIG['timeout'])
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
            
            content = self.driver.page_source
            logger.info(f'✓ Selenium: {url}')
            return content
        except Exception as e:
            logger.error(f'✗ Selenium error: {e}')
            return None
    
    def close(self):
        """关闭浏览器和会话"""
        if self.use_playwright and self.browser:
            self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
        elif self.driver:
            self.driver.quit()
        
        super().close()
