-- all the tests should perform without errors
-- connect the database
use ece656_project

-- review the tables
show tables;

-- test Countries table
SHOW COLUMNS FROM Countries;
select * from Countries where countryName = 'Canada';

-- test Language table
SHOW COLUMNS FROM Language;
select * from Language where languageName = 'English';

-- test Movies table
SHOW COLUMNS FROM Movies;
select titleID, originalTitle, releaseYear, genre, duration, averageImdbRating from Movies where processedTitle like '%matrix%';

-- test CastMembers table
SHOW COLUMNS FROM CastMembers;
select * from CastMembers where name = 'Keanu Reeves' and birthCountry is not NULL;

-- test MovieCast table
SHOW COLUMNS FROM MovieCast;
select m.originalTitle, c.name, mc.role from MovieCast mc 
    inner join CastMembers c using(castID) 
    inner join Movies m using(titleID) 
    where c.name like '%Reeves%' and originalTitle like '%Matrix%';

-- test MovieCountry table
SHOW COLUMNS FROM MovieCountry;
select m.originalTitle, m.releaseYear, m.genre, c.countryName from MovieCountry mc 
    inner join Countries c using(countryID) 
    inner join Movies m using(titleID) 
    where m.originalTitle like '%Matrix%';

-- test MovieLanguage table
SHOW COLUMNS FROM MovieLanguage;
select m.originalTitle, m.releaseYear, m.genre, l.languageName from MovieLanguage ml 
    inner join Language l using(languageID) 
    inner join Movies m using(titleID) 
    where m.originalTitle like '%Matrix%';

-- test Users table
SHOW COLUMNS FROM Users;
select * from Users limit 3;

-- test MovieUser table
SHOW COLUMNS FROM MovieUser;
select m.originalTitle, m.releaseYear, m.genre, u.firstName, u.lastName, mu.viewDate, mu.rating from MovieUser mu 
    inner join Users u using(userID) 
    inner join Movies m using(titleID) 
    where m.originalTitle like '%Matrix%';

-- test RottenTomatoesReviews table
SHOW COLUMNS FROM RottenTomatoesReviews;
select * from RottenTomatoesReviews limit 3;

-- test movies/reviews join
select m.originalTitle, m.releaseYear, m.genre, rtr.critic_name, rtr.review_date, if(rtr.review_type = 1, 'Fresh', 'Rotten') as 'Review type' 
    from RottenTomatoesReviews rtr 
    inner join Movies m using(RTlink) 
    where m.originalTitle like '%Matrix%' and rtr.top_critic = 1 and year(rtr.review_date) > 2010;

-- test cross table constraint review_date >= releaseYear; return a error
insert into RottenTomatoesReviews(RTlink,review_date) Values ('m/0814255','1924-05-08');








