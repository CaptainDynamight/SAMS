# Student Attendance Management System

Student Attendance Management System (S.A.M.S) is a web application developed for maintaining the daily attendance of students. Previously, the institutions relied heavily on paper records. The project uses a database to keep a record and uses it while generating a report for an individual student. The administrator manages the profiles and student attendance. The faculties can directly access the progress of an individual through a secure online interface. 

This system will help in evaluating attendance eligibility criteria of a student by default is set to be 85% and could be varied by the admin. The faculty can also send messages to parents or guardians about student performance and attendance by shortlisting the students. Hence the communication is facilitated with parents and faculty. The SMS sent to the mobile number of the student's guardian indicating the absence of the student.

You can preview the whole project at **https://project-sams.herokuapp.com/**

(Note : Testing Account Credentials)

```username : fcs05```

```password : passcs05```

## 🚀 Installation :

### ➖ Requirements

To be able to successfully run this web application there are few requirements that have to be satisfied and these include :

- Python 3.7 or higher
  which you can obtain [here](https://www.python.org/downloads/).

- Get all dependencies using

  ```
  pip install -r requirements.txt
  ```

- An SMS API, here we have used the API provided by [160by2](https://www.160by2.com/) (Optional).

### ➖ Instructions

- Clone the repo or fork it.

- Here you should be able to locate **manage.py** now its time to generate necessary migrations since models are added

  ```
  python manage.py makemigrations
  ```

- A migration file will be created that we have to apply it to our database using

  ```
  python manage.py migrate
  ```

- To create an admin user account that has control over everything on the site. Go back to the command line, type

  ```
  python manage.py createsuperuser
  ```

- Now you can start the local web server using

  ```
  python manage.py runserver
  ```

- Type the address

  **http://127.0.0.1:8000/admin/** to access the admin panel

  **http://127.0.0.1:8000/** to access the home page


## ❗ Bugs

- Return to home page after admin authentication raises 'Index Error'
