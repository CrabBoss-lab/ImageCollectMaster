# 导入依赖库
import time
import aiohttp
import asyncio
import requests
import os
from faker import Faker

headers = {
            'User-Agent': Faker().user_agent()
        }
async def download_image(url,keyword,dir_name):
    global count
    async with aiohttp.ClientSession() as client:
        async with client.get(url,headers=headers) as resp:
            with open(os.path.join(dir_name, f'{keyword}_{count}.jpg'), 'wb') as f:
                f.write(await resp.content.read())
                count += 1
                print(f'正在下载第 {count} 张图片')
                print(url)

async def download_images(keyword: str, num: int, save_path: str):
    global num_count
    """
    爬取百度图片搜索结果中指定关键词keyword的前 num 张图片，并下载到指定文件夹。
    :param keyword: 搜索关键词
    :param num: 需要下载的图片数量
    :param save_path:保存路径
    """
    # 创建保存图片的文件夹
    dir_name = f'{save_path}/outputs/{keyword}'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    count = 0
    page_num = 0
    thumb_list = []
    # 持续爬取图片，直到达到指定数量
    while True:
        print(f'正在爬取第{page_num + 1}页...')

        # 待请求URL
        url = f'https://image.baidu.com/search/acjson?tn=resultjs' \
              f'on_com&logid=11513145951136847483&ipn=rj&ct=20132659' \
              f'2&is=&fp=result&fr=&word={keyword}&queryWord={keyword}&' \
              f'cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&hd=&late' \
              f'st=&copyright=&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&' \
              f'nc=1&expermode=&nojc=&isAsync=&pn={page_num * 30}&rn=30&gsm=5a&1683422786613='

        # 模拟请求头
        headers = {
            'User-Agent': Faker().user_agent()
        }

        # 发送 HTTP 请求，获取响应结果并解析 JSON 数据
        response = requests.get(url, headers=headers).json()


        # 遍历所有图片信息
        for image_info in response['data']:
            try:
                # 打印当前正在下载的图片的 URL
                thumb_list.append(image_info['thumbURL'])
                # print(image_info['thumbURL'])
                # 下载图片并保存到本地文件夹
                # image_data = requests.get(image_info['thumbURL'], headers=headers)
                # with open(os.path.join(dir_name, f'{keyword}_{count}.jpg'), 'wb') as f:
                #     f.write(image_data.content)
                num_count += 1

                # 如果已经下载了足够数量的图片，则退出爬虫程序
                if num_count >= num:
                    tasks = []
                    for url in thumb_list:
                        tasks.append(asyncio.create_task(download_image(url,keyword,dir_name)))
                    await asyncio.wait(tasks)
                    print(f'一共下载了 {num} 张图片！！！！！！')
                    print(f'图片已保存至:{dir_name}')
                    return

            except:
                pass
        # 增加页数，以爬取下一页的图片
        page_num += 1

async def main():
    keyword = input('请输入关键字:')
    num = eval(input('请输入数量:'))
    await download_images(keyword, num,save_path='data')

if __name__ == '__main__':
    num_count = 0
    count = 0
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end = time.time()
    print(f"总用时{int(end - start)}s")