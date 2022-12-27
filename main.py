
#网站把视频进行转码(不同清晰度)做切片(ts)处理.
#有可能要加解密
#
import requests
from urllib import parse
from lxml import etree
import re
import aiohttp
import aiofiles
import asyncio
import os



def get_page_source(url):
    headers = {
        "origin":"https://www.wbdyba.com",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46"
    }
    
    return requests.get(url=url,headers=headers).text
    pass


def get_iframe_url(url,page_sourse):
    tree = etree.HTML(page_sourse)
    src = tree.xpath("//iframe[@name='mplay']/@src")[0]
    movie_url = parse.urljoin(url, src)
    return movie_url
    pass
# 访问src_url，提取到第一层m3U8文件地址
def get_m3u8_url(movie_url):
    # 在js代码里提取数据，最好用的就是re
    sourcecode = get_page_source(movie_url)
    obj = re.compile(r'url: "(?P<m3u8>.*?)"')

    return obj.search(sourcecode).group("m3u8")
    
    pass

def download_m3u8_file(m3u8_url1):

    sourcecode = get_page_source(m3u8_url1)
    m3u8_url2 = parse.urljoin(m3u8_url1,sourcecode.split("\n")[2])
    m3u8file = get_page_source(m3u8_url2)
    filename = "moviem3u8.txt"
    with open(filename, mode="w") as f:
        f.write(m3u8file)
    return filename
    pass
    
        
        
async def download_one_ts(file_path,ts_url,sem):

    filename = ts_url.split("/")[-1].strip()
    # print(ts_url)
    for i in range(10):
        try:
            async with sem:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=ts_url) as resp:
                        content = await resp.content.read()
                        async with aiofiles.open(f'{file_path}/{filename}',mode="wb") as f:
                            await f.write(content)
                            print(ts_url,"完成")
                            break

        except Exception as e:
            print("error发生，url=",ts_url,f"正在重试，第{i}次")
            print(e)




async def download_all_ts(filename):
    
    
    tasks = []

    file_path = "./缓存文件夹"

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    semaphore = asyncio.Semaphore(500)
    with open(filename,mode="r",encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue

            task = asyncio.create_task(download_one_ts(file_path = file_path,ts_url = line,sem = semaphore))
            tasks.append(task)
        
        await asyncio.wait(tasks)


  
def decrypt():
    

    pass


def mergemp4(file_path, m3u8file):
    name_list = []
    with open(m3u8file,mode="r",encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                else:
                    line = line.strip()
                    name_list.append(line.split("/")[-1])

    now_dir = os.getcwd()
    os.chdir("缓存文件夹")
    temp = []
    n = 0
    for i in range(len(name_list)):
        name = name_list[i]
        temp.append(name)  # [a.ts, b.ts, c.ts]
        if i != 0 and i % 100 == 0:  # 每100个合并一次
            # 合并,
            # cat a.ts b.ts c.ts > xxx.mp4
            # copy /b a.ts + b.ts + c.ts xxx.mp4
            names = " + ".join(temp)
            os.system(f"copy /b {names} {n}.ts")
            n += 1
            temp = []  # 还原成新的待合并列表
    # 把最后没有合并的进行收尾
    names = " + ".join(temp)
    os.system(f"copy /b {names} {n}.ts")

    n += 1

    temp_2 = []
    # 把所有的n进行循环
    for i in range(0, n+1):
        temp_2.append(f"{i}.ts")

    names = " + ".join(temp_2)
    os.system(f"copy /b {names} movie.mp4")

    # 3. 所有的操作之后. 一定要把工作目录切换回来
    os.chdir(now_dir)
    os.system(f"move 缓存文件夹\movie.mp4 movie.mp4")
    os.system(f"rd/s/q 缓存文件夹 缓存文件夹")






    

def main():

    # url = "https://www.wbdyba.com/play/45674_1_1.html"
    

    # movie_url = get_iframe_url(url=url , page_sourse= get_page_source(url=url))
    # m3u8_url1 = get_m3u8_url(movie_url=movie_url)
    # filename = download_m3u8_file(m3u8_url1=m3u8_url1)
    filename = "moviem3u8.txt"
    
    # asyncio.run(download_all_ts(filename))
    mergemp4("缓存文件夹",filename)
    
async def run():
    semaphore = asyncio.Semaphore(500)		 # 限制并发量为500,这里windows需要进行并发限制，
    						#不然将报错：ValueError: too many file descriptors in select()

    to_get = [main("http://blog.jobbole.com/{}/".format(_),semaphore) for _ in range(114364,120000)]
    																 #总共1000任务
    await asyncio.wait(to_get)


if __name__ == "__main__":
    main()
    print("done!")



