import os
import yaml

# 运行：python dir_to_yaml.py > dir.txt

# Bug fix: Fix the string literal termination issue and add a comment to indicate that the base_path parameter is not currently used.
def directory_to_yaml(path, base_path='D:\\Project\\trae_project\\Jmoon531.github.io\\docs\\Java基础'):
    """
    此函数用于将指定目录下的所有目录和文件的结构转换为 YAML 格式。
    :param path: 要处理的目录路径
    :return: 包含目录结构的字典
    """
    result = {}
    items = os.listdir(path)
    # Sort items based on the leading 1 or 2 digits in the filename
    # items.sort(key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() and (1 <= len(x.split('.')[0]) <= 2) else float('inf'))
    def custom_sort_key(item):
        try:
            if len(item.split('.')[0].split('-')[0]) != 0:
                return int(item.split('.')[0].split('-')[0])
            else:
                return 999
        except ValueError:
            return 999
    # sorted(items, key=lambda x: int(x.split('.')[0].split('-')[0]) if len(x.split('.')[0].split('-')[0]) != 0 else 0)
    # 对列表进行排序
    sorted_items = sorted(items, key=custom_sort_key)
    for item in sorted_items:
        # 新增：如果目录名为 _resources 则跳过
        if item == '_resources':
            continue
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            result['- ' + item] = directory_to_yaml(item_path)
        else:
            # 获取文件名（不带后缀）
            file_name = os.path.splitext(item)[0]
            # 获取文件绝对路径
            # abs_path = os.path.abspath(item_path)
            relative_path = os.path.relpath(item_path, base_path)
            result['- ' + file_name] = relative_path
    return result

# 指定要处理的目录
directory_path = './docs/Java基础'  # 这里可以修改为你想要处理的目录路径
structure = directory_to_yaml(directory_path)

# 将结构转换为 YAML 格式并打印
# To preserve spaces in values and prevent them from being converted to line breaks,
# you can use the `default_flow_style` parameter and set it to `False`.
yaml_output = yaml.dump(structure, allow_unicode=True, sort_keys=False, default_flow_style=False)
print(yaml_output)