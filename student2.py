import pymysql
import getpass
from IPython.display import clear_output
import datetime
import time


class STUDENT:
    def __init__(self, ID, Name, Password, Address):
        self.ID = ID
        self.Name = Name
        self.Password = Password
        self.Address = Address

    def info(self):
        return (self.ID, self.Name, self.Password, self.Address)

def CheckDatabaseOpen(dbname):
    mydb = pymysql.connect("localhost","root","password")
    mycursor = mydb.cursor()
    mycursor.execute("SHOW DATABASES")
    DATABASE_EXIST = False
    for name in mycursor:
        if name[0] == dbname:
            mydb.close()
            DATABASE_EXIST = True
            return
    mydb.close()
    assert DATABASE_EXIST, "DATABASE does not exist!!!!"
    return

def Login(mycursor):
    while(1):
#         clear_output()
#         print("please enter your user name:")
        usr = input("please enter your user name:")
        pwd = getpass.getpass(prompt='Password: ')
        if mycursor.execute('select * from student where Name = %s and Password = %s',(usr,pwd)) > 0:
            stu_info = mycursor.fetchone()
            my_stu = STUDENT(*stu_info)
            clear_output()
            print('welcome to your student menu, %s' % usr)
            return my_stu
        else:
            clear_output()
            print("user name not exist or passowrd not correct!")

def EnrolledQuarter():
    now = datetime.datetime.now()
    if now.month in [9,10,11]:
        return now.year, "Q1"
    elif now.month in [12,1,2]:
        return now.year, "Q2"
    elif now.month in [3,4,5]:
        return now.year, "Q3"
    else:
        return now.year, "Q4"

def ShowStuMenu(mycursor,usr):
    year,quar = EnrolledQuarter()
    mycursor.execute('select transcript.UoSCode, unitofstudy.UoSName, \
                transcript.Year, transcript.Semester, unitofstudy.Credits\
                from student, transcript, unitofstudy\
                where student.id = transcript.Studid and \
                unitofstudy.UoSCode = transcript.UoSCode\
                and transcript.Semester = %s and transcript.Year=%s \
                and Grade is NULL and student.name = %s', (quar,year,usr) )
#     mycursor.execute('select transcript.UoSCode, unitofstudy.UoSName,\
#                 transcript.Year, transcript.Semester, unitofstudy.Credits \
#                 from student, transcript, unitofstudy \
#                 where student.id = transcript.Studid and transcript.Semester = %s \
#                 and transcript.Year=%s and Grade is NULL  and \
#                 unitofstudy.UoSCode = transcript.UoSCode \
#                 and student.name = %s', (quar,year,usr) )
    clear_output()
    result = mycursor.fetchall()
    print("%s is currently taking %d courses:" % (usr,len(result)))
#     print("Course NO \t Course Name \t Year \t Semester \t Credits \t Grade")
    for x in result:
        print(x[0],"\t",x[1].ljust(40),x[2],"\t",x[3],"\t",x[4])

def WaitForNext(current_state = 'login'):
    print('************************************************')
    if current_state == 'login':
        print('Input your option: \n Transcript \n Enroll \n Withdraw \n Personal Details \n Logout')
    elif current_state == 'Transcript':
        print('Input your option: \n Details \n Back')
    elif current_state == 'Details':
        print('Input your option: \n Back')
    elif current_state == 'Personal Details':
        print('Input your option: \n Edit \n Back')
    elif current_state == 'Enroll':
        print('Input your option: \n Select \n Back')
    elif current_state == 'Withdraw':
        print('Input your option: \n Select \n Back')

    option = input()
    return option

def ShowTranscript(mycursor,usr):
    mycursor.execute('select transcript.UoSCode, unitofstudy.UoSName, \
                transcript.Year, transcript.Semester, unitofstudy.Credits,\
                transcript.Grade\
                from student, transcript, unitofstudy\
                where student.id = transcript.Studid and \
                unitofstudy.UoSCode = transcript.UoSCode\
                and student.name = %s\
                order by transcript.Year', (usr) )
    clear_output()
    result = mycursor.fetchall()
    print("%s's transcript is shown below " % (usr))
#     print("Course NO \t Course Name \t Year \t Semester \t Credits \t Grade")
    for x in result:
        print(x[0],"\t",x[1].ljust(40),x[2],"\t",x[3],"\t",x[4],"\t",x[5])


