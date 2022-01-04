-- This file contains all the queries for creation of tables/entities/relations

-- Clean the database

drop table if exists Countries;
drop table if exists Language;
drop table if exists CastMembers;
drop table if exists Movies;
drop table if exists MovieCast;
drop table if exists MovieCountry;
drop table if exists MovieLanguage;
drop table if exists RottenTomatoesMovies;
drop table if exists RottenTomatoesReviews;
drop table if exists Users;
drop table if exists MovieUser;
drop table if exists tempStreamData;
drop TRIGGER if exists dateReview;


-- Create required tables

create table Countries (
    countryID int primary key,
    countryName CHAR(50) UNIQUE
);

create table Language (
    languageID int primary key,
    languageName CHAR(40) UNIQUE
);

create table CastMembers (
    castID int primary key,
    name CHAR(40) NOT NULL,
    dateOfBirth date,
    birthCountry CHAR(40),
    FOREIGN KEY (birthCountry)
    REFERENCES Countries(countryName)
);

create table Movies (
    titleID int primary key,
    originalTitle CHAR(80) NOT NULL,
    processedTitle CHAR(80),
    releaseYear int,
    genre SET('Romance', 'Biography', 'Crime', 'Drama', 'History', 'Adventure', 'Fantasy', 'War', 'Mystery', 'Horror', 'Western', 'Comedy', 'Family', 'Action', 'Sci-Fi', 'Thriller', 'Sport', 'Animation', 'Musical', 'Music', 'Film-Noir', 'Adult', 'Documentary', 'Reality-TV', 'News'),
    duration int,
    country char(40), -- for future normalization
    language char(40), -- for future normalization
    productionCompany CHAR(80),
    description varchar(255),
    averageImdbRating DECIMAL(2,1),
    RTlink char(80),
    ImdbVotes int,
    onHulu TINYINT,
    onDisneyPlus TINYINT,
    onNetflix TINYINT,
    onAmazonPrime TINYINT,
    CHECK (duration >= 0),
    CHECK (averageImdbRating >= 0 and averageImdbRating <= 10)
);

-- index for RTlink to serve as a foreign key
create index RTlinkIndex on Movies(RTlink);

create table MovieCast (
    titleID int,
    castID int,
    role ENUM('actress', 'actor', 'director', 'producer', 'composer', 'cinematographer', 'writer', 'production_designer', 'editor', 'archive_footage', 'self', 'archive_sound') not null,
    PRIMARY KEY (titleID,castID),
    FOREIGN KEY (titleID)
    REFERENCES Movies(titleID),
    FOREIGN KEY (castID)
    REFERENCES CastMembers(castID)
);

create table MovieCountry (
    titleID int,
    countryID int,
    PRIMARY KEY (titleID,countryID),
    FOREIGN KEY (titleID)
    REFERENCES Movies(titleID),
    FOREIGN KEY (countryID)
    REFERENCES Countries(countryID)
);

create table MovieLanguage (
    titleID int,
    languageID int,
    PRIMARY KEY (titleID,languageID),
    FOREIGN KEY (titleID)
    REFERENCES Movies(titleID),
    FOREIGN KEY (languageID)
    REFERENCES Language(languageID)
);

create table RottenTomatoesMovies (
    RTlink char(80) PRIMARY KEY,
    movieTitle char(80) NOT NULL,
    processedTitle char(80),
    releaseYear int,
    titleID int
);

create table RottenTomatoesReviews (
    reviewID int primary key AUTO_INCREMENT,
    RTlink char(80) NOT NULL,
    critic_name char(20),
    top_critic TINYINT,
    review_type TINYINT,
    review_date date,
    review_content varchar(255),
    FOREIGN KEY (RTlink)
    REFERENCES Movies(RTlink)
);

create table Users (
    userID int primary key AUTO_INCREMENT,
    firstName char(20),
    lastName char(20),
    dateOfBirth DATE NOT NULL,
    age int NOT NULL,
    country CHAR(40) NOT NULL,
    preferredLanguage CHAR(40) NOT NULL,
    occupation char(30),
    FOREIGN KEY (country)
    REFERENCES Countries(countryName),
    FOREIGN KEY (preferredLanguage)
    REFERENCES Language(languageName),
    CHECK (age > 17),
    CHECK (country <> 'North Korea' or 'Syria')
);

create table MovieUser (
    titleID int,
    userID int,
    dateTime DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    rating DECIMAL(2,0),
    reviewContent varchar(255),
    PRIMARY KEY (titleID,userID),
    FOREIGN KEY (titleID)
    REFERENCES Movies(titleID),
    FOREIGN KEY (userID)
    REFERENCES Users(userID),
    CHECK (rating >= 0)
);

-- temp table to load stream platforms data to the Movies table
create table tempStreamData (
    title char(80),
    releaseYear int,
    PRIMARY KEY (title,releaseYear)
);
