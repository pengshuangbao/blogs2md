# -*- coding: utf-8 -*-
import _locale
from configparser import ConfigParser

import execjs
import os

""" 
使用execjs调用node.js,使用turndown框架将html转换为markdown 
"""

config = ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'blogs2md.ini'))
profile = config.get("config", "profile")
os.environ["NODE_PATH"] = config.get(profile, "node_module_path")
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
