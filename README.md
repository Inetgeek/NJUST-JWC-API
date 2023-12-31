# NJUST-JWC-API

> 南京理工大学教务处成绩及课表查询API

该项目诞生于实践类课程【移动应用开发】，本人负责提供教务处爬虫及整个业务流程交互规范设计，爬虫功能包含：

- 教务系统成绩信息
- 教务系统课程信息
- 教务处官网【学生通知】的通知爬取。

其中教务处通知代码不开源，但我提供了更新的API。爬虫部署到私有仓库的`Github Actions`工作流中，每天定时12:00及18:00对教务系统上的通知进行解析，若有更新，则会更新API里的内容。

> API地址（GET方法）

```python
http://cdn.inetgeek.cn/dl/notice.json
```

> 返回格式

```json
{
    "desc": "jwc",
    "data": [
        {
            "date": "2023-06-13",   //日期
            "title": "关于开展2022-2023学年春季学期学生网上评教工作的通知",
            "url": "https://jwc.njust.edu.cn/d9/2a/c1217a317738/page.htm"
        },
        {
            "date": "2023-06-13",   //日期
            "title": "2023年春季学期第19周考试日程安排",
            "url": "https://jwc.njust.edu.cn/d6/d9/c1217a317145/page.htm"
        }
    ]
}
```



### 运行

执行`python app.py`。



## 成绩及课程信息查询

> 使用说明

1. 代码采用Python编写，Python版本建议 &ge; 3.7。
2. 需要安装如下依赖：

```python
pip install flask
```

```python
pip install jsonify
```

```python
pip install ddddocr
```

或直接使用下列的方式安装相关依赖：
```python
pip install -r requirements.txt
```



3.接口采用教务处官网提供的地址进行登录，并没有从ehall站进入，因此**不保证代码一直有效**。若代码失效，则请二次开发`/njust/process.py`里的`jwc_login(uid, pwd)`函数相关逻辑及`/njust/config.py`里的`url_login`及`url_verify`参数进行适配即可，因为教务处网站的成绩查询及课程表查询页面结构一般不会改变，因此不需要修改其他任何内容。

### 成绩查询

> 接口（POST）

```python
/score
```

> 请求参数

```json
{
    "uid": "924104333355",  //学号
    "pwd": "Admin123"   //登录密码
}
```

> 返回值

```json
{
    "code": 200,    //返回状态码
    "data":[
        {
            "num": 1,   //序号
            "term": "2020-2021-1",  //开课学期
            "cid": "01078001",  //课程号
            "course": "图学基础与计算机绘图", //课程名称
            "socre": 91,    //成绩
            "credit": 2,    //学分
            "type": "必修"    //课程类型
        },
        {
            "num": 2,   //序号
            "term": "2021-2022-2",  //开课学期
            "cid": "14220701",  //课程号
            "course": "进阶英语（Ⅱ）",    //课程名称
            "socre": 80,    //成绩
            "credit": 2,    //学分
            "type": "必修"    //课程类型
        }
    ]
}
```

验证码是自动识别的，若验证码识别错误及密码错误则会登录失败。登录失败则返回：

```json
{
    "code": 401,
    "data": null
}
```

- `data`键里面是一个一维数组（Python里面叫列表），数组里面有多个对象（Python里面叫字典）组成。



### 课表查询

> 接口（POST）

```python
/course
```

> 请求参数

```json
{
    "uid": "924104333355",  //学号
    "pwd": "Admin123"   //登录密码
}
```

> 返回值

```json
{
    "code": 200,        //返回状态码
    "data": [
        {
            "num": "06022005",  //课程号
            "course": "操作系统",   //课程名称
            "teacher": "衷宜",    //教师
            "date": [10, 13],   //上课周次
            "time": [[1, 2, 3], [3, 6, 7]], //上课时间
            "credit": 2.5,  //学分
            "addr": "Ⅳ-A106",   //上课地点
            "type": "必修"    //课程类型
        },
        {
            "num": "06027002",  //课程号
            "course": "嵌入式系统",  //课程名称
            "teacher": "夏青元",   //教师
            "date": [10, 17],   //上课周次
            "time": [[2, 6, 7], [5, 2, 3]], //上课时间
            "credit": 2,    //学分
            "addr": "Ⅳ-B406",   //上课地点
            "type": "必修"    //课程类型
        }
    ]
}
```

- `data`键里面是一个一维数组（Python里面叫列表），数组里面有多个对象（Python里面叫字典）组成。

- `date`键里面是一个一维数组，第一个元素（a0）表示开始的周次，第二个元素（a1）表示结束的周次，**例**：`[10, 15]`表示第10周开课，第15周结课。

- `time`键里面是一个二维数组，里面可能存在多个数组（一般为1或2个），每个数组表示某一天的上课时间，若有2个数组，则表示该课在该周有2天需要上课。**例**：

    `[[1, 2, 3], [3, 6, 7]]`表示一周有2天要上该门课，其中的`[1, 2, 3]`表示周一的第2到3小节上该门课，`[3, 6, 7]`表示周三的第6-7小节上该门课。



### 注意

因为编写代码的时间很紧凑，因此对于课程表特殊情况代码做了特殊处理，下面举例说明代码的处理流程：

> 处理函数见`/njust/process.py`中的`course_merge()`。

假设课表上某一门课周一是第8周上课，周三是第2-5及第7周上课，则代码里将这些值中取最小值及最大值分别作为起始周次及结束周次，即该门课最后的返回值是`[2, 8]`，表示从第2周到第8周结束，有点不合实际，因此你可以在`/njust/process.py`中的`jwc_course(uid, pwd)`函数中的 <font style="color:red">[解析课程表上课周次]</font>进行二次开发。

**登录过程若返回401状态请多次尝试，有可能是验证码错误。若多次尝试均登陆失败则证明学号或登录密码错误。**



## 部署

1. 首先安装好Python环境（建议至少是3.7，不得低于Python3）及本文开头提到的依赖。

2. 使用`python app.py`运行程序。

3. 原代码默认使用8080端口作为API。

    - **本地运行**：按照1-2步配置好环境即可运行，本地对应的API：

        > 查询课表

        ```python
        http://127.0.0.1:8080/course
        ```

        > 查询成绩

        ```python
        http://127.0.0.1:8080/score
        ```

    - **云服务器部署**

        1. 首先在云服务器后台设置安全组策略。
        2. 入规则请开启`8080`端口，设置为：端口协议设置为`TCP:8080`、请求目标设置为`0.0.0.0/0`。
        3. 出规则请开启`8080`及`8090`端口，端口协议设置为`TCP:8080,8090`、请求目标设置为`0.0.0.0/0`。
        4. 在`app.py`所在目录执行如下指令即可挂在到后台运行，关闭控制台(terminal)不会终止运行。

        ```bash
        nohup python app.py >> app.log 2>&1
        ```

        5. 查看日志可使用下列指令：

        ```bash
        tail -f app.log
        ```

        6. 终止该接口步骤：1.使用`ps aux | grep "app.py"`找到该程序的进程pid，然后使用`kill -9 [pid]`进行终止即可。

        7. 云服务器对应的接口：

            > 查询课表

            ```python
            http://{your domain or your ip}:{your port}/course
            ```

            > 查询成绩

            ```python
            http://{your domain or your ip}:{your port}/score
            ```

            

4. 若想修改端口则修改`app.py`最后一行代码的`8080`即可，云服务器端修改完毕需要修改对应的组安全策略，<u>注意`8090`端口不能改动。</u>

-----------

<div align="center">Copyright&copy;2023 Colyn, All Rights Reserved.
