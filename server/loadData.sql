-- set location for local rep 'movie-finder-project'
-- '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/';
-- unfortunately didn't find workaround to use path variable in sql yet

drop database if exists ece656_project; -- clean the database

CREATE DATABASE IF NOT EXISTS ece656_project;  -- create new database

use ece656_project;

source /home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/RelationalSchema.sql

-- load Countries data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/countries.csv' ignore into table Countries
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    ignore 1 rows
    (@id, @countryName)
    SET countryID = @id,
    countryName = NULLIF(@countryName, '')
    ;

-- index for future lookup functions
create index countryNameIndex on Countries(countryName);

-- load Languages data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/languages.csv' ignore into table Language
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    ignore 1 rows
    (@id, @language)
    SET languageID = @id,
    languageName = NULLIF(@language, '')
    ;

-- index for future lookup functions
create index languageNameIndex on Language(languageName);

-- load Cast data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/imdb/IMDb names.csv' ignore into table CastMembers
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    ignore 1 rows
    (@imdb_name_id, @name, @birth_name, @height, @bio, @birth_details, @date_of_birth, @place_of_birth, @death_details, @date_of_death, @lace_of_death, @reason_of_death, @pouses_string, @spouses, @divorces, @pouses_with_children, @children)
    SET castID = RIGHT(@imdb_name_id, 7),
    name = @name,
    dateOfBirth = NULLIF(@date_of_birth, ''),
    birthCountry = NULLIF(REGEXP_REPLACE(SUBSTRING_INDEX(@place_of_birth, ' ', -1), '[^A-Za-z ]', ''), '')
    ;

-- index for future lookup functions
create index nameIndex on CastMembers(name);

-- load Movies data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/imdb/IMDb movies.csv' ignore into table Movies
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    ignore 1 rows
    (@imdb_title_id, @title, @original_title, @year, @date_published, @genre, @duration, @country, @language, @director, @writer, @production_company, @actors, @description, @avg_vote, @votes)
    SET titleID = RIGHT(@imdb_title_id, 7),
    originalTitle = NULLIF(@original_title, ''),
    processedTitle = LOWER(REGEXP_REPLACE(@original_title, '[^0-9a-zA-Z]', '')),
    releaseYear = @year,
    genre = REGEXP_REPLACE(@genre, ' ', ''),
    duration = @duration,
    country = NULLIF(@country, ''),
    language = if(@language = '' or @language = 'None', NULL, @language),
    productionCompany = @production_company,
    description = @description,
    averageImdbRating = @avg_vote,
    ImdbVotes = @votes,
    onHulu = 0,
    onDisneyPlus = 0,
    onNetflix = 0,
    onAmazonPrime = 0
    ;

-- index for future lookup functions
create index processedTitleIndex on Movies(processedTitle);

-- load movie - cast relation data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/imdb/IMDb title_principals.csv' ignore into table MovieCast
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    ignore 1 rows
    (@imdb_title_id, @ordering, @imdb_name_id, @category, @job, @characters)
    SET titleID = RIGHT(@imdb_title_id, 7),
    castID = RIGHT(@imdb_name_id, 7),
    role = @category
    ;

-- normalize movie - country relation
INSERT INTO MovieCountry (titleID, countryID) 
    select m.titleID, c.countryID from Movies m join Countries c where m.country like CONCAT('%', c.countryName, '%');

ALTER TABLE Movies DROP COLUMN country;

-- normalize movie - language relation
INSERT INTO MovieLanguage (titleID, languageID) 
    select m.titleID, l.languageID from Movies m join Language l where m.language like CONCAT('%', l.languageName, '%');

ALTER TABLE Movies DROP COLUMN language;

-- load movie data from rotten tomatoes
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/rotten_tomatoes/rotten_tomatoes_movies.csv' ignore into table RottenTomatoesMovies
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    ignore 1 rows
    (@rotten_tomatoes_link, @movie_title, @movie_info, @critics_consensus, @content_rating, @genres, @directors, @authors, @actors, @original_release_date)
    SET RTlink = @rotten_tomatoes_link,
    movieTitle = @movie_title,
    processedTitle = LOWER(REGEXP_REPLACE(@movie_title, '[^0-9a-zA-Z]', '')),
    releaseYear = YEAR(@original_release_date)
    ;

-- index for future link between different databases
create index rtTitleIndex on RottenTomatoesMovies(processedTitle);

-- link IMDB and RT movies datasets using title and release year
-- due to some minor inconsistency in release year between databases approximately match +- 1 year
-- run the code for the movies with exact matching processedTitle
UPDATE Movies m left join RottenTomatoesMovies rtm on m.processedTitle = rtm.processedTitle
    SET m.RTlink = rtm.RTlink, rtm.titleID = m.titleID
    WHERE m.releaseYear <= rtm.releaseYear + 1 and m.releaseYear >= rtm.releaseYear - 1;

-- run the code for the movies with non exact matching Title (~2.5K rows), e.g. match 'One Night' with '1 night(One Night)'
-- exclude rows updated from previous query as running the code for the whole database takes huge amount of time (> 30 mins)
-- expected time for following query is around 7 mins
with m_temp as (select * from Movies WHERE RTlink is NULL),
    rt_temp as (select * from RottenTomatoesMovies where titleID is NULL),
    temp as (select m.titleID, rtm.RTlink from m_temp m inner join 
        rt_temp rtm 
        ON (rtm.processedTitle LIKE Concat('%',m.processedTitle) or rtm.processedTitle LIKE Concat(m.processedTitle,'%'))
        WHERE m.releaseYear <= rtm.releaseYear + 1 and m.releaseYear >= rtm.releaseYear - 1)
