import io
from aip import AipOcr
from PIL import ImageGrab


def baiduOCR(string):
    # 百度文字识别
    APP_ID = '23826944'
    API_KEY = 'yqyr5zIRe74XUvgri70ZaOMG'
    SECRECT_KEY = 'yYG016DMMN3hO6Geum61ReflHj7AmTu8'
    client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)

    # 截屏
    img = ImageGrab.grab()
    # 字节容器
    img_b = io.BytesIO()
    # image转换为png
    img.save(img_b, format='PNG')
    # 存入容器
    img_b = img_b.getvalue()

    options = {"recognize_granularity": "small"}
    message = client.general(img_b, options)
    location = dict()
    for f in message['words_result']:
        n = f['words'].find(string)
        if n != -1:
            l = len(string)
            tops = list()
            heights = list()
            left = f['chars'][n]['location']['left']
            right = f['chars'][n + l - 1]['location']['left'] + f['chars'][n + l - 1]['location']['width']
            for i in f['chars'][n:n + l]:
                tops.append(i['location']['top'])
                heights.append(i['location']['height'])
            top = min(tops)
            bottom = top + max(heights)
            location = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
            print(f['words'], location)
            break



if __name__ == "__main__":
    while True:
        string = input('检索屏幕：')
        baiduOCR(string)
