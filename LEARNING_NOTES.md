"""
学习笔记和参考资源
"""

# ==========================================
# 爬虫基础知识
# ==========================================

## HTTP 请求方法

- **GET**: 获取资源，参数在 URL 中，幂等的
- **POST**: 提交数据，参数在请求体中，不幂等

## 常见 HTTP 状态码

| 状态码 | 含义 |
|------|------|
| 200 | OK - 请求成功 |
| 301 | 永久重定向 |
| 302 | 临时重定向 |
| 400 | Bad Request - 请求错误 |
| 403 | Forbidden - 禁止访问 |
| 404 | Not Found - 资源不存在 |
| 429 | Too Many Requests - 请求过于频繁 |
| 500 | 服务器错误 |
| 503 | 服务不可用 |

## 常见请求头

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Accept': 'text/html,application/xhtml+xml,...',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'https://example.com',
    'Cookie': 'session_id=xxx',
}
```

# ==========================================
# BeautifulSoup 选择器语法
# ==========================================

## CSS 选择器

```python
soup = BeautifulSoup(html, 'html.parser')

# 按标签
soup.select('div')

# 按 ID
soup.select('#myid')

# 按 class
soup.select('.myclass')

# 组合
soup.select('div.item > a.link')

# 属性选择
soup.select('a[href*="example"]')

# 伪类
soup.select('div:first-child')
soup.select('li:nth-child(3n)')
```

## 提取数据

```python
# 获取文本
text = element.get_text(strip=True)

# 获取属性
attr = element.get('href')
attr = element['data-id']

# 获取 HTML
html = element.prettify()

# 获取父元素
parent = element.parent

# 获取兄弟元素
next_sibling = element.next_sibling
prev_sibling = element.previous_sibling

# 获取子元素
children = element.children
```

# ==========================================
# Selenium 基础用法
# ==========================================

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 创建驱动
driver = webdriver.Chrome()

# 打开网页
driver.get('https://example.com')

# 等待元素出现（最多10秒）
wait = WebDriverWait(driver, 10)
element = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.item'))
)

# 查找元素
element = driver.find_element(By.CSS_SELECTOR, '.item')
elements = driver.find_elements(By.TAG_NAME, 'a')

# 交互
element.click()
element.send_keys('text')
element.clear()

# 执行 JavaScript
result = driver.execute_script('return document.title')

# 关闭
driver.quit()
```

# ==========================================
# Playwright 基础用法
# ==========================================

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 打开网页
    page.goto('https://example.com')
    
    # 等待元素
    page.wait_for_selector('.item')
    
    # 查找元素
    element = page.query_selector('.item')
    elements = page.query_selector_all('.items')
    
    # 获取属性
    text = page.text_content('.title')
    href = page.get_attribute('a', 'href')
    
    # 交互
    page.click('.button')
    page.fill('input', 'text')
    
    # 获取内容
    content = page.content()
    
    # 关闭
    browser.close()
```

# ==========================================
# 调试技巧
# ==========================================

## 1. 打印 HTML 结构

```python
from bs4 import BeautifulSoup

html = """..."""
soup = BeautifulSoup(html, 'html.parser')

# 美化输出
print(soup.prettify())

# 保存到文件
with open('debug.html', 'w') as f:
    f.write(soup.prettify())
```

## 2. 验证选择器

```python
# 在浏览器控制台验证
document.querySelectorAll('.item').length

# 或在爬虫中验证
elements = soup.select('.item')
print(f'找到 {len(elements)} 个元素')
```

## 3. 查看网络请求

在浏览器开发者工具中：
1. F12 打开开发者工具
2. 切换到 Network 标签
3. 刷新页面
4. 查看请求列表、状态码、响应内容

## 4. 模拟浏览器行为

```python
# 添加延迟
import time
time.sleep(2)

# 滚动页面
driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

# 移动鼠标
from selenium.webdriver.common.action_chains import ActionChains
ActionChains(driver).move_to_element(element).perform()
```

# ==========================================
# 常见问题解决方案
# ==========================================

## 问题 1: 403 Forbidden

**原因**: 服务器认为请求是爬虫

**解决方案**:
```python
headers = {
    'User-Agent': '浏览器 User-Agent',
    'Referer': '来源页面',
}
```

## 问题 2: 超时

**原因**: 网络慢或服务器响应慢

**解决方案**:
```python
requests.get(url, timeout=30)
page.goto(url, wait_until='networkidle', timeout=30000)
```

## 问题 3: 元素找不到

**原因**: 选择器错误或元素还没加载

**解决方案**:
```python
# 等待元素加载
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.item')))

# 或使用 Playwright
page.wait_for_selector('.item')
```

## 问题 4: 动态加载内容为空

**原因**: 内容通过 JavaScript 动态加载

**解决方案**:
```python
# 使用 Selenium 或 Playwright
html = spider.get_with_js(url, wait_selector='.item')
```

# ==========================================
# 性能优化建议
# ==========================================

1. **使用连接池**: 复用 HTTP 连接
2. **设置超时**: 避免长时间等待
3. **增量更新**: 只爬取新增数据
4. **数据去重**: 使用 Set 或数据库唯一约束
5. **缓存结果**: 避免重复爬取
6. **多线程**: 并发爬取多个页面

# ==========================================
# 爬虫礼仪
# ==========================================

1. **检查 robots.txt**
   ```
   https://example.com/robots.txt
   ```

2. **合理延迟**
   ```python
   time.sleep(random.uniform(1, 3))
   ```

3. **识别自己**
   ```python
   User-Agent: MySpider/1.0
   ```

4. **尊重 Crawl-Delay**
   ```
   Crawl-Delay: 2
   ```

5. **不爬取个人数据**

6. **不对服务器造成压力**

---

祝您学习顺利！
"""