def ShowCourseDetails(mycursor,usr):
#     print("Please input the course number:")
    course_num = input("Please input the course number:")
    mycursor.execute('select transcript.UoSCode, unitofstudy.UoSName,\
            transcript.Year, transcript.Semester, \
            uosoffering.Enrollment,  uosoffering.MaxEnrollment, \
            faculty.Name, transcript.Grade\
            from  unitofstudy, uosoffering, faculty, student, transcript\
            where faculty.Id = uosoffering.InstructorId and \
            transcript.UoSCode = unitofstudy.UoSCode \
            and unitofstudy.UoSCode = uosoffering.UoSCode and \
            uosoffering.Year = transcript.Year \
            and uosoffering.Semester = transcript.Semester and \
            student.id = transcript.Studid and \
            student.name = %s and transcript.UoSCode = %s', (usr,course_num) )
#     clear_output()
    result = mycursor.fetchall()
    if len(result):
        clear_output()
        print("detailed transcript is shown below ")
        for x in result:
            print("\nCourse NO.",x[0], "\nCourse Name.",x[1],\
                 "\nYear.", x[2], "\nSemester.",x[3], "\nEnrollment",x[4],\
                 "\nMaxEnrollment.",x[5],"\nInstructor Name.",x[6], "\nGrade.",x[7])
    else:
        print("wrong course number!!!")

def ShowPersonalDetails(mycursor,usr):
    mycursor.execute('select * from student where student.Name = %s', (usr))
    result = mycursor.fetchall()
    clear_output()
    print("%s's personal details are shown below:" % usr)
    print("ID \t NAME \t\t PASSWORD \t ADDRESS")
    for x in result:
        print(x[0],'\t',x[1],'\t',x[2],'\t',x[3])

def EditPersonalDetails(mycursor,usr):
    option = input("Input your option: \n password \n address\n")
    new_content = input("Input your new content:")
    while new_content == "":
        new_content = input("Content cannot be empty. Input your new content:")
    args = (new_content,option,usr,0)
    state = mycursor.callproc('updatepersonalinformation', args)
    mycursor.execute("SELECT @_updatepersonalinformation_3")
    result = mycursor.fetchall()
#     clear_output()
    if result[0][0] == 0:
        print("personal details updated successfully!!!")
    elif result[0][0] == 1:
        print("editing target is wrong!!!")
    else:
        print("transaction failed!!!")

def NextQuarter(curQuar, year):
    if curQuar == "Q1":
        return "Q2", year + 1
    if curQuar == 'Q2':
        return "Q3", year
    if curQuar == "Q3":
        return "Q4", year
    else:
        return "Q1", year

def ShowAvailableCourses(mycursor):
    year, quar = EnrolledQuarter()
    mycursor.execute('select * from lecture where year = %s and semester = %s', (year, quar))
    result1 = mycursor.fetchall()
    clear_output()
    quar, year = NextQuarter(quar,year)
    mycursor.execute('select * from lecture where year = %s and semester = %s', (year, quar))
    result2 = mycursor.fetchall()
    clear_output()
    print("Here are the courses in this quarter and next quarter:")
    for x in result1:
        print(x[0],"\t",x[1], "\t", x[2],"\t",x[3],"\t",x[4])
    for x in result2:
        print(x[0],"\t",x[1], "\t", x[2],"\t",x[3],"\t",x[4])

def SelectToEnroll(mycursor, usrID):
    cname = input("Please enter the course number you want to enroll:")
    year, quar = EnrolledQuarter()
    quar2, year2 = NextQuarter(quar, year)
    args = [cname, quar, year, usrID, 0, '']
    args2 = [cname, quar2, year2, usrID, 0, '']
    state = mycursor.callproc('enroll', args)
    mycursor.execute('Select @_enroll_0, @_enroll_1, @_enroll_2, @_enroll_3, @_enroll_4, @_enroll_5')
    result1 = mycursor.fetchall()
    mycursor.callproc('enroll', args2)
    mycursor.execute('Select @_enroll_0, @_enroll_1, @_enroll_2, @_enroll_3, @_enroll_4, @_enroll_5')
    result2 = mycursor.fetchall()
    if result1[0][4] == 1 or result2[0][4] == 1:
        print("Enroll succeed!")
    elif result1[0][4] == 0 or result2[0][4] == 0:
        print("Your have token this course!")
    elif result1[0][4] == 4 or result2[0][4] == 4:
        print("Enrollment exceeds Maximum Enrollment!")
    elif result1[0][4] == 7 or result2[0][4] == 7:
        print("Invalid course number!")
    else:
        mycursor.execute('select PrereqUoSCode from requires where UoSCode = %s', (cname))
        result = mycursor.fetchall()
        clear_output()
        print("Invalid course number or there are prerequisites for this course.")
        for x in result:
            print(x[0])
        # SelectToEnroll(mycursor, usrID)


