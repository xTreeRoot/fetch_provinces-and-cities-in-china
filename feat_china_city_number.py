import requests
import pymysql
from bs4 import BeautifulSoup

# 创建数据库连接，并打开游标
conn = pymysql.connect(
    host='localhost',  # 数据库服务器地址
    port=3306,  # 端口号，默认为3306
    user='root',  # 用户名
    password='root',  # 密码
    database='city'  # 数据库名称
)
cursor = conn.cursor()

# 创建表，表名为 city，包含三个字段：id(自增长主键), city_name, district_name
create_table_sql = '''CREATE TABLE IF NOT EXISTS city (
                        id INT(11) PRIMARY KEY AUTO_INCREMENT,
                        city_name VARCHAR(255) NOT NULL,
                        city_code CHAR(6) NOT NULL,
                        district_name VARCHAR(255) NOT NULL,
                        district_code CHAR(6) NOT NULL
                    );'''
cursor.execute(create_table_sql)

# 替换为您需要爬取的URL
url = 'http://www.ip33.com/area_code.html'
response = requests.get(url)
html = response.content
soup = BeautifulSoup(html, 'html.parser')

# 查找class为"wrap"的标签  find_all找所有的标签
wrap_tags = soup.find_all(class_='ip')

# wrap_tags里面存放的是html代码
for tag in wrap_tags:
    # 获取h4标签文本内容，即城市名
    h4_tag = tag.find('h4')
    if not h4_tag:
        continue
    city_text = h4_tag.text
    city_name = city_text.split()[0]  # 如：北京
    city_code = city_text.split()[1]  # 如：11

    # 找到与h4同级的ul标签
    ul_tag = h4_tag.find_next_sibling('ul')
    if not ul_tag:
        continue

    # 获取ul标签里的所有li标签，包括市辖区和县
    li_tags = ul_tag.find_all('li')

    for li_tag in li_tags:
        # 获取li标签里的第一个h5标签，即市辖区或县
        h5 = li_tag.find('h5')

        # 如果找到了h5标签，则表示该li标签包含区或县信息
        if h5:
            district_name = h5.text
            # 找到该li标签下的所有具体区和县
            district_names = [x.text for x in li_tag.find_all('li')]
            for district in district_names:
                # 将数据插入到表中
                district_name = district.split()[0]  # 如：东城区
                district_code = district.split()[1]  # 如：110101
                print("城市：{}，城市代码：{}，区/县：{}，区/县代码：{}".format(city_name,
                                                                         city_code,
                                                                         district_name,
                                                                         district_code) )

                # 插入到表中
                insert_sql = "INSERT INTO city (city_name, city_code, district_name, district_code) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_sql, (city_name, city_code, district_name, district_code))

# 提交更改并关闭数据库连接
conn.commit()
cursor.close()
conn.close()
