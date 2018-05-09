# -*- coding: utf-8 -*-
import _locale
import execjs
import os

""" 
使用execjs调用node.js,使用turndown框架将html转换为markdown 
"""

os.environ["NODE_PATH"] = "C:\\Users\\admin\\node_modules\\"
os.environ["EXECJS_RUNTIME"] = "Node"
script = '''
var TurndownService = require('turndown')
var turndownService = new TurndownService({gfm:true,codeBlockStyle:\"fenced\"})
function md(html,args){
  return turndownService.turndown(html,args)
}
'''
# 设置默认的编码
_locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])
parser = execjs.compile(script)


def transform(html):
    result = parser.call('md', html)
    return result
