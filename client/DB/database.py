import mysql.connector as con
from .config import mysql as cfg
from prompt_toolkit import prompt
from prettytable import PrettyTable
import sys
from .movie_rec import *
from .helpers import *

def initializeConnection():
  
  try:
    print('Checking Connection...')
    db = con.connect(
    host= cfg["host"],
    user=cfg["user"],
    database=cfg["database"],
    password=cfg["password"]
    )
    
    if db.is_connected():
      db_Info = db.get_server_info()
      print("Connected to MySQL Server Version", db_Info)
      return db
  
  except con.Error as err:
    print(err)  
  except:
    print("Error connecting to MySQL Server, Make sure the MySQL Server is running and connection parameters are correct, then try again!")
    print("Exiting!")
    sys.exit()


def confirmMovie(db):
  while True:
    curs = db.cursor()
    answer=prompt('Please enter a movie name: ')
    #convert answer to processedtitle format (no punctuation, spaces)
    answer = ''.join(char for char in answer if char.isalnum())
    grab_movie_sql = """SELECT titleID, originalTitle, releaseYear FROM Movies WHERE processedTitle LIKE %s;"""
    answer = '%' + answer + '%'
    curs.execute(grab_movie_sql, (answer, ))
    matching_data = curs.fetchall()
    
    if len(matching_data) == 0:
      print('Movie could not be found, please try again.')
      break

    table = PrettyTable()
    table.field_names = ["#","TitleID","Title","Release Year"]
    
    for i,row in enumerate(matching_data):
      table.add_row([i+1,row[0],row[1],row[2]])
    print(table)
    
    movie_to_select = prompt("Please confirm the movie you'd like to review by entering the row number: ")
    
    if movie_to_select.isdigit() == False or int(movie_to_select) > len(matching_data):
      print('Invalid input, please try again')
      break
    
    matching_row = matching_data[int(movie_to_select) - 1]
    
    return matching_row

