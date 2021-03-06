# -*- coding:utf-8 -*-
__author__ = '东方鹗'
__blog__ = 'http://www.os373.cn'

from models import session, Employee, Department, DeptEmp, DeptManager, Salary, Title
import operator
from sqlalchemy import func, and_, or_, text
from sqlalchemy.orm import aliased

'''===========================================联合查询实例==========================================='''

'''----------------------------------------------第一例-----------------------------------------------
    功能说明：
    查询主键为 10004 的员工的所有年薪，需 Employees，Salaries 两个表联合查询。
    结果是： 返回字段为 emp_no, birth_date, first_name, last_name, gender, hire_date, times, salary
'''

'''使用 sql 语句方式进行查询'''
sql = """
        SELECT
            emp.*, CONCAT_WS('--', s.from_date, s.to_date) AS 'times',
            s.salary
        FROM
            employees emp
        JOIN salaries s ON emp.emp_no = s.emp_no
        WHERE
            emp.emp_no = 10004
"""
sql_data = [(d.emp_no, d.birth_date, d.first_name, d.last_name, d.gender, d.hire_date, d.times, d.salary)
            for d in session.execute(sql)]

'''使用 sqlalchemy 方式进行查询'''
alchemy_data = session.query(Employee.emp_no, Employee.birth_date, Employee.first_name,
                  Employee.last_name, Employee.gender, Employee.hire_date,
                  func.concat_ws('--', Salary.from_date, Salary.to_date).label('times'), Salary.salary).\
    filter(Employee.emp_no==10004, Salary.emp_no==10004).all()

'''比较两个结果，应该是True'''
for d in zip(sql_data, alchemy_data):
    print(d)
print('第一例结果是：{}'.format(operator.eq(sql_data, alchemy_data)))

'''-------------------------------------------------------------------------------------------------'''

'''----------------------------------------------第二例-----------------------------------------------
    功能说明：
    查询主键为 10004 的员工的所有年薪，需 Employees，Salaries，Title 三个表联合查询。
    结果是： 返回字段为 emp_no, birth_date, first_name, last_name, gender, hire_date, 
    title(新增字段，需联表 Title), times， salary
'''

'''使用 sql 语句方式进行查询'''
sql = """
        SELECT
            emp.*, t.title,
            CONCAT_WS('--', s.from_date, s.to_date) AS 'times',
            s.salary
        FROM
            employees emp
        JOIN titles t ON emp.emp_no = t.emp_no
        JOIN salaries s ON emp.emp_no = s.emp_no
        WHERE
            emp.emp_no = 10004
        AND (
            s.from_date BETWEEN t.from_date
            AND t.to_date
        )
"""
sql_data = [(d.emp_no, d.birth_date, d.first_name, d.last_name, d.gender, d.hire_date, d.title, d.times, d.salary)
            for d in session.execute(sql)]

'''使用 sqlalchemy 方式进行查询'''
alchemy_data = session.query(Employee.emp_no, Employee.birth_date, Employee.first_name,
                                 Employee.last_name, Employee.gender, Employee.hire_date, Title.title,
                                 func.concat_ws('--', Salary.from_date, Salary.to_date).label('times'),
                                 Salary.salary).\
    filter(Employee.emp_no == 10004, Salary.emp_no == 10004, Title.emp_no == 10004,
           Salary.from_date.between(Title.from_date, Title.to_date)).all()

'''比较两个结果，应该是True'''
for d in zip(sql_data, alchemy_data):
    print(d)
print('第二例结果是：{}'.format(operator.eq(sql_data, alchemy_data)))

'''-------------------------------------------------------------------------------------------------'''

