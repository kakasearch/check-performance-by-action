#获取课程代码，已获取完毕
#写一个下载器，功能：自定义headers,cookie,session,不要重复下载，多线程下载
#获取全部文件的下载url
#传递给下载器，修改保存代码，从url获取文件后缀
# requests lxml webdav3

import swjtu_jw_login
import requests
import re,os
from lxml import etree
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from webdav3.client import Client
from webdav3.exceptions import LocalResourceNotFound
from webdav3.urn import Urn
class davclient(Client):
	def download_file(self, remote_path,progress=None):
		"""Downloads file from WebDAV server and save it locally.
		More information you can find by link http://webdav.org/specs/rfc4918.html#rfc.section.9.4

		:param remote_path: the path to remote file for downloading.
		:param local_path: the path to save file locally.
		:param progress: progress function. Not supported now.
		"""
		urn = Urn(remote_path)
		if not self.check(urn.path()):
			return 0
		try:
			response = self.execute_request('download', urn.quote())
			return response
		except:
			return 0
	def upload_file(self, remote_path, local_rb_data, progress=None):
		"""Uploads file to remote path on WebDAV server. File should be 2Gb or less.
		More information you can find by link http://webdav.org/specs/rfc4918.html#METHOD_PUT

		:param remote_path: the path to uploading file on WebDAV server.
		:param local_path: the path to local file for uploading.
		:param progress: Progress function. Not supported now.
		"""
		urn = Urn(remote_path)
		if not self.check(urn.parent()):
			return 0
		try:
			self.execute_request(action='upload', path=urn.quote(), data=local_rb_data)
			return 1
		except:
			return 0
def jianguo_dav(rb_data,webdav_data,action='upload'):
	#上传或者下载,返回text
	options = {
		'webdav_hostname': "https://dav.jianguoyun.com/dav",
		'webdav_login': webdav_data[0],
		'webdav_password': webdav_data[1],
		'disable_check': True, #有的网盘不支持check功能
	}
	client = davclient(options)
		# 我选择用时间戳为备份文件命名
	name = 'jw/成绩记录.txt'
	try:
		# 写死的路径，第一个参数是网盘地址
		if action =='upload':
			r = client.upload_file(name,rb_data)
			if r:
				print('upload at ' + name)
			else:
				print('上传失败')
		elif action =='download':
			file = client.download_file(name)
			if file:
				#print(file.text.encode("iso-8859-1").decode(encoding="utf-8"))
				# 打印结果，之后会重定向到log
				print('download at ' + name)
				return file.text.encode("iso-8859-1").decode(encoding="utf-8")
			else:
				return 0
	except LocalResourceNotFound as exception:
		print('An error happen: LocalResourceNotFound ---'  + name)
		return 0

def send_email(email_user,receivers,subject='test',content='测试内容'):
	sender =email_user[0]
	passWord = email_user[1]
	mail_host = 'smtp.163.com'
	#receivers是邮件接收人，用列表保存，可以添加多个
	

	#设置email信息
	msg = MIMEMultipart()
	#邮件主题
	msg['Subject'] = subject#input(u'请输入邮件主题：')
	#发送方信息
	msg['From'] = sender
	#邮件正文是MIMEText:
	msg_content = content#input(u'请输入邮件主内容:')
	msg.attach(MIMEText(msg_content, 'html', 'utf-8'))

	#登录并发送邮件
	try:
		#QQsmtp服务器的端口号为465或587
		s = smtplib.SMTP_SSL(mail_host, 465)
		s.set_debuglevel(1)
		s.login(sender,passWord)
		#给receivers列表中的联系人逐个发送邮件
		for item in receivers:
			msg['To'] = to = item
			s.sendmail(sender,to,msg.as_string())
			print('Success!')
		s.quit()
		print ("All emails have been sent over!")
		return True
	except smtplib.SMTPException as e:
		print ("Falied,%s",e)
		return False

def check(email_user,username,password,email_,grade_,has_login=0):
	if not has_login:
		login = swjtu_jw_login.login(username,password)
		session = login.session
	else:
		session = has_login
	####查看成绩
	headers={
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
				'Accept-Encoding': 'gzip, deflate',
				'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
				'Cache-Control': 'max-age=0',
				'Connection': 'keep-alive',
				#'Cookie': `JSESSIONID=${Sid}; username=${username}`,//SESSIONID和学号
				'Host': 'jwc.swjtu.edu.cn',
				'Upgrade-Insecure-Requests': '1',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
			}


	chengji_url = 'http://jwc.swjtu.edu.cn/vatuu/StudentScoreInfoAction?setAction=studentScoreQuery&viewType=studentScore&orderType=submitDate&orderValue=desc'

	r = session.get(chengji_url,headers=headers)

	trs = re.findall(r'<tr>.*?</tr>',r.text.replace('\t','').replace('  ','').replace('\n',''))
	new = 0
	first =0
	if not grade_:
		first =1
	for tr in trs[5:]:
			tds = re.findall(r'<td >(.*?)</td>',tr)
			name = tds[2]
			total = ''.join(re.findall(r'\S',tds[5]))
			end = tds[6]
			mid = tds[7]
			cj_str ='科目： <b>'+name+'</b><br>总成绩： <b>'+total+'</b><br>期末成绩： <b>'+end+'</b><br>期中成绩： <b>'+mid+'</b><br>'
			#检查
			if first:
				#first
				grade_.append(cj_str)
			else:
				if cj_str not in grade_:
					send_email(email_user,receivers = [email_],subject='教务网成绩跟新提醒',content=cj_str)
					new = 1 # 有新的
					grade_.append(cj_str)

	if new or first:
		return grade_
	else: 
		return False
		
# #登录一次
# def login(user):
# 	for username,password,email_ in user:
# 		login = swjtu_jw_login.login(username,password)
# 		session = login.session
# 	return session


#main start

users  = os.environ['users']
webdav_data =  os.environ['web_dav'].split('#')#webdav 的账号#密码 
email_user =  os.environ['email_user'].split('#')#email的账号#密码 
users = [tuple(user.split(',')) for user in users.split('#')]
has_data = jianguo_dav(0,webdav_data,action='download')#dict or 0
if has_data:
	grade = eval(has_data)#grade
else:
	grade = {}
up = 0
for user in users:
	username,password,email_ = user
	print('开始检查')
	try:
		grade[username]
		need_upload =check(email_user,username,password,email_,grade[username])
	except:
		need_upload =check(email_user,username,password,email_,[])
	if need_upload:
		grade[username] = need_upload
		up =1#
if up:
	res = jianguo_dav(str(grade).encode(encoding="utf-8"),webdav_data,action='upload')
else:
	print('无跟新')