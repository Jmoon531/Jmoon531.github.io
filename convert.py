import re

def html_img_to_markdown(html):
    # html = '<img src="images/Redis底层数据结构.png" alt="image-20211129214602845" style="zoom: 33%;" />'
    # 定义正则表达式模式
    pattern = r'<img\s+src="([^"]+)"'
    # 查找匹配项
    match = re.search(pattern, html)
    if match:
        src = match.group(1)
        return '![](./'+src+')'

while True:
    # 从控制台获取用户输入
    user_input = input()
    # 检查用户是否输入了退出指令
    if user_input.lower() == 'quit':
        break
    # 打印用户输入的内容
    print(html_img_to_markdown(user_input))