'''----------------------------------------------第三例-----------------------------------------------
    功能说明：
    查询主键为 10004, 10001, 10006, 10003 的四位员工在 1997-12-01 时期的年薪及上年年薪，
    需 Employees，Salaries，Title 三个表联合查询。
    结果是： 返回字段为 emp_no, birth_date, first_name, last_name, gender, hire_date, 
    title(新增字段，需联表 Title), from_date, to_date, salary, last_salary
    提示：该实例很复杂，重点如下：
        1、if else 三目运算符的使用。
        2、func.date_sub 的使用。
        3、text 可以使用原始的 sql 语句。
        4、对 salaries 表同时进行两次及以上查询，用到了 aliased。
        5、使用 IFNULL 函数。
'''

'''使用 sql 语句方式进行查询'''
sql = """
        SELECT
            emp.*, t.title,
            s.from_date,
            s.to_date,
            s.salary,
            IFNULL(
                (
                    SELECT
                        s.salary
                    FROM
                        salaries s
                    WHERE
                        s.emp_no = emp.emp_no
                    AND (
                        DATE_SUB(
                            DATE('1997-12-01'),
                            INTERVAL 1 YEAR
                        ) BETWEEN s.from_date
                        AND s.to_date
                    )
                ),
                0
            ) AS last_salary
        FROM
            employees emp
        JOIN titles t ON emp.emp_no = t.emp_no
        JOIN salaries s ON emp.emp_no = s.emp_no
        WHERE
            (
                emp.emp_no = 10004
                OR emp.emp_no = 10001
                OR emp.emp_no = 10006
                OR emp.emp_no = 10003
            )
        AND (
            DATE('1997-12-01') BETWEEN s.from_date
            AND s.to_date
        )
        AND (
            DATE('1997-12-01') BETWEEN t.from_date
            AND t.to_date
        )
        """
sql_data = [(d.emp_no, d.birth_date, d.first_name, d.last_name, d.gender, d.hire_date, d.title, d.from_date, d.to_date,
             d.salary, d.last_salary)
            for d in session.execute(sql)]

'''使用 sqlalchemy 方式进行查询'''

'''方法一：使用 if else 三目运算符'''
s1 = aliased(Salary)
s2 = aliased(Salary)
alchemy_data = session.query(Employee.emp_no, Employee.birth_date, Employee.first_name,
                                 Employee.last_name, Employee.gender, Employee.hire_date, Title.title,
                                 s1.from_date, s1.to_date, s1.salary, (0 if not
                                        session.query(s2.salary).filter(s2.emp_no==Employee.emp_no,
                                        func.date_sub(text("date('1997-12-01'), interval 1 year")).
                                        between(s2.from_date, s2.to_date))
                             else session.query(s2.salary).
        filter(s2.emp_no==Employee.emp_no, func.date_sub(text("date('1997-12-01'), interval 1 year")).
               between(s2.from_date, s2.to_date))).label("last_salary")).\
    filter(Employee.emp_no==s1.emp_no , Title.emp_no==s1.emp_no,
           or_(Employee.emp_no==10004,
               Employee.emp_no==10001,
               Employee.emp_no==10006,
               Employee.emp_no==10003),
           func.date('1997-12-01').between(s1.from_date, s1.to_date),
           func.date('1997-12-01').between(Title.from_date, Title.to_date)).all()

'''===============================以下是两种错误方法================================================'''
'''方法二：使用 IFNULL 函数，这是一种错误的方法，由于使用 aliased ，在 from 之后将会出现另一条 IFNULL 语句, 
数据本身会提示错误——“Every derived table must have its own alias”
s1 = aliased(Salary)
s2 = aliased(Salary)
alchemy_data = session.query(Employee.emp_no, Employee.birth_date, Employee.first_name,
                                 Employee.last_name, Employee.gender, Employee.hire_date, Title.title,
                                 s1.from_date, s1.to_date, s1.salary, func.IFNULL(
                                        session.query(s2.salary).filter(s2.emp_no==Employee.emp_no,
                                        func.date_sub(text("date('1997-12-01'), interval 1 year")).
                                        between(s2.from_date, s2.to_date)), 0).label("last_salary")).\
    filter(Employee.emp_no==s1.emp_no , Title.emp_no==s1.emp_no,
           or_(Employee.emp_no==10004,
               Employee.emp_no==10001,
               Employee.emp_no==10006,
               Employee.emp_no==10003),
           func.date('1997-12-01').between(s1.from_date, s1.to_date),
           func.date('1997-12-01').between(Title.from_date, Title.to_date)).all()
'''


