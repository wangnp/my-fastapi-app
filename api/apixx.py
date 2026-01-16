import json
import os
import requests
import utils
import base64
from googleapiclient.discovery import build
from config import google_api_key, google_cse_id, feisoo_headers, google_headers
from lxml import etree
from Crypto.Cipher import AES


# 设置默认全局代理
proxies = utils.get_system_proxy()
if proxies.get("http"):
    os.environ['HTTP_PROXY'] = proxies.get("http")
if proxies.get("https"):
    os.environ['HTTPS_PROXY'] = proxies.get("https")


# 初始化session
session = requests.session()
session.headers = google_headers
# session.get("https://www.google.com")


# ------------------谷歌官方API搜索----------------------"""
def google_search(keyword, page=1, pageNum=10):
    """
    谷歌官方API搜索
    @param keyword: 搜索关键词
    @param page: 页码
    @param pageNum: 页面大小
    @return:
    """
    start = (page - 1) * pageNum + 1
    service = build("customsearch", "v1", developerKey=google_api_key)
    # num=10 是单次请求最大允许返回的条数
    res = service.cse().list(q=keyword, cx=google_cse_id, num=pageNum, start=start).execute()
    items = res.get('items', [])

    print(res)

    result = []
    for item in items:
        result.append({
            "url": item["link"],
            "title": item["title"],
            "snippet": item["snippet"],
            "htmlTitle": item["htmlTitle"],
            "htmlSnippet": item["htmlSnippet"]
        })
    return result


# ------------------谷歌爬虫----------------------
def search(keyword, page=1, pageNum=10, domain="feishu.cn"):
    """
    谷歌搜索（爬虫搜索结果）
    @param keyword: 关键词
    @param page: 当前页
    @param pageNum: 页面大小
    @param domain: 域名
    @return:
    """
    search_result = []

    # 计算开始条数
    start = (page - 1) * pageNum + 1
    url = "https://www.google.com/search"
    params = {
        "q": f"{keyword} site:{domain}",
        "start": start
    }
    response = session.get(url, params=params)
    html_content = response.text

    # 解析页面
    tree = etree.HTML(html_content)
    divs = tree.xpath('//div[@class="MjjYud"]')
    for div in divs:
        title = div.xpath(".//h3/text()")
        if title:
            title = title[0]
            html_title = title.replace(keyword, f"<b>{keyword}</b>")
            url = div.xpath(".//a/@href")[0]
            snippet_span = div.xpath('.//div/div/div/div[2]/div//text()')
            snippet = "".join(snippet_span)
            htmlSnippet = snippet.replace(keyword, f"<b>{keyword}</b>")
            # htmlSnippet = etree.tostring(snippet_span, encoding='unicode', method='html').strip()

            # print(f"[标题] {title}")
            # print(f"[html_title] {html_title}")
            # print(f"[链接] {url}")
            # print(f"[摘要] {snippet}")
            # print(f"[html摘要] {htmlSnippet}")
            # print("-" * 20)
            search_result.append({
                "url": url,
                "title": title,
                "snippet": snippet,
                "htmlTitle": html_title,
                "htmlSnippet": htmlSnippet
            })
    return search_result


# ------------------飞搜侠----------------------
class AesUtils:
    def __init__(self):
        self.key = "aaDJL2d9DfhLZO0z".encode('utf-8')
        self.iv = "412ADDSSFA342442".encode('utf-8')
        self.block_size = 16

    def _pad(self, text):
        """实现 ZeroPadding: 填充 \0 直到满足 block_size"""
        padding_len = self.block_size - (len(text.encode('utf-8')) % self.block_size)
        if padding_len == self.block_size:
            return text.encode('utf-8')
        return text.encode('utf-8') + (b'\0' * padding_len)

    def _unpad(self, b_text):
        """移除 ZeroPadding"""
        return b_text.rstrip(b'\0')

    def encrypt(self, text):
        """对应 JS 中的 zx 函数"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded_data = self._pad(text)
        encrypted_bytes = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def decrypt(self, encoded_text):
        """对应 JS 中的 qx 函数"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 将 base64 字符串转回字节
        encrypted_bytes = base64.b64decode(encoded_text)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        # 解码并去除末尾的填充字符
        return self._unpad(decrypted_bytes).decode('utf-8')


aesUtils = AesUtils()


def feishu_search(keyword: str, page: int):
    """
    飞搜侠API
    @param keyword: 关键词
    @param page: 页码
    @return:
    """
    # 发起请求
    data = {
        "keyword": keyword,
        "pageNum": page
    }
    data_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    encrypt_data = aesUtils.encrypt(data_str)
    url = "https://www.feisoo.com/prod-api/source/search/feishuQuery"
    response = requests.post(url, headers=feisoo_headers, data=encrypt_data)
    # print(f"返回结果：{response.text}")
    result = response.text

    # 解密数据
    decrypt_text = aesUtils.decrypt(result)
    # print(f"解密结果：{decrypt_text}")
    decrypt_text = json.loads(decrypt_text)

    items = decrypt_text['data']
    result = []
    for item in items:
        title = item["title"]
        description = item["description"]
        html_title = title.replace(keyword, f"<b>{keyword}</b>")
        htmlSnippet = description.replace(keyword, f"<b>{keyword}</b>")
        result.append({
            "url": item["url"],
            "title": title,
            "snippet": description,
            "htmlTitle": html_title,
            "htmlSnippet": htmlSnippet
        })
    return result


if __name__ == '__main__':
    # 谷歌官方
    results = google_search("数据分析师", page=1)
    print(results)

    # 谷歌爬虫
    # results = search("数据分析师", page=3, pageNum=10, domain="feishu.cn")
    # print(results)

    # 飞搜侠
    # results = feishu_search("数据分析师", 1)
    # print(results)