UPDATE Movies m inner join temp t using (titleID)
    SET m.RTlink = t.RTlink;

-- this code for the rest movies with missing release date
UPDATE Movies m right join RottenTomatoesMovies rtm on m.processedTitle = rtm.processedTitle
    SET m.RTlink = rtm.RTlink
    WHERE m.RTlink is NULL;

-- update indices in Movies table
ANALYZE table Movies;

-- load review data from rotten tomatoes
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/rotten_tomatoes/rotten_tomatoes_critic_reviews.csv' ignore into table RottenTomatoesReviews
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    ignore 1 rows
    (@rotten_tomatoes_link, @critic_name, @top_critic, @publisher_name, @review_type, @review_score, @review_date, @review_content)
    SET RTlink = @rotten_tomatoes_link,
    critic_name = NULLIF(@critic_name, ''),
    top_critic = if(@top_critic = 'TRUE', 1, 0),
    review_type = if(@review_type = 'Fresh', 1, 0),
    review_date = @review_date,
    review_content = NULLIF(@review_content, '')
    ;

-- load random user samples
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/users.csv' ignore into table Users
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    (@firstName, @lastName, @DOB, @country, @language)
    SET firstName = @firstName,
    lastName = @lastName,
    dateOfBirth = @DOB,
    age = TIMESTAMPDIFF(YEAR, @DOB, CURDATE()),
    country = (SELECT countryName from Countries where countryID = @country),
    preferredLanguage = (SELECT languageName from Language where languageID = @language)
    ;

-- randomly generated freaking user-movie relation, did not find a better way to create this one yet
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/movieuser.csv' ignore into table MovieUser
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\r\n'
    (@movie, @user, @date_time, @rating, @review)
    SET titleID = @movie,
    userID = @user,
    dateTime = @date_time,
    rating = @rating,
    reviewContent = @review
    ;

-- load Amazon Prime data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/streaming_platforms/amazon_prime_titles.csv' ignore into table tempStreamData
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\ns'
    ignore 1 rows
    (@show_id, @type, @title, @director, @cast, @country, @date_added, @release_year)
    SET title = LOWER(REGEXP_REPLACE(@title, '[^0-9a-zA-Z]', '')),
    releaseYear = NULLIF(@release_year, '')
    ;

UPDATE Movies m inner join tempStreamData t on m.processedTitle = t.title
    SET m.onAmazonPrime = 1 
    WHERE m.releaseYear <= t.releaseYear + 1 and m.releaseYear >= t.releaseYear - 1;

delete from tempStreamData;


-- load Disney Plus data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/streaming_platforms/disney_plus_titles.csv' ignore into table tempStreamData
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\ns'
    ignore 1 rows
    (@show_id, @type, @title, @director, @cast, @country, @date_added, @release_year)
    SET title = LOWER(REGEXP_REPLACE(@title, '[^0-9a-zA-Z]', '')),
    releaseYear = NULLIF(@release_year, '')
    ;

UPDATE Movies m inner join tempStreamData t on m.processedTitle = t.title
    SET m.onDisneyPlus = 1 
    WHERE m.releaseYear <= t.releaseYear + 1 and m.releaseYear >= t.releaseYear - 1;

delete from tempStreamData;


-- load Hulu data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/streaming_platforms/hulu_titles.csv' ignore into table tempStreamData
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\ns'
    ignore 1 rows
    (@show_id, @type, @title, @director, @cast, @country, @date_added, @release_year)
    SET title = LOWER(REGEXP_REPLACE(@title, '[^0-9a-zA-Z]', '')),
    releaseYear = NULLIF(@release_year, '')
    ;

UPDATE Movies m inner join tempStreamData t on m.processedTitle = t.title
    SET m.onHulu = 1 
    WHERE m.releaseYear <= t.releaseYear + 1 and m.releaseYear >= t.releaseYear - 1;

delete from tempStreamData;


-- load Netflix data
load data local infile '/home/justin1002/Desktop/University of Waterloo/Semester 1/ECE 656/Project/movie-finder-project/server/source_data/streaming_platforms/netflix_titles.csv' ignore into table tempStreamData
    fields terminated by ','
    enclosed by '"'
    lines terminated by '\ns'
    ignore 1 rows
    (@show_id, @type, @title, @director, @cast, @country, @date_added, @release_year)
    SET title = LOWER(REGEXP_REPLACE(@title, '[^0-9a-zA-Z]', '')),
    releaseYear = NULLIF(@release_year, '')
    ;

UPDATE Movies m inner join tempStreamData t on m.processedTitle = t.title
    SET m.onNetflix = 1 
    WHERE m.releaseYear <= t.releaseYear + 1 and m.releaseYear >= t.releaseYear - 1;

drop table tempStreamData;

drop table if exists RottenTomatoesMovies;

-- add trigger preventing Year(reviewDate) < releaseYear
drop trigger if exists dateReview;

delimiter //
CREATE TRIGGER dateReview BEFORE INSERT ON RottenTomatoesReviews
FOR EACH ROW
    IF YEAR(new.review_date) < (SELECT m.releaseYear from Movies m
        where m.RTlink = new.RTlink)
    THEN SIGNAL SQLSTATE '50001' SET MESSAGE_TEXT = 'Review must be written after movie release year.';
    END IF; //
delimiter ;