def ShowCurrentCourses(mycursor, usrID):
    mycursor.execute('select UoSCode, Semester, Year from transcript where studid = %s and Grade is NULL', (usrID))
    result = mycursor.fetchall()
    clear_output()
    print("Here are the courses you are currently taking:")
    for x in result:
        print(x[0], "\t", x[1], "\t", x[2])

def SelectToWithdraw(mycursor, usrID):
    cname = input("Please enter the course number you want to withdraw:")
    args = [cname, usrID, 0]
    state = mycursor.callproc('drops', args)
    mycursor.execute('Select @_drops_0, @_drops_1, @_drops_2')
    result = mycursor.fetchall()
    if result[0][2] == 0:
        print("Withdraw succeed!")
        percentID = '1'
        mycursor.execute('select percent from enrollpercent where id = %s', (percentID))
        percent = mycursor.fetchall()
        if percent[0][0] < 0.5:
            print("Warnig: Enrollment percentage is below 50%")
    else:
        print("Invalid course number.")
        # SelectToWithdraw(mycursor, usrID)

def main():
    dbname = 'project3-nudb'

    CheckDatabaseOpen(dbname)

    mydb = pymysql.connect("localhost", "root", "password", dbname)
    mycursor = mydb.cursor()

    mycursor.execute('drop table if exists enrollpercent');
    mycursor.execute('create table enrollpercent (id int, percent float)')
    mycursor.execute('insert into enrollpercent values(1, 0.0)')
    states = ['waitforlogin', 'login', 'Transcript', 'Details', 'Personal Details']
    options = ['Transcript', 'Back']

    while (1):

        my_stu = Login(mycursor)
        ShowStuMenu(mycursor, my_stu.Name)

        current_state = 'login'
        option = WaitForNext(current_state)

        while option != "Logout":
            VALID_OPTION = False
            if option == "Transcript" and current_state == 'login':
                ShowTranscript(mycursor, my_stu.Name)
                current_state = 'Transcript'
                VALID_OPTION = True
            if option == "Back" and current_state == 'Transcript':
                ShowStuMenu(mycursor, my_stu.Name)
                current_state = 'login'
                VALID_OPTION = True
            if option == "Details" and current_state == 'Transcript':
                ShowCourseDetails(mycursor, my_stu.Name)
                current_state = 'Details'
                VALID_OPTION = True
            if option == "Back" and current_state == 'Details':
                ShowTranscript(mycursor, my_stu.Name)
                current_state = 'Transcript'
                VALID_OPTION = True
            if option == "Personal Details" and current_state == 'login':
                ShowPersonalDetails(mycursor, my_stu.Name)
                current_state = 'Personal Details'
                VALID_OPTION = True
            if option == "Edit" and current_state == 'Personal Details':
                EditPersonalDetails(mycursor, my_stu.Name)
                time.sleep(5)
                # mydb.commit()
                ShowPersonalDetails(mycursor, my_stu.Name)
                VALID_OPTION = True
            if option == "Back" and current_state == 'Personal Details':
                ShowStuMenu(mycursor, my_stu.Name)
                current_state = 'login'
                VALID_OPTION = True
            if option == "Enroll" and current_state == 'login':
                ShowAvailableCourses(mycursor)
                current_state = 'Enroll'
                VALID_OPTION = True
            if option == "Back" and current_state == 'Enroll':
                ShowStuMenu(mycursor, my_stu.Name)
                current_state = 'login'
                VALID_OPTION = True
            if option == "Select" and current_state == 'Enroll':
                SelectToEnroll(mycursor, my_stu.ID)
                time.sleep(5)
                ShowAvailableCourses(mycursor)

                VALID_OPTION = True
            if option == "Withdraw" and current_state == 'login':
                ShowCurrentCourses(mycursor, my_stu.ID)
                current_state = 'Withdraw'
                VALID_OPTION = True
            if option == "Select" and current_state == 'Withdraw':
                SelectToWithdraw(mycursor, my_stu.ID)
                time.sleep(5)
                ShowCurrentCourses(mycursor, my_stu.ID)
                VALID_OPTION = True
            if option == "Back" and current_state == 'Withdraw':
                ShowStuMenu(mycursor, my_stu.Name)
                current_state = 'login'
                VALID_OPTION = True
            if option == "exit" and current_state == 'login':
                mycursor.close()
                mydb.close()
                return
            if not VALID_OPTION:
                print("wrong option !!!!!")
            option = WaitForNext(current_state)
        del my_stu
        clear_output()
    mycursor.close()
    mydb.close()

if __name__ == "__main__":
    main()