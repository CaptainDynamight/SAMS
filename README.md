# Student-Attendance-Management-System

Student Attendance Management System (S.A.M.S) is a web application developed for daily attendance of students. Previously, the institutions relied heavily on paper records. The project makes use of database in order to keep a record of attendance and is used while generating a report for individual student. The system is fully controlled by administrator who manages staff’s profile, student information and student attendance. The faculties are able to directly access all aspects of the student’s progress through a secure online interface. After the class has been finished, the lecturer can view the student’s attendance that has been saved in the database.

This system will also help in evaluating attendance eligibility criteria of a student which is by default set to be 85% and could be changed by the user. The faculty can also send messages to parents or guardians about the student performance and attendance by short listing the students. Hence, here communication is made easier with parents and faculty. The messages can be sent through SMS to the mobile number of the student's guardian.

You can experience the whole project at **https://project-sams.herokuapp.com/**

## Setup Guide

### Requirements

To be able to successfully run this web application there are few reuirements that have to be satisfied and these include :

- Python 3.7 or higher
  which you can obtain [here](https://www.python.org/downloads/).

- Django using

  ```
  pip install Django
  ```

- An SMS API, here we have used the API provided by [160by2](https://www.160by2.com/) (Optional).

### Instructions

- Clone the repo or fork it.

- Move into **Student_Management_System**.

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
