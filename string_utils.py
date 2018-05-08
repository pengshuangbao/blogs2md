# coding=utf-8


def find_sub_str(substr, str, i):
    count = 0
    while i > 0:
        index = str.find(substr)
        if index == -1:
            return -1
        else:
            str = str[index+1:]   #第一次出现的位置截止后的字符串
            i -= 1
            count = count + index + 1   #字符串位置数累加
    return count - 1