'''方法三：使用 IFNULL 函数，这是一种错误的方法， sqlalchemy 本事不支持这种语法，出现错误提示——
别名为last_salary的字段的 “select 语句” “returned no FROM clauses due to auto-correlation;”
alchemy_data = session.query(Employee.emp_no, Employee.birth_date, Employee.first_name,
                                 Employee.last_name, Employee.gender, Employee.hire_date, Title.title,
                                 Salary.from_date, Salary.to_date, Salary.salary, func.IFNULL(
                                        session.query(Salary.salary).filter(Salary.emp_no==Employee.emp_no,
                                        func.date_sub(text("date('1997-12-01'), interval 1 year")).
                                        between(Salary.from_date, Salary.to_date)), 0).label("last_salary")).\
    filter(Employee.emp_no==Salary.emp_no , Title.emp_no==Salary.emp_no,
           or_(Employee.emp_no==10004,
               Employee.emp_no==10001,
               Employee.emp_no==10006,
               Employee.emp_no==10003),
           func.date('1997-12-01').between(Salary.from_date, Salary.to_date),
           func.date('1997-12-01').between(Title.from_date, Title.to_date)).all()
'''

'''比较两个结果，应该是True'''
for d in zip(sql_data, alchemy_data):
    print(d)
print('第三例结果是：{}'.format(operator.eq(sql_data, alchemy_data)))

'''-------------------------------------------------------------------------------------------------'''

'''----------------------------------------------第四例-----------------------------------------------
    功能说明：
    查询主键为 10001 的员工的当年年薪，上年年薪及差额，需对 salaries 表看做两个表进行联合查询。
    结果是： 返回字段为 emp_no, from_date, to_date, salary, last_salary(上年年薪), difference(差额)。
    提示：对 salaries 表同时进行两次及以上查询，用到了 aliased
'''

'''使用 sql 语句方式进行查询'''
sql = """
        SELECT
            s.emp_no,
            s.from_date,
            s.to_date,
            s.salary,
        
        IF (
            ISNULL(s1.salary),
            0,
            s1.salary
        ) AS last_salary,
         (
            s.salary -
            IF (
                ISNULL(s1.salary),
                0,
                s1.salary
            )
        ) AS difference
        FROM
            salaries s
        LEFT JOIN salaries s1 ON s.emp_no = s1.emp_no
        AND YEAR (s1.from_date) = YEAR (s.from_date) - 1
        WHERE
            s.emp_no = 10001
        """
sql_data = [(d.emp_no, d.from_date, d.to_date, d.salary, d.last_salary, d.difference)
            for d in session.execute(sql)]

'''使用 sqlalchemy 方式进行查询'''
s1 = aliased(Salary)
s2 = aliased(Salary)
alchemy_data = session.query(s1.emp_no, s1.from_date, s1.to_date, s1.salary,
                             func.IF(func.isnull(s2.salary), 0, s2.salary).label("last_salary"),
                             (s1.salary - (func.IF(func.isnull(s2.salary), 0, s2.salary))).label("difference")).\
    outerjoin(s2, and_(s2.emp_no==s1.emp_no, func.year(s2.from_date)==func.year(s1.from_date)-1)).\
    filter(s1.emp_no==10001).all()

'''比较两个结果，应该是True'''
for d in zip(sql_data, alchemy_data):
    print(d)
print('第四例结果是：{}'.format(operator.eq(sql_data, alchemy_data)))

'''-------------------------------------------------------------------------------------------------'''
session.commit()
session.close()
