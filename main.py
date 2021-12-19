# coding: utf-8
import os
import re
import json
# 相同方法，对于当前页面需要刷新的数据，也可以通过Python脚本去遍历，获取TagName: 的标签，PageName就是当前文件夹的名字
# 同样写成配置文件JSON格式，App启动初始化的时候，就去读取配置文件，根据 key - value 去匹配
# 这个过程可以在点击下载按钮的时候，去完成


class Traverse:
    # def __init__(self):

    # 获取本地指定目录及其子目录下的所有文件
    def get_all_file(self, path):
        file_list = []
        # cur_path 表示当前正在访问的文件夹路径
        # cur_dirs 表示该文件夹下的子目录名list
        # cur_files 表示该文件夹下的文件list
        # os.walk获取文件夹下及其所有子文件夹下的文件 os.listdir 需要递归遍历
        for cur_path, cur_dirs, cur_files in os.walk(path):
            for name in cur_files:
                # os.path.join()在Linux/macOS下会以斜杠（/）分隔路径，而在Windows下则会以反斜杠（\）分隔路径。
                filename = os.path.join(cur_path, name)
                filename = filename.replace('\\', '/')
                file_list.append(filename)
        return file_list

    def write_text_to_json(self, ts_list):
        all_ts_dict = {"tans": []}
        all_ts_dict["tans"] = ts_list
        with open('zh_CN.json', 'w', encoding='utf-8') as file_obj:
            # indent=4 有缩进
            # ensure_ascii=False 处理中文乱码问题
            listallarr2 = json.dumps(
                all_ts_dict, indent=4, ensure_ascii=False)
            file_obj.write(listallarr2)

    def find_ts_text(self, path):
        file_list = self.get_all_file(path)
        all_text_list = []
        # 正则表达式匹配qsTr 括号里面的内容，包含换行符号
        # 查找("")里面的内容，内容不能换行
        pattern_qstr = re.compile(r'qsTr[\s]*\([\s]*"(.*)"[\s]*\)')
        # pattern_quotes = re.compile(r'[\s\S]*(\"[\s\S]*\")[\s\S]*')
        for file in file_list:
            if file.endswith('.qml') or file.endswith('.js'):
                with open(file, 'r', encoding='utf-8') as fr:
                    # 遍历每行其实可以用 search
                    # for line in fr:
                    qstr_match = pattern_qstr.findall(fr.read())
                    if qstr_match:
                        for text in qstr_match:
                            text_dict = {"source": "", "translation": ""}
                            text_dict["source"] = text
                            all_text_list.append(text_dict)
        self.write_text_to_json(all_text_list)


if __name__ == '__main__':
    WriteQsTr = Traverse()
    local_path = r'./Test'
    WriteQsTr.find_ts_text(local_path)
