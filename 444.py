import requests
from tabulate import tabulate
from prettytable import PrettyTable
from fake_useragent import UserAgent
import time

# 登录模块
def login(name, passwd):
    headers = {"User-Agent": UserAgent().random}
    while True:
        try:
            # 获取登录cookies
            r = requests.get("https://passport2.chaoxing.com/fanyalogin", headers=headers)
            cookies = dict(r.cookies)
            data = {
                "fid": "-1",
                "uname": name,
                "password": passwd,
                "refer": "https%3A%2F%2Fi.chaoxing.com",
                "t": "true",
                "forbidotherlogin": "0",
                "validate": "",
                "doubleFactorLogin": "0",
                "independentId": "0"
            }
            jsessionid = cookies["JSESSIONID"]
            r = requests.post("https://passport2.chaoxing.com/fanyalogin", headers=headers, data=data, cookies=cookies)
            cookies = dict(**{"JSESSIONID": jsessionid}, **r.cookies)
            r = requests.get("https://i.chaoxing.com/", headers=headers, cookies=cookies, allow_redirects=False)
            cookies = dict(**cookies, **{"source": ""})
            r = requests.get(f"https://i.chaoxing.com/base?t={int(time.time() * 1000)}", headers=headers,
                             cookies=cookies)
            cookies.pop("JSESSIONID")
            cookies = dict(**cookies, **{"spaceFid": "270"}, **{"spaceRoleId": ""})
            r = requests.get("https://mooc1-1.chaoxing.com/visit/interaction", headers=headers, cookies=cookies)
            cookies = dict(**cookies, **r.cookies)
            if '_uid' in cookies:
                return cookies
            else:
                print("账号或密码错误，请重新输入")
                return None
        except:
            continue

# 使用登录模块获取cookies
username = input("请输入用户名：")
password = input("请输入密码：")
cookies = login(username, password)

while cookies is None:
    username = input("请输入用户名：")
    password = input("请输入密码：")
    cookies = login(username, password)

url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1"

headers = {
  'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ChaoXingStudy/ChaoXingStudy_3_4.5.6_ios_phone_202007311550_41 (@Kalimdor)_7877438621606668303",
  'Accept-Encoding': "gzip",
  'Accept-Language': "zh-Hans-CN;q=1",
}

response = requests.get(url, headers=headers, cookies=cookies)
data = response.json()

course_list = data['channelList']

def sort_key(course):
    is_retired = course["content"]["isretire"]
    return is_retired

sorted_course_list = sorted(course_list, key=sort_key)

table = PrettyTable(["序号", "课程名称", "班级名称", "任课老师", "课程ID", "学生数", "结课状态"])

for index, course in enumerate(sorted_course_list, start=1):
    class_name = course['content']['name'][:10] if len(course['content']['name']) > 10 else course['content']['name']
    course_name = course['content'].get('course', {}).get('data', [{}])[0].get('name', 'Unknown')
    course_name = course_name[:10] if len(course_name) > 10 else course_name
    is_retired = course["content"]["isretire"]
    teacher_name = course['content'].get('course', {}).get('data', [{}])[0].get('teacherfactor', 'Unknown')
    teacher_name = teacher_name[:8] if len(teacher_name) > 8 else teacher_name
    course_id = course['content'].get('course', {}).get('data', [{}])[0].get('id', 'Unknown')
    student_count = course['content'].get('studentcount', 'Unknown')
    retired_status = "已结课" if is_retired == 1 else "未结课"
    
    table.add_row([index, course_name, class_name, teacher_name, course_id, student_count, retired_status])

print(table)

# 用户输入课程序号
course_index = int(input("请输入课程序号: ")) - 1
selected_course = sorted_course_list[course_index]
clazz_id = selected_course['content']['id']
course_id = selected_course['content'].get('course', {}).get('data', [{}])[0].get('id', 'Unknown')

url = 'https://stat2-ans.chaoxing.com/work-stastics/student-works'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip'
}

params = {
    'clazzid': clazz_id,  
    'courseid': course_id,  
    'page': '1',
    'pageSize': '200'
}

response = requests.get(url, headers=headers, cookies=cookies, params=params)
data = response.json()

data['data'].sort(key=lambda x: x['avg'], reverse=True)
for i, item in enumerate(data['data']):
    item['rank'] = i + 1

table_data = []
for item in data['data']:
    row = [
        item['rank'],  
        item['userName'],
        item['completeNum'],
        item['workSubmited'],
        item['workMarked'],
        item['avg'],
        item['max'],
        item['min']
    ]
    table_data.append(row)

table_format = 'pretty'  
table = tabulate(table_data, headers=['排名', '姓名', '作业总数', '提交数', '批阅数', '平均分', '最高分', '最低分'],
                 tablefmt=table_format)

print(table)
