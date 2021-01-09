import requests
import time
import json
import base64,re,os
#1.登陆教务网
class random_num():#获取验证码
	def tryagain(self,name):
		eval("self."+name + '()')
	def __init__(self):
	# client_id 为官网获取的AK， client_secret 为官网获取的SK
		try:
			self.session = requests.session()
			self.session.get("http://jwc.swjtu.edu.cn/service/login.html")
			host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=Wd8p7GGkRpb6KXB4Qu5fByvj&client_secret=tQAxfDVDoW9OzreQY2VsR17TP9pTaDUy'
			response = requests.get(host)
			if response:
				self.access_token = response.json()['access_token']
		except:
			self.tryagain('init')
	def get_str(self):
		r = self.session.get("http://jwc.swjtu.edu.cn/vatuu/GetRandomNumberToJPEG?test="+str(int(time.time())))
		img = base64.b64encode(r.content)
		params = {"image":img}
		request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage"
		request_url = request_url + "?access_token=" + self.access_token
		headers = {'content-type': 'application/x-www-form-urlencoded'}
		response = requests.post(request_url, data=params, headers=headers)
		if response:
			#print(response.json())
			try:
				result = response.json()['words_result'][0]
				print('1',result)
				self.result = result['words'].strip()
				if len(self.result) != 4:
					print(self.result)
					raise Exception("Invalid")
			except:
				self.tryagain('get_str')


class login():#柔和验证码获取
	def tryagain(self,name):
		print('重试'+name)
		eval("self."+name + '()')
	def get_str(self):
		r = self.session.get("http://jwc.swjtu.edu.cn/vatuu/GetRandomNumberToJPEG?test="+str(int(time.time())))
		img = base64.b64encode(r.content)
		params = {"image":img}
		request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"#accurate_basic"
		request_url = request_url + "?access_token=" + self.access_token
		headers = {'content-type': 'application/x-www-form-urlencoded'}
		response = requests.post(request_url, data=params, headers=headers)
		if response:
			#print(response.json())
			try:
				result = response.json()['words_result'][0]
				#print('1',result)
				self.yzm = result['words'].strip()
				if len(self.yzm) != 4:
					print(self.yzm)
					raise Exception("Invalid")
			except:
				print(response.text)
				self.tryagain('get_str')
	def __init__(self,username="",password=""):
		#获取用户信息
		if(username and password):
			self.username = username
			self.password = password
		else:
			self.username = input("请输入教务网用户名：")
			self.password = input("请输入密码：")
		try:
			os.system('cls')
		except:
			pass
		print("正在获取验证码......")
		try:
			self.session = requests.session()
			self.session.get("http://jwc.swjtu.edu.cn/service/login.html")
			host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=Wd8p7GGkRpb6KXB4Qu5fByvj&client_secret=tQAxfDVDoW9OzreQY2VsR17TP9pTaDUy'
			response = requests.get(host)
			if response:
				self.access_token = response.json()['access_token']
		except:
			self.tryagain('__init__')

		self.get_str()#获取验证码
		print('验证码解析成功：',self.yzm)
		#模拟登陆
		#第一步POST发送
		sendmsg = {
		    'username' : self.username,
		    'password' : self.password,
		    'url' : 'http://jwc.swjtu.edu.cn/vatuu/UserExitAction&returnUrl',
		    'area' : '',
		    'ranstring' : self.yzm,
		    }
		login_header = {
		    'Referer' : 'http://jwc.swjtu.edu.cn/service/login.html',
		    'Origin' : 'http://jwc.swjtu.edu.cn',
		    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
		    'DNT' : '1',
		    'Accept' : 'application/json, text/javascript, */*; q=0.01',
		    'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
		    'X-Requested-With' : 'XMLHttpRequest',
		}
		r = self.session.post("http://jwc.swjtu.edu.cn/vatuu/UserLoginAction", data=sendmsg ,headers=login_header)
		loginMsg = json.loads(r.text)['loginMsg']
		print(loginMsg)
		if '不正确' in loginMsg:
			self.__init__(self.username,self.password)

		#第二步确认登陆
		sendmsg = {
		    'url' : 'http://jwc.swjtu.edu.cn/vatuu/UserExitAction&returnUrl',
		    'returnUrl' : '',
		    'loginMsg' : loginMsg
		}
		login_header = {
		    'Referer' : 'http://jwc.swjtu.edu.cn/vatuu/StudentScoreInfoAction?setAction=studentMarkUseProgram',
		    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
		    'DNT' : '1',
		    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
		    'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
		    'Upgrade-Insecure-Requests' : '1',
		    'Accept-Encoding' : 'deflate',
		    'Accept-Language' : 'zh-CN,zh;q=0.9'
		}
		r = self.session.post("http://jwc.swjtu.edu.cn/vatuu/UserLoadingAction", data=sendmsg ,headers=login_header)
		#已经成功登陆