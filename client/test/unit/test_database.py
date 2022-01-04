import unittest
import sys
import os
import io
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from DB.database import *
from DB.helpers import *
from unittest.mock import patch
import mysql.connector as con
from DB.config import mysql as cfg

db = con.connect(
  host= cfg["host"],
  user=cfg["user"],
  database=cfg["database"],
  password=cfg["password"]
  )

userID = 3
searchNumber = '11'
class TestConfirmMovie(unittest.TestCase):
  def test_confirm_movie_valid(self):
    '''
    Testing successful execution of movie confirmation procedure
    '''
    mock_args = ['Matrix', '1']
    with patch('DB.database.prompt', side_effect=mock_args):
      res = confirmMovie(db)
      self.assertEqual(res, (133093, 'The Matrix', 1999))
  
  @patch('sys.stdout', new_callable=io.StringIO)
  def test_confirm_movie_invalid(self, mocked_stdout):
    mock_args = ['123123123']
    with patch('DB.database.prompt', side_effect=mock_args):
      confirmMovie(db)
      self.assertEqual("Movie could not be found, please try again.\n", mocked_stdout.getvalue())

class TestFindMovieRecomendations(unittest.TestCase):
    @patch('DB.database.searchByCastMember')
    def test_cast_members(self, mock_call):
      '''
      Testing successful execution of cast member procedure 
      '''
      mock_call.return_value = ['''SELECT titleID FROM MovieCast
                                INNER JOIN CastMembers USING(castID)
                                INNER JOIN Movies USING(titleID)
                                WHERE role IN ('actress','actor') 
                                AND name IN (%s) ''', ('Anne Hathaway',) ]
      mock_args = ['1',searchNumber, 'N','2']
      with patch('DB.database.prompt', side_effect=mock_args):
          with self.assertRaises(SystemExit) as cm:
            findMovieRecommendations(db)
            self.assertEqual(cm.exception.code, 1)
    
    @patch('DB.database.searchByDirectors')
    def test_movie_directors(self, mock_call):
      '''
      Testing successful execution movie directors procedure
      '''
      mock_call.return_value = ['''
                                SELECT titleID From MovieCast
                                INNER JOIN CastMembers USING(castID)
                                INNER JOIN Movies USING(titleID)
                                WHERE role IN ('director')
                                AND name IN (%s)
                                ''', ('Lana Wachowski',)]
      mock_args = ['2',searchNumber,'2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)

    @patch('DB.database.searchByYear')
    def test_search_by_year(self, mock_call):
      '''
      Testing successful execution search by year procedure
      '''
      mock_call.return_value = ['''
                                SELECT titleID FROM Movies WHERE releaseYear = (%s)
                                ''', ('1950',)]
      mock_args = ['3',searchNumber,'N','2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)
          
    @patch('DB.database.searchByDuration')
    def test_search_by_duration(self, mock_call):
      mock_call.return_value = ['''
                                SELECT titleID FROM Movies WHERE duration >= %s
                                ''', ('200',)]
      mock_args = ['4',searchNumber,'N','2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)
          
    @patch('DB.database.searchByRating')
    def test_search_by_rating(self,mock_call):
      mock_call.return_value = ['''
                                SELECT titleID FROM Movies WHERE averageImdbRating >= %s
                                ''',('7.5',)]
      mock_args = ['5',searchNumber,'N','2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)
          
    @patch('DB.database.searchByCountry')
    def test_search_by_country(self, mock_call):
      mock_call.return_value = ['''
                                SELECT titleID FROM MovieCountry
                                INNER JOIN Countries USING (countryID)
                                WHERE countryName IN (%s)
                                ''',('Canada',)]
      mock_args = ['6',searchNumber,'N','2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)
          
    @patch('DB.database.searchByLanguage')
    def test_languages_found(self,mock_call):
      '''
      Testing successful execution successful language procedure (makes it to endpoint)
      '''
      mock_call.return_value = ['''
                                SELECT titleID From MovieLanguage
                                INNER JOIN Language USING (languageID)
                                WHERE languageName IN (%s)
                            ''',('French',)]
  
      mock_args = ['7',searchNumber,'N','2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)
  
    @patch('DB.database.searchByGenre')
    def test_genres_found(self,mock_call):
      '''
      Testing successful execution genre procedure (makes it to endpoint)
      '''
      mock_call.return_value = ['''
                                SELECT titleID From Movies WHERE find_in_set(%s,genre)
                                ''', ('Drama',)]
      mock_args = ['8',searchNumber,'N','2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)
    
    @patch('DB.database.searchByStreamingPlatform')
    def test_streaming_platform(self,mock_call):
      '''
      Testing successful execution streaming platform procedure (makes it to endpoint)
      '''
      mock_call.return_value = '''
                                SELECT titleID FROM Movies WHERE onNetflix = 1
                                '''
      mock_args = ['9',searchNumber,'N','2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)
          
    @patch('DB.database.searchByRTFresh')
    def test_critically_acclaimed(self,mock_call):
      '''
      Testing successful execution critically acclaimed procedure
      '''
      mock_call.return_value = '''
        SELECT RTLink, titleID, (sum(review_type = 1) / (sum(review_type = 1) + sum(review_type = 0))) as percentFresh
        FROM RottenTomatoesReviews INNER JOIN RottenTomatoesMovies USING (RTLink)
        WHERE top_critic = 1
        GROUP BY RTLINK HAVING percentFresh >= 0.6 AND count(top_critic) > 5
      '''
      
    @patch('DB.database.searchByCastMember')
    @patch('DB.database.searchByDirectors')
    def test_multiple_parameters(self,mock_callA,mock_callB):
      '''
      Testing successful execution successful response for multiple parameters
      '''
      mock_callA.return_value = ['''SELECT titleID FROM MovieCast
                                INNER JOIN CastMembers USING(castID)
                                INNER JOIN Movies USING(titleID)
                                WHERE role IN ('actress','actor') 
                                AND name IN (%s) ''', ('Keanu Reeves',) ]
      mock_callB.return_value = ['''
                          SELECT titleID From MovieCast
                          INNER JOIN CastMembers USING(castID)
                          INNER JOIN Movies USING(titleID)
                          WHERE role IN ('director')
                          AND name IN (%s)
                          ''', ('Lana Wachowski',)]
      
      mock_args = ['1', '2', searchNumber, '2']
      with patch('DB.database.prompt', side_effect=mock_args):
        with self.assertRaises(SystemExit) as cm:
          findMovieRecommendations(db)
          self.assertEqual(cm.exception.code, 1)
      
      
class TestGetMovieReviews(unittest.TestCase):
  def test_no_reviews_found(self):
    '''
    Testing successful execution procedure when no reviews are found
    '''
    mock_args = ['Alice','54']
    with patch('DB.database.prompt', side_effect=mock_args):
      getMovieReviews(db)
      self.assertRaises(Exception)
  
  def test_reviews_found(self):
    '''
    Testing successful execution find review procedure (makes it to endpoint)
    '''
    mock_args = ['Snakes', '4', 'N', '2']
    with patch('DB.database.prompt', side_effect=mock_args):
      with self.assertRaises(SystemExit) as cm:
        getMovieReviews(db)
        self.assertEqual(cm.exception.code, 1)


class TestCheckMovieDetails(unittest.TestCase):
  def test_movie_details(self):
    '''
    Testing successful execution movie details(makes it to endpoint)
    '''
    mock_args = ['Alice', '54', '2']
    with patch('DB.database.prompt', side_effect=mock_args):
      with self.assertRaises(SystemExit) as cm:
        checkMovieDetails(db)
        self.assertEqual(cm.exception.code, 1)
    

class TestAddToWatchedList(unittest.TestCase):
  @patch('DB.database.commitReview')
  def test_add_to_watched_list(self, mock_call):
    '''
    Testing successful add review procedure (makes it to endpoint)
    '''
    mock_call.return_value = ('')
    mock_args = ['Alice', '54', searchNumber,'Great', '2']
    with patch('DB.database.prompt', side_effect=mock_args):
      with self.assertRaises(SystemExit) as cm:
        addToWatchedList(db,userID)
        self.assertEqual(cm.exception.code, 1)
        
class TestGetWatchedList(unittest.TestCase):
  def test_get_watched_list(self):
    '''
    Testing successful get watched list procedure
    '''
    mock_args = ['2']
    with patch('DB.database.prompt', side_effect=mock_args):
      with self.assertRaises(SystemExit) as cm:
        getWatchedList(db,userID)
        self.assertEqual(cm.exception.code, 1)

class TestEditWatchedList(unittest.TestCase):
  @patch('DB.database.deleteReview')
  def test_delete_review(self,mock_call):
    '''
    Testing successful delete review procedure
    '''
    mock_call.return_value=('')    
    mock_args = ['Now You See Me', '1', 'delete', '2']
    with patch('DB.database.prompt', side_effect=mock_args):
      with self.assertRaises(SystemExit) as cm:
        editWatchedList(db,userID)
        self.assertEqual(cm.exception.code, 1)
  
  @patch('DB.database.editReview')
  def test_edit_review(self,mock_call):
    '''
    Testing successful edit review procedure
    '''
    mock_call.return_value=('')
    mock_args = ['Now You See Me', '1', 'edit', '2']
    with patch('DB.database.prompt', side_effect=mock_args):
      with self.assertRaises(SystemExit) as cm:
        editWatchedList(db,userID)
        self.assertEqual(cm.exception.code, 1)
  
    
if __name__ == '__main__':
    unittest.main(verbosity=2)