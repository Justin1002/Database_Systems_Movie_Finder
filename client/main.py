import sys
from prompt_toolkit import prompt
from DB.database import *

menu_options = {
  1: 'Find a movie recommendation',
  2: 'Look at movie reviews',
  3: 'Add a movie to your watched list',
  4: 'Check movie details',
  5: 'Access watched list',
  6: 'Edit watched list',
  7: 'Exit'
}

def menu(db, userid):
  try:
    for key in menu_options.keys():
      print(key, '---', menu_options[key])
    print()
    answer = prompt('Please select an option: ')
    
    if answer == '1':
      findMovieRecommendations(db)
    elif answer == '2':
      getMovieReviews(db)
    elif answer == '3':
      addToWatchedList(db, userid)
    elif answer == '4':
      checkMovieDetails(db)
    elif answer == '5':
      getWatchedList(db,userid)
    elif answer == '6':
      editWatchedList(db,userid)
    elif answer == '7':
      print('Thank you and goodbye!')
      exit()
    else:
      print('I did not understand your choice, please input a number from 1-7.')
      
  except KeyboardInterrupt:
    return
  
  except EOFError:
    sys.exit()

if __name__ == '__main__':
    db = initializeConnection()

    print('Welcome to Movie Finder!')
    userID = prompt('please enter your user ID: ')
    if not userID.isdigit():
      print('invalid userID')
      sys.exit()
    print('-----------------------------------------')
    print('Successfully logged in as user %s' % userID)
    print('-----------------------------------------')
    print("Press CTRL+D to exit the program at any point, and CTRL+C to get back to the main menu.")
    print()
    while True:
      menu(db, userID)

    
    
    