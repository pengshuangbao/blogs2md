# coding=utf-8
import os
from queue import Queue


def remove_element_for_html(div_str="", tag="div", class_str="dp-highlighter"):
    class_index = div_str.index(class_str)
    start = div_str.rfind('<' + tag, 0, class_index)
    end = find_end(div_str, tag, start + 4)
    # 这里不能用rfind rfind是从最后面找的，找最大的那个，find是找最小的那个
    all_end = div_str.find('>', end)
    return div_str[0:start] + div_str[all_end + 1:]


def find_end(html="", tag="div", begin=0):
    html = html[begin:]
    queue = Queue()
    queue.put(begin)
    splits = html.split("\n")
    position = begin
    for split in splits:
        position += len(split)
        if "<" + tag in split:
            queue.put(position)
        if "/" + tag + ">" in split:
            if queue.qsize() == 1:
                return position
            else:
                queue.get()
    return -1


def delete_file_folder(src):
    if os.path.isfile(src):
        try:
            os.remove(src)
        except IOError:
            pass

    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc = os.path.join(src, item)
            delete_file_folder(itemsrc)
        try:
            os.rmdir(src)
        except IOError:
            pass


def find_sub_str(substring, string, i):
    count = 0
    while i > 0:
        index = string.find(substring)
        if index == -1:
            return -1
        else:
            string = string[index + 1:]  # 第一次出现的位置截止后的字符串
            i -= 1
            count = count + index + 1  # 字符串位置数累加
    return count - 1

