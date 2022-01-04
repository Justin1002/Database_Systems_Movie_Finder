from prompt_toolkit import prompt
from prettytable import PrettyTable


def searchByCastMember():
  
  answer = prompt("Enter the name of the actresses/actors you'd like to search by, separated by commas: ")
  
  if answer == '':
    return None, None
  
  names = [x.strip() for x in answer.split(',')]

  placeholder = ', '.join(['%s']* len(names))
  movieCastSQL = '''
  SELECT titleID FROM MovieCast
  INNER JOIN CastMembers USING(castID)
  INNER JOIN Movies USING(titleID)
  WHERE role IN ('actress','actor') 
  AND name IN ({}) 
  '''.format(placeholder)
  
  if len(names) > 1:  
    movieCastSQL += ' GROUP BY titleID HAVING COUNT(titleID) > 1'

  
  return movieCastSQL, tuple(names)


def searchByDirectors():
  answer = prompt('Enter the name of the directors, separated by commas: ')
  if answer == '':
    return None, None
  
  names = [x.strip() for x in answer.split(',')]
  
  placeholder = ', '.join(['%s']*len(names))
  movieDirectorSQL = '''
  SELECT titleID From MovieCast
  INNER JOIN CastMembers USING(castID)
  INNER JOIN Movies USING(titleID)
  WHERE role IN ('director')
  AND name IN ({})
  '''.format(placeholder)
  
  if len(names) > 1:
    movieDirectorSQL += ' GROUP BY titleID HAVING COUNT(titleID) > 1'
  
  
  return movieDirectorSQL, tuple(names)

def searchByYear():
  answer = prompt('Type > to find movies greater than or equal to year, Type < to find movies less than or equal to year, or = to find movies in that year: ')
  year = prompt("Type in the year: ")
  
  if answer == '' or year == '':
    return None, None
  
  year = year.strip()
  
  yearSQL = '''
  SELECT titleID FROM Movies WHERE releaseYear
  '''
  if answer == '>':
    yearSQL += ' >= %s'
  elif answer == '<':
    yearSQL += ' <= %s'
  elif answer == '=':
    yearSQL += ' = %s'
  else:
    print('I did not understand your command')
    return None, None
    
  
  return yearSQL, ("{}".format(year),)

def searchByDuration():
  answer = prompt('Type > to find movies greater than or equal duration, or < to find movies less than or equal to duration: ')
  duration = prompt("Type in duration in minutes: ")
  
  if answer == '' or duration == '':
    return None, None
  
  duration = duration.strip()
  
  durationSQL = '''
  SELECT titleID FROM Movies WHERE duration
  '''
  if answer == '>':
    durationSQL += ' >= %s'
  
  elif answer == '<':
    durationSQL += ' <= %s'
  
  else:
    print('I did not understand your command')
    return None, None
  
  return durationSQL, ("{}".format(duration),)

def searchByRating():
  answer = prompt('Type > to find movies greater than or equal to a rating, or < to find movies less than or equal to rating: ')
  rating = prompt('Type in rating (IE: 5.4): ')
  
  if answer == '' or rating == '':
    return None, None
  
  rating = rating.strip()
  
  ratingSQL = '''
  SELECT titleID FROM Movies WHERE averageImdbRating
  '''
  
  if answer == '>':
    ratingSQL += ' >= %s'
  
  elif answer == '<':
    ratingSQL += ' <= %s'
    
  else:
    print('I did not understand your command.')
    return None, None
  
  return ratingSQL, ("{}".format(rating),)

def searchByCountry():
  country = prompt('Please enter countries, separated by commas: ')
  
  if country == '':
    return None, None
  
  countries = [x.strip() for x in country.split(',')]
  placeholder = ', '.join(['%s']* len(countries))
  
  countrySQL = '''
  SELECT titleID FROM MovieCountry
  INNER JOIN Countries USING (countryID)
  WHERE countryName IN ({})
  '''.format(placeholder)
  
  return countrySQL, tuple(countries)

