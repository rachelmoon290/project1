# CS-S33a Project 1: Weather.Info Website
This website allows visitors to register and login in order to search for their location information, including weather information. Then the users can check in, and also leave comments. Visitors can also get APIs from the website.

## import.py
This python program creates location table, and imports location information from zips.csv.

## create_data_table.py
This python program creates users and checkin table.

## application.py
This is the main web application program that takes care of backend processing of the website.

## layout.html
This is the basic layout html for all other html files. This website mainly uses bootstrap for styling.

## index.html
This is the homepage html for users who are not logged in. Users can either log in or sign up in this page.

## login.html
This is the login page.

## signup.html
This is the signup page.

## signupsuccess.html
If user correctly fills out all the parts of the signup form with a new ID, then this sign-up-success confirmation page comes out.

## usermain.html
If ID and password match, then user is logged in and can view the main page. In the main page, user can search for location by typing zipcode, name of city, or state.

## locations.html
This is a page where all the search results are shown in a table.

## location.html
If user chooses one location from the results from locations.html, then he/she can view details about the location in this page. The user can also view comments other users have left, and also check into the location.

## checkin_submission.html
If user checks in, then this page shows up, confirming that he or she has successfully checked into the location.

## error.html
This is an error page template for some errors that may take place while users are using the website.

## error2.html
This is an error page especially for the checkin_submission html error (when user submits more than one checkin at a same location), with a button that brings back to location.html, which requires a specific location_id.

## style.css
Although this website mainly implements bootstrap features for styling, this stylesheet specifies styles for some elements in html files.

## d79kdcuj6gsi9t.sql
This is the sql file of the database(users, location, checkin table) that the website requires in order to operate.

## zips.csv
This is the location database, with basic information about each location.

## requirements.txt
This is a list of package names that should be installed in order to run application.py.