def findMovieRecommendations(db):
  
  menu_options = {
  1: 'By cast members',
  2: 'By director',
  3: 'By year',
  4: 'By duration',
  5: 'IMDB rating',
  6: 'Country', 
  7: 'Languages',
  8: 'Genre',
  9: 'Streaming Platforms',
  10:'Critically acclaimed on Rotten Tomatoes',
  11: 'Search',
  12: 'Exit'
  }
   
  while True:
    try:
      curs = db.cursor()
      
      for key in menu_options.keys():
        print(key, '---', menu_options[key])
      print()
      
      answer = prompt('Please select an option: ')
      
      if answer == '1':
        movieCastSQL, castNames = searchByCastMember()
      elif answer == '2':
        movieDirectorSQL, directorNames = searchByDirectors()
      elif answer == '3':
        yearSQL, year = searchByYear()
      elif answer == '4':
        durationSQL, duration = searchByDuration()
      elif answer == '5':
        ratingSQL, rating = searchByRating()
      elif answer == '6':
        countrySQL, country = searchByCountry()
      elif answer == '7':
        languageSQL, languages = searchByLanguage()
      elif answer == '8':
        genreSQL, genres = searchByGenre()
      elif answer == '9':
        streamingSQL = searchByStreamingPlatform()
      elif answer == '10':
        freshSQL = searchByRTFresh()
      elif answer == '12':
        print()
        break
      elif answer == '11':
        
        def find_movie_sql(offset,combined_tuple, count):
          baseSQL = 'WITH '
          
          if "movieCastSQL" in locals():
            combined_tuple += castNames
            count += 1
            baseSQL += 'A as ({})'.format(movieCastSQL)
          
          if "movieDirectorSQL" in locals():
            combined_tuple += directorNames
            if count > 0:
              baseSQL += ','
            baseSQL += 'B as ({})'.format(movieDirectorSQL)
            count += 1
          
          if "yearSQL" in locals():
            combined_tuple += year
            if count > 0:
              baseSQL += ','
            baseSQL += 'C as ({})'.format(yearSQL)
            count += 1
          
          if "durationSQL" in locals():
            combined_tuple += duration
            if count > 0:
              baseSQL += ','
            baseSQL += 'D as ({})'.format(durationSQL)
            count += 1
          
          if "ratingSQL" in locals():
            combined_tuple += rating
            if count > 0:
              baseSQL += ','
            baseSQL += 'E as ({})'.format(ratingSQL)
            count += 1
          
          if "countrySQL" in locals():
            combined_tuple += country
            if count > 0:
              baseSQL += ','
            baseSQL += 'F as ({})'.format(countrySQL)
            count += 1
          
          if "languageSQL" in locals():
            combined_tuple += languages
            if count > 0:
              baseSQL += ','
            baseSQL += 'G as ({})'.format(languageSQL)
            count += 1
          
          if "genreSQL" in locals():
            combined_tuple += genres
            if count > 0:
              baseSQL += ','
            baseSQL += 'H as ({})'.format(genreSQL)
            count += 1
          
          if "streamingSQL" in locals():
            if count > 0:
              baseSQL += ','
            baseSQL += 'I as ({})'.format(streamingSQL)
            count += 1
            
          if "freshSQL" in locals():
            if count > 0:
              baseSQL +=','
            baseSQL += 'J as ({})'.format(freshSQL)
            count += 1
           
          baseSQL += ''' SELECT originalTitle, releaseYear, genre, duration, 
          averageImdbRating, ImdbVotes, onHulu, onDisneyPlus, 
          onAmazonPrime, onNetflix FROM Movies'''
          
          if "movieCastSQL" in locals():
              baseSQL += ' INNER JOIN A USING (titleID)'
          
          if "movieDirectorSQL" in locals():
            baseSQL += ' INNER JOIN B USING (titleID)'
          
          if "yearSQL" in locals():
            baseSQL += ' INNER JOIN C USING (titleID)'
          
          if "durationSQL" in locals():
            baseSQL += ' INNER JOIN D USING (titleID)'
          
          if "ratingSQL" in locals():
            baseSQL += ' INNER JOIN E USING (titleID)'
          
          if "countrySQL" in locals():
            baseSQL += ' INNER JOIN F USING (titleID)'
          
          if "languageSQL" in locals():
            baseSQL += ' INNER JOIN G USING (titleID)'
          
          if "genreSQL" in locals():
            baseSQL += ' INNER JOIN H USING (titleID)'
          
          if "streamingSQL" in locals():
            baseSQL += ' INNER JOIN I USING (titleID)'
          
          if "freshSQL" in locals():
            baseSQL += ' INNER JOIN J USING (titleID)'
            
          baseSQL += f' LIMIT 10 OFFSET {offset};'
          
          return baseSQL, combined_tuple
      
        
        #Quick way to check if search is executed right away without parameters
        if len(locals()) <= 6:
          print('No parameters specified.')
          print()
          continue
        
        read_more = True
        offset = 0
        
        ##Fetch data, ten rows at a time
        while read_more:
          combined_tuple = tuple()
          count = 0
          baseSQL, combined_tuple = find_movie_sql(offset, combined_tuple, count)
          curs.execute(baseSQL, combined_tuple)
          data = curs.fetchall()
          
          if len(data) == 0:
            print('No movies found.')
            print()
            break
          
          table = PrettyTable()
          table.field_names =['Title', 'Year', 'Genres', 'Duration', 'Average IMDB Rating', 'IMDB Votes', 'on Hulu', 'on Disney Plus', 'on Amazon Prime', 'on Netflix']
          table.align['Description'] = 'l'
          for row in data:
            on_hulu = 'Y'
            on_prime = 'Y'
            on_dp = 'Y'
            on_netflix = 'Y'
            if row[6] == 0:
              on_hulu = 'N'
            if row[7] == 0:
              on_dp = 'N'
            if row[8] == 0:
              on_prime = 'N'
            if row[9] == 0:
              on_netflix = 'N'
            
            table.add_row([row[0],row[1],row[2],row[3],row[4], row[5], on_hulu, on_dp, on_prime, on_netflix])

          print(table)
          print()

          if len(data) < 10:
            break
        
          read = prompt('Read more? (Y/N):')
          if read == 'Y':
            offset += 10
            continue
          elif read == 'N':
            break
          else:
            print('Option not understood.')
            continue
        
        choice = prompt("Type 1 to go back to main menu or 2 to exit the program: ")
        
        if optionComplete(choice):
          break
        
        sys.exit()
        
      else:
        print('I did not understand your choice, please input a number from 1-10.')
    except con.Error as error:
      print("Failed to get movie recommendation: {}".format(error))
    
      

