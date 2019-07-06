# -*- coding:UTF-8 -*-

import requests
import codecs
import json 
#import matplotlib
import numpy as np
import os


def getStyleCell(handle,rating,flag=False):
	if flag:
		handle = '<a href="http://codeforces.com/profile/%s" target="_blank">%s</a>'%(handle,handle)
	if rating == 0:
		ret = '<td class="U">%s</td>'%handle
	elif rating < 1200:
		ret = '<td class="N">%s</td>'%handle
	elif rating < 1400:
		ret = '<td class="P">%s</td>'%handle
	elif rating < 1600:
		ret = '<td class="S">%s</td>'%handle
	elif rating < 1900:
		ret = '<td class="E">%s</td>'%handle
	elif rating < 2100:
		ret = '<td class="CM">%s</td>'%handle
	elif rating < 2300:
		ret = '<td class="M">%s</td>'%handle
	elif rating < 2400:
		ret = '<td class="IM">%s</td>'%handle
	elif rating < 2600:
		ret = '<td class="GM">%s</td>'%handle
	elif rating < 3000:
		ret = '<td class="IGM">%s</td>'%handle
	else:
		ret = '<td class="N"><span class="LGM1">%s</span>%s</td>'%(handle[0],handle[1:])
	return ret

class User(object):
	def __init__(self,handle,name):
		self.handle = handle
		self.name = name
		self.status = 'ok'
		self.cnt = 0
		self.cur = 0
		self.minR = 0
		self.maxR = 0
		self.last5 = 0
	def prt(self):
		print("%s,%s,%s,%d,%d,%d,%d,%d"%(self.handle,self.name,self.status,self.cnt,self.cur,self.minR,self.maxR,self.last5))
	def toHtml(self):
		html = getStyleCell(self.handle,self.cur,True)
		html = html + '<td>%s</td><td>%s</td><td>%d</td>'%(self.name,self.status,self.cnt)
		html = html + getStyleCell(str(self.cur),self.cur)
		html = html + getStyleCell(str(self.minR),self.minR)
		html = html + getStyleCell(str(self.maxR),self.maxR)
		html = html + getStyleCell(str(self.last5),self.last5)
		return html


def getUserRating(handle):
    target = 'http://codeforces.com/api/user.rating?handle='+handle
    req = requests.get(url=target)
    rating = json.loads(req.text)
    return rating

def getUsersRating(users):
	for user in users:
		print("reading infomation:%s,%s"%(user.handle,user.name))
		rating = getUserRating(user.handle)
		if rating["status"] == "OK":
			user.cnt = len(rating["result"])
			if user.cnt == 0:
				user.status = 'unrated'
			elif user.cnt < 5:  
				user.status = 'insufficient'
			if user.cnt > 0 :
				ratingList = [x['newRating'] for x in rating['result']]			
				user.minR = min(ratingList)
				user.maxR = max(ratingList)
				user.cur = ratingList[-1]
				if user.cnt >= 5:
					user.last5 = int(round(np.mean(ratingList[-5:])))
		else:
			user.status = 'non-existent'



def saveHtml(users,filename):
	fp = codecs.open(filename,"w","UTF-8")
	html_head = u'''<!DOCTYPE html>
	<html>
		<head>
			<meta http-equiv="content-type" content="text/html; charset=UTF-8">
			<link rel="stylesheet" type="text/css" href="rating.css" />
		</head>
		<body>
		<div>
			<table id="rating">
			<tbody>
				<tr><th>排名</th><th>账号</th><th>姓名</th><th>状态</th><th>场次</th><th>当前</th><th>最低</th><th>最高</th><th>最近5场平均</th></tr>
	''';
	fp.write(html_head)
	rank = 0
	for user in users:
		rank = rank + 1
		if rank%2 == 0:
			line = '<tr class="dark"><td>%d</td>%s</tr>\n'%(rank,user.toHtml())
		else:
			line = '<tr><td>%d</td>%s</tr>\n'%(rank,user.toHtml())
		fp.write(line)
	fp.write("</tbody></table></div></body></html>")
	fp.close()


def main():
	fp = codecs.open("users.txt","r","UTF-8")
	print("open files:%s"%fp.name)
	users = []
	for line in fp.readlines():
		handle,name = line.split()		
		users.append(User(handle,name))
	fp.close()
	getUsersRating(users)
	users.sort(key=lambda user: (user.last5,user.cur,user.maxR,user.cnt),reverse=True)
	html_file = "cf_rating.html"
	print('Save to html: %s'%html_file)
	saveHtml(users,html_file)
	print('Done')



if __name__ == '__main__':
			main()		