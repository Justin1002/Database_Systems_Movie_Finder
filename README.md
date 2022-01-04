# Movie Finder



## Getting started
### For the database (mySQL version 8.0.27) 
1. replace the file header `/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/` with the location of your local repository
2. run the command `mysql --local-infile -u [USERNAME] -p < loadData.sql in the server folder 
(You may have to enable --local-infile loading, otherwise place CSV files in the mySQL data directory)


### For the client (Python version 3.7)
1. create a config.py file in the client/DB folder, and fill it in as follows with your relevant database information:

```
mysql = {
    "host":"YOUR HOST NAME",
    "user":"YOUR USER NAME",
    "database":"YOUR DB",
    "password":"YOUR PW"
}
```
2.  Install all requirements with the command:
```
pip install -r requirements.txt
```
3.  Run the main program in the client folder using `python3 main.py`

4. Run the unit tests in the client folder using `python3 -m unittest -b`

## Project Dependencies
```
prompt_toolkit==3.0.24
mysql_connector_repackaged==0.3.1
prettytable==2.4.0
```

## Application Demo

!['Main User Interface'](https://git.uwaterloo.ca/yyuzhako/movie-finder-project/-/raw/master/docs/Find%20a%20movie.gif)

!['Add/Edit Reviews'](https://git.uwaterloo.ca/yyuzhako/movie-finder-project/-/raw/master/docs/Add%20and%20edit%20review.gif)

!['Movie Reviews'](https://git.uwaterloo.ca/yyuzhako/movie-finder-project/-/raw/master/docs/Movie%20Reviews.gif)
