# -*- coding:UTF-8 -*-

import requests
import codecs
import json 
#import matplotlib
import numpy as np
import os
import time
#from math import log10


def getStyleRating(rating,text):
	if rating == 0:
		ret = '<span class="U">%s</span>'%text
	elif rating < 1200:
		ret = '<span class="N">%s</span>'%text
	elif rating < 1400:
		ret = '<span class="P">%s</span>'%text
	elif rating < 1600:
		ret = '<span class="S">%s</span>'%text
	elif rating < 1900:
		ret = '<span class="E">%s</span>'%text
	elif rating < 2100:
		ret = '<span class="CM">%s</span>'%text
	elif rating < 2300:
		ret = '<span class="M">%s</span>'%text
	elif rating < 2400:
		ret = '<span class="IM">%s</span>'%text
	elif rating < 2600:
		ret = '<span class="GM">%s</span>'%text
	elif rating < 3000:
		ret = '<span class="IGM">%s</span>'%text
	else:
		ret = '<span class="LGM1">%s</span><span class="LGM">%s</span>'%(text[0],text[1:])
	return ret

def getStyleText(handle,rating,flag=False):
	text = getStyleRating(rating,handle)
	if flag:
		text = '<a href="http://codeforces.com/profile/%s" target="_blank">%s</a>'%(handle,text)
	return text

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
		self.ratingChange = []
		self.lastContestDate = 'no_contest'

	def ratingChangeToString(self):
		text = ''
		if self.cnt > 0: 
			for x in self.ratingChange[:-1]:
				text = text + getStyleText(str(x),x) + '&rarr;'
			text = text + getStyleText(str(self.ratingChange[-1]),self.ratingChange[-1])
		return text

	def prt(self):
		print("%s,%s,%s,%d,%d,%d,%d,%d,%s,%s"%(self.handle,self.name,self.status,self.cnt,self.cur,self.minR,self.maxR,self.last5,self.lastContestDate))
	def toHtml(self):
		html = '<td>%s</td>'%getStyleText(self.handle,self.cur,True)
		html = html + '<td>%s</td><td>%s</td><td>%d</td>'%(self.name,self.status,self.cnt)
		html = html + '<td>%s</td>'%getStyleText(str(self.cur),self.cur)
		html = html + '<td>%s</td>'%getStyleText(str(self.minR),self.minR)
		html = html + '<td>%s</td>'%getStyleText(str(self.maxR),self.maxR)
		html = html + '<td>%s&ensp; / &ensp; %s</td>'%(self.ratingChangeToString(),getStyleText(str(self.last5),self.last5))
		html = html + '<td>%s</td>'%(self.lastContestDate)
		return html


def getUserRating(handle):
    target = 'http://codeforces.com/api/user.rating?handle='+handle
    flag = False
    rating = ''
    try:
    	req = requests.get(url=target)
    except Exception as e:
    	print(e)
    else:
    	rating = json.loads(req.text)
    	flag = True
    
    finally:    
    	return flag,rating

def getUsersRating(users):
	for user in users:
		print("reading infomation:%s,%s"%(user.handle,user.name))
		cnt = 0
		flag = False
		while not flag and cnt < 5:
			flag,rating = getUserRating(user.handle)
			cnt = cnt + 1
			if not flag:
				time.sleep(1)
				print('retry read information: %s %d times'%(user.handle,cnt))
		if cnt >= 5:
			print('Can not read information: %s'%user.handle)
			continue
		if rating["status"] == "OK":
			user.cnt = len(rating["result"])
			if user.cnt == 0:
				user.status = 'unrated'
			elif user.cnt < 10:  
				user.status = 'penalty'
			if user.cnt > 0 :
				ratingList = [x['newRating'] for x in rating['result']]			
				user.minR = min(ratingList)
				user.maxR = max(ratingList)
				user.cur = ratingList[-1]
				localtime = time.localtime(rating['result'][-1]['ratingUpdateTimeSeconds'])
				dt = time.strftime('%Y-%m-%d',localtime)
				user.lastContestDate = dt;
				k = min(user.cnt,5)
				user.ratingChange.append(rating['result'][-k]['oldRating'])
				user.ratingChange.extend([x['newRating'] for x in rating['result'][-k:]])
				#if user.cnt >= 5:
				#	user.last5 = int(round(np.mean(ratingList[-5:])))
				if k == 5 :
					coffs = np.array([0.9,0.95,1.00,1.05,1.10])
				elif k == 4:
					coffs = np.array([.90,.95,1.05,1.10])
				elif k == 3:
					coffs = np.array([.95,1.00,1.05])
				elif k == 2:
					coffs = np.array([.95,1.05])
				else:
					coffs = np.array([1.00])
				x = np.array(ratingList[-k:])
				user.last5 = int(round(np.mean(x*coffs)))
				if user.cnt < 10:
					coff = (user.cnt + 30) / 40 
				else:
					coff = 1.0
				user.last5 = int(round(user.last5 * coff))
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
				<tr><th>排名</th><th>账号</th><th>姓名</th><th>状态</th><th>场次</th><th>当前</th><th>最低</th><th>最高</th><th>最近5场/加权平均</th><th>最近比赛日期</th></tr>
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