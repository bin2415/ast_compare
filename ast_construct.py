#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
构建一个python文件的ast
'''

import ast
import string
import re
import astunparse

#定义AST的节点类

class Node:
    def __init__(self, label, value):
        self.label = label
        self.value = value
        self.childen = list() # 存放孩子节点
        #self.id = 0 #每个节点有一个标识符
    
    def insert_child(self, node):
        self.childen.append(node)

pattern = re.compile('(%s)' % ('|'.join([c for c in string.whitespace])))

#根据astbody构建Node结构的AST

def ast_construct(astbody, parent):
    for child in ast.iter_child_nodes(astbody):
        if isinstance(child, ast.Assign):
            label = 'Assign'
            value = astunparse.unparse(child)
            value = pattern.sub('', value)
            assign = Node(label, value)
            parent.insert_child(assign)
        
        if isinstance(child, ast.Break):
            label = 'Break'
            value = 'break'
            n_break = Node(label, value)
            parent.insert_child(n_break)

        if isinstance(child, ast.Expr):
            if isinstance(child.value, ast.Call):
                label = 'Call'
                value = astunparse.unparse(child.value)
                value = pattern.sub('', value)
                call = Node(label, value)
                parent.insert_child(call)

            else:
                label = 'Expr'
                value = astunparse.unparse(child)
                value = pattern.sub('', value)
                node_expr = Node(label, value)
                parent.insert_child(node_expr)
        
        if isinstance(child, ast.AugAssign):
            label = 'AugAssign'
            value = astunparse.unparse(child)
            value = pattern.sub('', value)
            augassign = Node(label, value)
            parent.insert_child(augassign)

        if isinstance(child, ast.Return):
            n_return = Node('Return', 'return')
            parent.insert_child(n_return)
            # 如果有返回值，对返回值进行处理
            if child.value:
                return_value = astunparse.unparse(child.value)
                return_value = pattern.sub('', return_value)
                if return_value[0] == '(' and return_value[-1] == ')':
                    return_value = return_value[1:-1]
                return_value = return_value.split(',')
                for item in return_value:
                    node_return_value = Node('Return_Value', item)
                    n_return.insert_child(node_return_value)
        
        if isinstance(child, ast.If):
            label = 'If'
            value = astunparse.unparse(child.test) #If节点的value为其判断条件
            value = pattern.sub('', value)
            node_if = Node(label, value)
            parent.insert_child(node_if)

            #如果If包含oreless块，则生成Then和Else作为If的子节点，否则body的内容直接作为If的孩子节点插入
            if child.orelse:
                node_then = Node('Then', value) #自身不带value的节点从其父结点继承value
                node_if.insert_child(node_then)
                source_then = astunparse.unparse(child.body) # If.body无法直接处理，先反解析为源代码，再重新生成ast
                ast_then = ast.parse(source_then)
                ast_construct(ast_then, node_then)

                node_else = Node('Else', value)
                node_if.insert_child(node_else)
                source_else = astunparse.unparse(child.orelse)
                ast_else = ast.parse(source_else)
                ast_construct(ast_else, node_else)
            else:
                source_body = astunparse.unparse(child.body) # If.body无法直接处理，先泛解析为源代码，再重新生成ast
                ast_then = ast.parse(source_body)
                ast_construct(ast_then, node_if)
            
        if isinstance(child, ast.FunctionDef):
            value = child.name
            value = pattern.sub('', value)
            label = 'FunctionDef'
            n_functiondef = Node(label, value)
            parent.insert_child(n_functiondef)
            #parent.insert_child(n_functiondef)
                #处理FunctionDef的参数和装饰器decorator_list,参数分为位置参数args, 可变长度参数vararg和关键字参数kwargs几类
            source_args = astunparse.unparse(child.args)
            source_args = pattern.sub('', source_args)
            args = list() #位置参数
            vararg = list() #可变长度位置参数*args
            kwonlyargs = list() #关键字参数
            kwargs = list() # 可变长度关键字参数**args
            defaults = list()
            kw_defaults = list()
            varargs_flag = 0
            if source_args != "":
                source_args = source_args.split(',')
                for item in source_args:
                    if '**' in item:
                        kwargs.append(item[2:])
                    elif '*' in item:
                        vararg.append(item[1:])
                        varargs_flag = 1
                    elif '=' in item and varargs_flag == 1:
                        kw_defaults.append(item)
                    elif '=' not in item and varargs_flag == 1:
                        kwonlyargs.append(item)
                    elif '=' in item:
                        defaults.append(item)
                    else:
                        args.append(item)
                        
            for arg in args:
                arg_node = Node('args', arg)
                n_functiondef.insert_child(arg_node)
                    
            for arg in vararg:
                vararg_node = Node('vararg', arg)
                n_functiondef.insert_child(vararg_node)
                    
            for arg in kwonlyargs:
                kwonlyargs_node = Node('kwnolyarg', arg)
                n_functiondef.insert_child(kwonlyargs_node)
                    
            for arg in kwargs:
                kwargs_node = Node('kwargs', arg)
                n_functiondef.insert_child(kwargs_node)

            for arg in defaults:
                default_node = Node('default_args', arg)
                n_functiondef.insert_child(default_node)
                    
            for arg in kw_defaults:
                kw_defaults_node = Node('kw_default', arg)
                n_functiondef.insert_child(kw_defaults_node)
                
                #处理Function_body
            source_functionbody = astunparse.unparse(child.body)
            ast_functionbody = ast.parse(source_functionbody)
            ast_construct(ast_functionbody, n_functiondef)
            
        if isinstance(child, ast.ClassDef):
            class_name = child.name
            label = 'ClassDef'
            node_classdef = Node(label, class_name)
            parent.insert_child(node_classdef)
            # 处理基类
            bases = astunparse.unparse(child.bases) #只考虑name和base, keywos, starargs等暂时不考虑
            bases = pattern.sub('', bases)
            if bases != '':
                node_bases = Node('base', bases)
                node_classdef.insert_child(node_bases)
                
                #处理 class body
            source_classbody = astunparse.unparse(child.body)
            ast_classbody = ast.parse(source_classbody)
            ast_construct(ast_classbody, node_classdef)
            
        if isinstance(child, ast.For):
            label = 'For'
            value = astunparse.unparse(child.iter) #For的value在考虑
            value = pattern.sub('', value)
            node_for = Node(label, value)
            parent.insert_child(node_for)
            #判断For循环是否有else部分，如果有，new一个ForBody和ForElse作为Node_For的孩子节点;否则，for.body直接作为For的孩子节点插入
            if child.orelse:
            #处理For.body
                node_then = Node('Then', value)
                node_for.insert_child(node_then)
                source_then = astunparse.unparse(child.body)
                ast_then = ast.parse(source_then)
                ast_construct(ast_then, node_then)
                node_else = Node('Else', value)
                node_for.insert_child(node_else)
                source_else = astunparse.unparse(child.orelse)
                ast_else = ast.parse(source_else)
                ast_construct(ast_else, node_else)
            else:
                source_forbody = astunparse.unparse(child.body)
                ast_forbody = ast.parse(source_forbody)
                ast_construct(ast_forbody, node_for)
                
        if isinstance(child, ast.While):
            label = 'While'
            value = astunparse.unparse(child.test)
            value = pattern.sub('', value)
            node_while = Node(label, value)
            parent.insert_child(node_while)
            source_whilebody = astunparse.unparse(child.body)
            ast_whilebody = ast.parse(source_whilebody)
            ast_construct(ast_whilebody, node_while)
                    

