import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
import csv

def contentReq(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
    # 2. 写到请求页面的header里面去
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8')
    #  3. 打开网页， 获取内容
    soup = BeautifulSoup(html, "html.parser")
    item=soup.select('#JIATHIS_CODE_HTML4')
    #print(item)
    cont=item[0].select('td')[0].text
    return cont


def information(url):
    try:
        url = url
        header = {"User-Agent": "Mozilla5.0 (Windows NT 6.1; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0"}
        request = urllib.request.Request(url, headers=header)
        response = urllib.request.urlopen(request, timeout=1)  # timeout设置超时的时间,防止出现访问超时问题
        # 取出json文件里的内容，返回的格式是字符串
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")

        for item0 in soup.select('.common'):
            kind = item0.select('a')[2].text
            infor = item0.select('a')[3]
            name = infor.text
            contenturl = infor['href']
            content = contentReq('http://www.12345.suzhou.gov.cn/bbs/' + contenturl)
            f2.write(kind + ' ' + name + ' ' + content + '\n')
    except Exception as e:  # 抛出超时异常
        print('a', str(e))





f2 = open('complaint.txt','a+',encoding='utf-8')

for i in range(1,190):
    url = 'http://www.12345.suzhou.gov.cn/bbs/forum.php?mod=forumdisplay&fid=2&locationid=4&orderby=lastpost&ascdesc=DESC&page=189&page='+str(i)
    information(url)
f2.close()
#print (count)