"""
指定单个关键字图片的获取
"""
import asyncio
import requests
import re
import os
import time
import getpass
import aiohttp
from faker import Faker
import csv


def mkdirs():
    # 获取计算机的用户名
    user_name = getpass.getuser()
    # 保存至桌面
    outputs = f'C:/Users/{user_name}/Desktop/outputs'
    data_dir_name = outputs + r'/' + 'data'
    log_dir_name = outputs + r'/' + 'log'
    error_dir_name = outputs + r'/' + 'error'
    try:  # 如果没有文件夹就创建
        os.mkdir(outputs)
        os.mkdir(data_dir_name)
        os.mkdir(log_dir_name)
        os.mkdir(error_dir_name)
    except:
        pass

    return data_dir_name, log_dir_name, error_dir_name


def exec_wrong():
    try:
        # 处理报错关键字
        print('开始处理报错关键字')
        while True:
            error_keyword_path = f'{error_dir_name}' + r'/' + 'error_keyword.txt'
            # 将error关键字读取到列表
            f2 = open(error_keyword_path, 'r+', encoding='utf-8')
            error_kw_list = f2.readlines()
            f2.close()

            # 将error关键字文件内容清空
            f2 = open(error_keyword_path, 'r+', encoding='utf-8')
            f2.truncate(0)
            f2.close()
            print(error_kw_list)
            if error_kw_list == []:
                print('已将报错关键字再次爬取成功')
                break
            else:
                # error_keyword.txt中没有空，则继续爬
                for kw in error_kw_list:
                    keyword = kw.strip('\n')
                    try:
                        print('-' * 50 + f'正在爬取：{keyword}' + '-' * 50)
                        # 下载图片函数
                        download_pics(keyword, nums)
                        print('-' * 50 + f'爬取完成' + '-' * 50)
                        print()
                    except:
                        print(f'error：关键字【{keyword}】爬取失败 ！')
                        # 记录报错、报错的keyword
                        error_log = open(f'{error_dir_name}' + r'/' + 'error_log.txt', 'a', encoding='utf-8')
                        error_log.write(f'error：关键字【{keyword}】爬取失败 ！\n')
                        error_keyword = open(f'{error_dir_name}' + r'/' + 'error_keyword.txt', 'a', encoding='utf-8')
                        error_keyword.write(f'{keyword}\n')
    except:
        print('无报错关键字处理')


async def download_pic(url, data_dir_name, keyword, sem, csvwriter):
    global count
    async with sem:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    count += 1
                    string = f'{data_dir_name}' + r'\\' + keyword + r'\\' + keyword + '_' + str(count) + '.jpg'
                    with open(string, mode='wb') as f:
                        f.write(await resp.content.read())
                    csvwriter.writerow([string, url])
                    print(f"第{count}张图片已爬取完毕,链接为{url}")
            except BaseException:
                print('错误，当前图片无法下载')


def download_pics(keyword, nums):
    global count
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        "User-Agent": Faker().user_agent(),
        'Host': 'image.baidu.com',
        'Referer': 'https://image.baidu'
                   '.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=&st=-1&fm=result&fr=&sf=1&fmq=1610952036123_R&pv=&ic=&nc=1&z=&hd=&latest=&copyright=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&sid=&word=%E6%98%9F%E9%99%85',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest'
    }

    url = 'http://image.baidu.com/search/index?tn=baiduimage&fm=result&ie=utf-8&word='  # 百度链接
    is_outindex = False  # 判断需要的数量是否大于百度图库拥有的数量
    keyword = keyword
    countmax = nums
    url = url + keyword + "&pn="

    # 获取初始时间
    time_start = time.time()

    # get方式获取数据
    strhtml = requests.get(url, headers=headers, timeout=20)
    string = str(strhtml.text)

    # 正则表达式取得图片总数量
    totalnum = re.findall('<div id="resultInfo" style="font-size: 13px;">(.*?)</div>', string)
    totalnumInt = re.findall('<div id="resultInfo" style="font-size: 13px;">找到相关图片(.*?)张</div>', string)
    print("百度图片" + totalnum[0])
    # if int(nums) > int(totalnumInt[0]):
    #     is_outindex = True

    img_url_regex = '"thumbURL":"(.*?)",'  # 正则匹配式
    count = 0  # 总共下载的图片数
    index = 0  # 链接后面的序号
    page = 0  # 当前搜集的页

    path_file_name = f'{log_dir_name}' + r'/' + f'{keyword}_log.csv'
    csvfile = open(path_file_name, "a", encoding='utf_8_sig', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(['pic_path', 'pic_url'])
    # try:
    while True:
        strhtml = requests.get(url + str(index), headers=headers)  # get方式获取数据
        string = str(strhtml.text)
        print("已爬取网页")
        pic_url = re.findall(img_url_regex, string)  # 先利用正则表达式找到图片url
        print("第" + str(page + 1) + "页共收集到" + str(len(pic_url)) + "张图片")
        if count + len(pic_url) >= countmax:
            pic_url = pic_url[:-(count + len(pic_url) - countmax)]
        else:
            pic_url = pic_url

        index += len(pic_url)  # 网址索引向后，跳到下一页继续搜刮图片
        try:  # 如果没有文件夹就创建
            os.mkdir(f'{data_dir_name}' + r'/' + keyword)
        except:
            pass
        # 设置最大同时10个线程
        sem = asyncio.Semaphore(10)
        loop = asyncio.get_event_loop()
        tasks = [download_pic(url, data_dir_name, keyword, sem, writer) for url in pic_url]
        loop.run_until_complete(asyncio.wait(tasks))
        if countmax == count:
            break
        page += 1


    # except:
    #     if is_outindex == True:
    #         pass
    #     else:
    #         raise TypeError()
    time_end = time.time()  # 获取结束时间
    print('处理完毕，共耗时:' + str(time_end - time_start) + "秒")

if __name__ == '__main__':
    start = time.time()
    print('------0:指定单个关键字\t模式1：指定多个关键字------')
    mode = eval(input('请选择模式(0或1): '))

    # 单个关键字模式
    if mode == 0:
        keyword = input('请输入图片关键字:')
        nums = eval(input('请输入图片数量：'))
        data_dir_name, log_dir_name, error_dir_name = mkdirs()
        download_pics(keyword, nums)

    # 多个关键字模式
    elif mode == 1:
        # 获取关键字并遍历
        path = input('请输入关键字文件的绝对路径(为txt文件，一个关键字为一行)：')
        nums = eval(input('请输入图片数量：'))
        data_dir_name, log_dir_name, error_dir_name = mkdirs()
        f = open(rf'{path}', 'r', encoding='utf-8')
        kw_list = f.readlines()
        for kw in kw_list:
            keyword = kw.strip('\n')
            try:
                print('-' * 50 + f'正在爬取：{keyword}' + '-' * 50)
                # 下载图片函数
                download_pics(keyword, nums)
                print('-' * 50 + f'爬取完成' + '-' * 50)
                print()
            except Exception as e:
                print(e)
                print(f'error：关键字【{keyword}】爬取失败 ！')
                # 记录报错、报错的keyword
                error_log = open(f'{error_dir_name}' + r'/' + 'error_log.txt', 'a', encoding='utf-8')
                error_log.write(f'error：关键字【{keyword}】爬取失败 ！\n')
                error_keyword = open(f'{error_dir_name}' + r'/' + 'error_keyword.txt', 'a', encoding='utf-8')
                error_keyword.write(f'{keyword}\n')
        else:
            # 处理无效关键词
            exec_wrong()
    else:
        print('无效输入')
    end = time.time()
    print(f"总耗时为{start - end}")