def searchByLanguage():
  language = prompt('Please enter languages, separated by commas: ')
  
  if language == '':
    return None, None
  
  languages = [x.strip() for x in language.split(',')]  
  placeholder = ', '.join(['%s']* len(languages))
  
  languageSQL = '''
  SELECT titleID From MovieLanguage
  INNER JOIN Language USING (languageID)
  WHERE languageName IN ({})
  '''.format(placeholder)
  
  return languageSQL, tuple(languages)

def searchByGenre():
  validGenres = ('Romance', 'Biography', 'Crime', 'Drama', 'History', 'Adventure', 'Fantasy', 'War', 'Mystery', 
                 'Horror', 'Western', 'Comedy', 'Family', 'Action', 'Sci-Fi', 'Thriller', 'Sport', 'Animation', 
                 'Musical', 'Music', 'Film-Noir', 'Adult', 'Documentary', 'Reality-TV', 'News')
  
  table = PrettyTable()
  table.field_names = ['Valid Genre']
  for item in validGenres:
    table.add_row([item])
  print(table)
    
  genre = prompt('Please enter genre combination, separated by commas: ')
  
  if genre == '':
    return None, None
  
  genres = [x.strip() for x in genre.split(',')]
  
  genreSQL = '''
  SELECT titleID From Movies WHERE
  '''
  
  for i, genre in enumerate(genres):
    if i == 0:
      genreSQL += ' find_in_set(%s,genre)'
    else:
      genreSQL += ' AND find_in_set(%s,genre)'
  
  return genreSQL, tuple(genres)

def searchByRTFresh():
  answer = prompt("This will limit movies with a fresh score >= 60% by top critics (Y/N): ")
  
  if answer == 'Y':
    #Movie is considered fresh when percentage of fresh reviews is greater than 60%, with more than 5 reviews
    freshSQL = '''
    SELECT RTLink, titleID, (sum(review_type = 1) / (sum(review_type = 1) + sum(review_type = 0))) as percentFresh
    FROM RottenTomatoesReviews INNER JOIN Movies USING (RTLink)
    WHERE top_critic = 1
    GROUP BY RTLink, titleID HAVING percentFresh >= 0.6 AND count(top_critic) > 5
    '''
    return freshSQL
  elif answer == 'N':
    return
  else:
    return

def searchByStreamingPlatform():
  while True:
    
    streamingSQL = '''
    SELECT titleID FROM Movies WHERE
    '''
    c = 0
    amazon = prompt('Must be on Amazon Prime? (Y/N): ')
    if amazon.upper() == 'Y':
      streamingSQL += ' onAmazonPrime = 1'
      c+= 1
    elif amazon.upper() == 'N':
      pass
    else:
      print('Invalid input: Please try again')
      continue
    
    hulu = prompt('Must be on Hulu? (Y/N): ')
    if hulu.upper() == 'Y':
      if c > 0:
        streamingSQL += ' AND'
      streamingSQL +=' onHulu = 1'
      c+= 1
    elif hulu.upper() == 'N':
      pass
    else:
      print('Invalid input: Please try again')
      continue
    
    dp = prompt('Must be on Disney Plus? (Y/N): ')
    if dp.upper() == 'Y':
      if c > 0:
        streamingSQL += ' AND'
      streamingSQL +=' onDisneyPlus = 1'
    elif dp.upper() == 'N':
      pass
    else:
      print('Invalid input: Please try again')
      continue
    
    netflix = prompt('Must be on Netflix? (Y/N): ')
    if netflix.upper() == 'Y':
      if c > 0:
        streamingSQL += ' AND'
      streamingSQL +=' onNetflix = 1'
    elif netflix.upper() == 'N':
      pass
    else:
      print('Invalid input: Please try again')
      continue
  
  
    if amazon.upper() == 'N' and hulu.upper() == 'N' and dp.upper() == 'N' and netflix.upper() == 'N':
      return
    
    return streamingSQL