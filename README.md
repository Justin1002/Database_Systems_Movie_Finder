# Movie Finder
# Project by Justin Ly and Yakov Yuzhakov


## Getting started
### For the database (mySQL version 8.0.27) 
1. replace the file header `/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/` with the location of your local repository
2. run the command `mysql --local-infile -u [USERNAME] -p < loadData.sql in the server folder 
(You may have to enable --local-infile loading, otherwise place CSV files in the mySQL data directory)
3. Download source data [here](https://drive.google.com/file/d/1h8l4uKAdhWKiNVHd8vVyn1I3ReH8x0jl/view?usp=sharing) and extract zip folder in the `/server/` folder.

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

!['Main User Interface'](https://github.com/Justin1002/MovieFinder/blob/master/docs/Find%20a%20movie.gif?raw=true)

!['Add/Edit Reviews'](https://github.com/Justin1002/MovieFinder/blob/master/docs/Add%20and%20edit%20review.gif?raw=true)

!['Movie Reviews'](https://github.com/Justin1002/MovieFinder/blob/master/docs/Movie%20Reviews.gif?raw=true)
