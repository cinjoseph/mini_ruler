
# MiniRuler 简单的规则匹配引擎库

<br>

## 功能介绍

	- 支持解析Int、Float、String等基础类型
	- 支持解析Var、Function等内嵌变量类型，支持Function嵌套
	- 支持比较运算 
		== != > >= < <=
	- 支持与、或逻辑运算
		&&	||

	- 支持运算符优先级
	- 支持多条件匹配
	- 支持圆括号提升优先级，支持圆括号嵌套
	- 支持自定义函数
	- 暂不支持算数运算

For Example：

	IF in_num_range(pkt.id1, 1, 10000) && pkt.id2 <= 7788.672 && ( exist('111', 222, @pid.__id, exist(333)) && (pkt.id1 == 2048 || pkt.id2 <= 7788.672) ) && pkt.s == 'string' THEN ACCEPT()
	IF in_num_range(pkt.id1, 1, 10000) && pkt.id3 == 22 THEN GOTO('rule_3', __builtin_raw__)
	IF in_num_range(pkt.id1, 1, 10000) THEN GOTO('rule_3', __builtin_raw__)


## 试一下
下载后直接执行如下代码，查看样例程序：

python mini_ruler/rule.py 