def getMovieReviews(db):
  while True:
    try:
      matching_row = confirmMovie(db)
      curs = db.cursor()
      
      if matching_row == None:
        continue
      
      def construct_rt_reviews_sql(matching_row, offset = 0):
        return f'''
        SELECT critic_name, top_critic, review_type, review_date, review_content FROM RottenTomatoesReviews 
        WHERE RTlink = (SELECT RTlink FROM Movies WHERE titleID='{matching_row[0]}') LIMIT 10 OFFSET {offset};
        '''
      
      read_more = True
      offset = 0
      
      #Fetch data 10 rows at a time
      while read_more:    
        find_rt_reviews_sql = construct_rt_reviews_sql(matching_row,offset)
        curs.execute(find_rt_reviews_sql)
        data = curs.fetchall()
        
        if len(data) == 0:
          raise Exception

        table = PrettyTable()
        table.field_names = ['Critic Name', 'Top Critic', 'Review Type', 'Review Date', 'Review Content']
        table.align['Review Content'] = 'l'
        for row in data:
          top_critic = 'Y'
          review_type = 'Fresh'
          if row[1] == 0:
            top_critic = 'N'
          if row[2] == 0:
            review_type = 'Rotten'
          table.add_row([row[0],top_critic,review_type,row[3], wrapr(row[4])])

        print(table)
        
        #Check if data is less than 10, then no more read more option
        if len(data) < 10:
          break
        
        read = prompt('Read more? (Y/N):')
        if read == 'Y':
          offset += 10
          continue
        elif read == 'N':
          break
        else:
          print('Option not understood.')
          continue
      
      choice = prompt("Type 1 to go back to main menu or 2 to exit the program: ")
      
      if optionComplete(choice):
        break
      
      sys.exit()
      
    except Exception:
      print('No reviews found.\n')
      break
      
    except con.Error as error:
      print("Failed to get movie review: {}".format(error))
      print()
      return

def checkMovieDetails(db):
  while True:
    try:
      matching_row = confirmMovie(db)
      curs = db.cursor()
      
      if matching_row == None:
        continue
      
      find_movie_details_sql = f'''SELECT originalTitle, releaseYear, genre, duration, averageImdbRating,
                                   ImdbVotes, onNetflix, onHulu, onDisneyPlus, onAmazonPrime, productionCompany, description
                                   FROM Movies where titleID = {matching_row[0]}'''
      
      curs.execute(find_movie_details_sql)
      
      data = curs.fetchall()
    
      table = PrettyTable()
      table.field_names =['Title', 'Year', 'Genres', 'Duration', 'Average IMDB Rating', 'IMDB Votes', 'on Hulu', 'on Disney Plus', 'on Amazon Prime', 'on Netflix', 'Production Company', 'Description']
      table.align['Description'] = 'l'
      for row in data:
        on_netflix = 'Y'
        on_hulu = 'Y'
        on_prime = 'Y'
        on_dp = 'Y'
        if row[6] == 0:
          on_hulu = 'N'
        if row[7] == 0:
          on_dp = 'N'
        if row[8] == 0:
          on_prime = 'N'
        if row[9] == 0:
          on_netflix = 'N'
        
        table.add_row([wrapr(row[0]),row[1],row[2],row[3],row[4], row[5], on_hulu, on_dp, on_prime, on_netflix, row[10], wrapr(row[11])])
      
      print(table)
      
      choice = prompt("Type 1 to go back to main menu or 2 to exit the program: ")
      
      if optionComplete(choice):
        break
      
      sys.exit()

                                   
    except con.Error as error:
      print("Failed to get movie details: {}".format(error))
      print()
      return

