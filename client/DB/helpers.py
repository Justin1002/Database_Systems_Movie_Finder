from textwrap import fill, dedent
from prompt_toolkit import prompt
from prettytable import PrettyTable

#Helper function to wrap paragraph texts correctly for PrettyTable
WRAP_WIDTH = 50
def wrapr(text):
  if text == None:
    return text
  new = fill(text, width = WRAP_WIDTH)
  return dedent(new)

def optionComplete(choice):
  print()    
  if choice == '1':
    return True
  elif choice == '2': 
    return False
  else:
    return False

def commitReview(db, titleID, userID, rating, reviewContent):
      
  insert_review_sql= 'INSERT INTO MovieUser (titleID, userID, rating, reviewContent) VALUES (%s,%s,%s,%s);'
  review_values = (titleID, userID, rating, reviewContent)
  curs = db.cursor()
  
  curs.execute(insert_review_sql,review_values)
  
  db.commit()
  return

def editReview(db, userid, matching_row):
  curs = db.cursor()
  rating = prompt("Please rate the movie out of 10:")
  review_content = prompt("Please enter your text review: ")
      
  update_row_sql = '''UPDATE MovieUser SET rating = %s, reviewContent = %s
  WHERE titleID = {} and userID = {};
  '''.format(matching_row[0],userid)
        
  curs.execute(update_row_sql, (rating, review_content))
  return

def deleteReview(db, userid, matching_row):
  curs = db.cursor()
  delete_movie_sql = f'''
  DELETE FROM MovieUser 
  WHERE titleID = {matching_row[0]} AND userID = {userid};
  '''
  curs.execute(delete_movie_sql)
  return