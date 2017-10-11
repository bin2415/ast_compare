#!/usr/bin/python
# -*- coding: utf-8 -*-

import ast
import Levenshtein
import codecs
import re
from ast_construct import *
from collections import deque

def match_two_files(file1_name, file2_name):
    left_ast = parse_file(file1_name)
    left_root = Node('ast_root', 'root')
    ast_construct(left_ast, left_root)
    left_nums = get_nums(left_root)
    
    right_ast = parse_file(file2_name)
    right_root = Node('ast_root', 'root')
    ast_construct(right_ast, right_root)
    right_nums = get_nums(right_root)

    nums = left_nums if left_nums >= right_nums else right_nums
    
    matchers = [0.0]

    find_max_matchers(left_root, right_root, matchers)
    matchers[0] -= 1
    nums -= 1
    
    print('matching rate is %f' % (float(matchers[0])/nums))

def find_max_matchers(root1, root2, matchers):
    #如果两个节点的标签一样
    if root1.label == root2.label:
        # 如果两个节点的字符串莱文斯坦比大于0.6表示匹配成功
        if Levenshtein.ratio(root1.value, root2.value) > 0.8:
            print root1.value
            print root2.value
            matchers[0] += 1
        #matchers[0] += 1
    else:
        if len(root1.childen) > 0:
            for r_child in root2.childen:
                find_max_matchers(root1, r_child, matchers)
        if len(root2.childen) > 0:
            for l_child in root1.childen:
                find_max_matchers(l_child, root2, matchers)

    if len(root1.childen) > 0 and len(root2.childen) > 0:
        for i in range(len(root1.childen)):
            for j in range(i,len(root2.childen)):
                find_max_matchers(root1.childen[i], root2.childen[j], matchers)




def get_nums(tree):
    queue = deque()
    queue.append(tree)
    id_count = 0
    while len(queue) > 0:
        current = queue.popleft()
        #current.id = id_count
        id_count += 1
        for child in current.childen:
            queue.append(child)
    return id_count


def parse_file(filename):
    global enc, lines
    enc, enc_len = detect_encoding(filename)
    f = codecs.open(filename, 'r', enc)
    lines = f.read()

    # remove BOM
    lines = re.sub(u'\ufeff', ' ', lines)

    if enc_len > 0:
        lines = re.sub('#.*coding\s*[:=]\s*[\w\d\-]+',  '#' + ' ' * (enc_len-1), lines)

    f.close()
    return parse_string(lines, filename)


def parse_string(string, filename=None):
    tree = ast.parse(string)
    if filename:
        tree.filename = filename
    print ast.dump(tree)
    return tree


def detect_encoding(path):
    fin = open(path, 'rb')
    prefix = str(fin.read(80))
    encs = re.findall('#.*coding\s*[:=]\s*([\w\d\-]+)', prefix)
    decl = re.findall('#.*coding\s*[:=]\s*[\w\d\-]+', prefix)

    if encs:
        enc1 = encs[0]
        enc_len = len(decl[0])
        try:
            info = codecs.lookup(enc1)
            # print('lookedup: ', info)
        except LookupError:
            # print('encoding not exist: ' + enc1)
            return 'latin1', enc_len
        return enc1, enc_len
    else:
        return 'latin1', -1