def addToWatchedList(db, userid):
  while True:
    try:
      matching_row = confirmMovie(db)
      
      if matching_row == None:
        continue
      
      rating = prompt("Please rate the movie out of 10:")
      review_content = prompt("Please enter your text review: ")
      
      commitReview(db,int(matching_row[0]), int(userid), int(rating),review_content)
      
      choice = prompt("Type 1 to go back to main menu or 2 to exit the program: ")
      
      if optionComplete(choice):
        break
      
      sys.exit()
      
    except con.Error as error:
      print("Failed to add movie: {}".format(error))
      print()
      return
  
def editWatchedList(db, userid):
  while True:
    try:
      curs = db.cursor()
      answer=prompt('Please enter a movie name: ')
      grab_movie = """SELECT titleID, originalTitle, releaseYear FROM Movies INNER JOIN MovieUser USING(titleID) WHERE originalTitle LIKE %s AND userID = %s;"""
      answer = '%' + answer + '%'
      curs.execute(grab_movie, (answer,userid))
      matching_data = curs.fetchall()
      
      if len(matching_data) == 0:
        print('Movie could not be found, please try again.')
        break

      table = PrettyTable()
      table.field_names = ["#","TitleID","Title","Release Year"]
      
      for i,row in enumerate(matching_data):
        table.add_row([i+1,row[0],row[1],row[2]])
      print('Movies Found On Watched List:')
      print(table)
      
      movie_to_select = prompt("Please confirm the movie you'd like to edit/delete by entering the row number: ")
      if movie_to_select.isdigit() == False or int(movie_to_select) > len(matching_data):
        print('Invalid input, please try again')
        break
    
      matching_row = matching_data[int(movie_to_select) - 1]
      
      choice = prompt('Would you like to edit or delete this movie on your watched list?(edit/delete): ')
      
      if choice.lower() == 'edit':
        editReview(db,userid,matching_row)
        
      elif choice.lower() == 'delete':
        deleteReview(db,userid,matching_row)
        
      else:
        print('I did not understand that option, please try again')
        continue
      
      choice = prompt("Type 1 to go back to main menu or 2 to exit the program: ")

      if optionComplete(choice):
        break
      
      sys.exit()
      
      
    except con.Error as error:
      print("Failed to edit Watch List: {}".format(error))
      print()
      return

def getWatchedList(db, userid):
  try:
    curs = db.cursor()
    get_watched_list_sql = """
    SELECT originalTitle, releaseYear, duration, rating, reviewContent 
    FROM MovieUser
    INNER JOIN Movies USING (titleID) WHERE MovieUser.userID = {} ORDER BY dateTime ASC;
    """.format(userid)
    
    curs.execute(get_watched_list_sql)
    
    data = curs.fetchall()
    
    table = PrettyTable()
    table.field_names = ['Title', 'Release Year', 'Duration', 'Rating', 'Review']
    table.align['Review'] = 'l'
    for row in data:
      table.add_row([row[0],row[1],row[2],row[3],wrapr(row[4])])
    
    print(table)
    choice = prompt("Type 1 to go back to main menu or 2 to exit the program: ")
    
    if optionComplete(choice):
      return
    
    sys.exit()
    
  except con.Error as error:
      print("Failed to get watchList: {}".format(error))
      print()
      return