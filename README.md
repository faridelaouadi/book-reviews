Background and Motivation
------

- This technologies used are : Python's Flask, Bootstrap and PostgreSQL for the database. I have had experience developing static frontend websites and decided to begin learning dynamic content generation and basically how to create full stack apps. I also created a rest API with this app so users can make GET requests using ISBN numbers and retrieve information like title, publish date and more. 


Current Progress
----------------
![](demo.gif)
Full video here: https://youtu.be/NpC8r8lJ-K8

How can i run this? 
-----

1) Set up the PostgreSQL database on a platform like heroku. 
2) Use a service like adminer to make the following tables
  a) USERS( username (pk) , password )
  b) BOOKS( isbn(pk), title, author, year )
  c) REVIEWS( isbn(fk), username(fk), stars, content ) 
3) Set up the database_url variable locally as an environment variable using the following command on linux

export DATABASE_URL=""--link to the database here--""

4) Pip install all the dependencies needed 
5) run import.py which will populate the books table in your database wuth 5000 entries from the books.csv file 
6) run the flask app like so:

export FLASK_APP=application.py
flask run 

7) to make use of the api, simply make a GET request to the url /api/{{insert isbn here}}
```
{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}
```

Things to do
------------
1) Encrypt passwords in the database
2) Add reading lists for each user 
3) Add user profiles and maybe a social networking aspect 
4) allow users to edit existing reviews 
5) Reading wish list which tracks price on amazon for discounts 

