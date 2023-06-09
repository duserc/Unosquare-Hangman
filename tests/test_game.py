import unittest
import uuid

from main import app
from unittest.mock import patch
from controllers.game import start_game
from controllers.game import generate_word
from controllers.game import mask_word
from controllers.game import is_valid_guess
from controllers.game import check_correct_guess
from controllers.game import api_output

GAMEID = '06335e84-2872-4914-8c5d-3ed07d2a2f16'
BANANA = 'Banana'

def mock_uuid():
    return uuid.UUID(GAMEID)

def mock_generate_word():
    return BANANA

class TestGameController(unittest.TestCase):

    def test_generate_word_gives_string(self):
        result = generate_word()
        word_list = ['Banana','Canine','Unosquare','Airport']
        self.assertIn(result, word_list)
        
    def test_masking_mask_word(self):
        word = 'Banana'
        guessed_letters = []
        masked_word = mask_word(word, guessed_letters)
        self.assertEqual(masked_word, ['_', '_', '_', '_', '_', '_'])
    
    def test_is_invalid_guess_valid_lower_case(self):
        guess = 'a'
        guess_attempt = is_valid_guess(guess)
        self.assertTrue(guess_attempt)
    
    def test_is_invalid_guess_valid_upper_case(self):
        guess = 'B'
        guess_attempt = is_valid_guess(guess)
        self.assertTrue(guess_attempt)   
        
    def test_is_invalid_guess_invalid_character(self):
        guess = '#'
        guess_attempt = is_valid_guess(guess)
        self.assertFalse(guess_attempt)

    def test_is_invalid_guess_invalid_len(self):
        guess = 'aa'
        guess_attempt = is_valid_guess(guess)
        self.assertFalse(guess_attempt)

    def test_is_invalid_guess_invalid_len_with_caps(self):
        guess = 'aA'
        guess_attempt = is_valid_guess(guess)
        self.assertFalse(guess_attempt)
        
    def test_check_correct_guess_correct(self):
        guess = 'a'
        word = 'Banana'
        game =  {
        'word': word,
        'guessed_letters': [],
        'attempts': 6,
        'game_status': 'waiting first guess'
        }
        check_correct_guess(guess, game, word)
        self.assertEqual(game['guessed_letters'], ['a'])
        self.assertEqual(game['attempts'], 6)        
        
    def test_check_correct_guess_incorrect(self):
        guess = 'u'
        word = 'Unosquare'
        game =  {
        'word': word,
        'guessed_letters': [],
        'attempts': 6,
        'game_status': 'waiting first guess'
        }
        check_correct_guess(guess, game, word)
        self.assertEqual(game['guessed_letters'], ['u'])
        self.assertEqual(game['attempts'], 6)
        
    def test_api_output_outputs(self): 
        word = 'Unosquare'
        game = {
            'word': word,
            'guessed_letters': [],
            'attempts': 6,
            'game_status': 'waiting first guess',
            'masked_word': ''
        }
        expected_output = {
            'guesses_so_far': game['guessed_letters'],
            'remaining_attempts': game['attempts'],
            'status': game['game_status'],
            'word': game['masked_word']
        }
        check = api_output(game)
        self.assertEqual(check, expected_output)
        
        
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_create_game_returns_valid_id(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)    
    def test_generate_word_returns_word(self):
        id, code = start_game()
        word = mock_generate_word()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        self.assertEqual(word, 'Banana') 
    
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_check_game_state_returns(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        with app.test_client() as client:
            response = client.get(f'/games/{id}')
            self.assertEqual(response.status_code, 200)
            word = mock_generate_word()
            self.assertEqual(word, 'Banana') 
            expected_json = {
                'guesses_so_far': [],
                'remaining_attempts': 6,
                'status': 'waiting first guess',
                'word': '______'
            }
            self.assertEqual(response.json, expected_json)
    
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_make_guess_correct_letter_lower(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        with app.test_client() as client:
            response = client.get(f'/games/{id}')
            self.assertEqual(response.status_code, 200)
            word = mock_generate_word()
            self.assertEqual(word, 'Banana') 
            expected_json = {
                'guesses_so_far': [],
                'remaining_attempts': 6,
                'status': 'waiting first guess',
                'word': '______'
            }
            self.assertEqual(response.json, expected_json)
            with app.test_client() as client:
                response = client.post(f'/games/{id}/guesses', json={'letter': 'a'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['a'],
                'remaining_attempts': 6,
                'status': 'in progress',
                'word': '_a_a_a'
                }
                self.assertEqual(response.get_json(), expected_response)
                
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_make_guess_correct_upper_case_letter(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        with app.test_client() as client:
            response = client.get(f'/games/{id}')
            self.assertEqual(response.status_code, 200)
            word = mock_generate_word()
            self.assertEqual(word, 'Banana') 
            expected_json = {
                'guesses_so_far': [],
                'remaining_attempts': 6,
                'status': 'waiting first guess',
                'word': '______'
            }
            self.assertEqual(response.json, expected_json)
            with app.test_client() as client:
                response = client.post(f'/games/{id}/guesses', json={'letter': 'B'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['b'],
                'remaining_attempts': 6,
                'status': 'in progress',
                'word': 'B_____'
                }
                self.assertEqual(response.get_json(), expected_response)
                
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_make_guess_correct_incorrect_char(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        with app.test_client() as client:
            response = client.get(f'/games/{id}')
            self.assertEqual(response.status_code, 200)
            word = mock_generate_word()
            self.assertEqual(word, 'Banana') 
            expected_json = {
                'guesses_so_far': [],
                'remaining_attempts': 6,
                'status': 'waiting first guess',
                'word': '______'
            }
            self.assertEqual(response.json, expected_json)
            with app.test_client() as client:
                response = client.post(f'/games/{id}/guesses', json={'letter': '#'})
                self.assertEqual(response.status_code, 400)
                expected_response = {'Message': 'Guess must be supplied with 1, letter'}
                self.assertEqual(response.get_json(), expected_response)
                
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_make_guess_correct_word(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        with app.test_client() as client:
            response = client.get(f'/games/{id}')
            self.assertEqual(response.status_code, 200)
            word = mock_generate_word()
            self.assertEqual(word, 'Banana') 
            expected_json = {
                'guesses_so_far': [],
                'remaining_attempts': 6,
                'status': 'waiting first guess',
                'word': '______'
            }
            self.assertEqual(response.json, expected_json)
            with app.test_client() as client:
                response = client.post(f'/games/{id}/guesses', json={'letter': 'B'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['b'],
                'remaining_attempts': 6,
                'status': 'in progress',
                'word': 'B_____'
                }
                self.assertEqual(response.get_json(), expected_response) 
                response = client.post(f'/games/{id}/guesses', json={'letter': 'a'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['b', 'a'],
                'remaining_attempts': 6,
                'status': 'in progress',
                'word': 'Ba_a_a'
                }
                self.assertEqual(response.get_json(), expected_response)
                response = client.post(f'/games/{id}/guesses', json={'letter': 'n'})
                self.assertEqual(response.status_code, 200)
                expected_response = {'Message': 'Congratulations! You have guessed the word correctly.'}
                self.assertEqual(response.get_json(), expected_response)
            
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_make_guess_incorrect_word(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        with app.test_client() as client:
            response = client.get(f'/games/{id}')
            self.assertEqual(response.status_code, 200)
            word = mock_generate_word()
            self.assertEqual(word, 'Banana') 
            expected_json = {
                'guesses_so_far': [],
                'remaining_attempts': 6,
                'status': 'waiting first guess',
                'word': '______'
            }
            self.assertEqual(response.json, expected_json)
            with app.test_client() as client:
                response = client.post(f'/games/{id}/guesses', json={'letter': 'x'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['x'],
                'remaining_attempts': 5,
                'status': 'in progress',
                'word': '______'
                }
                self.assertEqual(response.get_json(), expected_response) 
                response = client.post(f'/games/{id}/guesses', json={'letter': 'y'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['x', 'y'],
                'remaining_attempts': 4,
                'status': 'in progress',
                'word': '______'
                }
                self.assertEqual(response.get_json(), expected_response) 
                response = client.post(f'/games/{id}/guesses', json={'letter': 'z'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['x', 'y', 'z'],
                'remaining_attempts': 3,
                'status': 'in progress',
                'word': '______'
                }
                self.assertEqual(response.get_json(), expected_response) 
                response = client.post(f'/games/{id}/guesses', json={'letter': 'e'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['x', 'y', 'z', 'e'],
                'remaining_attempts': 2,
                'status': 'in progress',
                'word': '______'
                }
                self.assertEqual(response.get_json(), expected_response) 
                response = client.post(f'/games/{id}/guesses', json={'letter': 'f'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['x', 'y', 'z', 'e', 'f'],
                'remaining_attempts': 1,
                'status': 'in progress',
                'word': '______'
                }
                self.assertEqual(response.get_json(), expected_response) 
                response = client.post(f'/games/{id}/guesses', json={'letter': 'g'})
                self.assertEqual(response.status_code, 422)
                expected_response = {'Error': 'No more attempts left, game over'}
            
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_make_guess_repeated_letter(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        with app.test_client() as client:
            response = client.get(f'/games/{id}')
            self.assertEqual(response.status_code, 200)
            word = mock_generate_word()
            self.assertEqual(word, 'Banana') 
            expected_json = {
                'guesses_so_far': [],
                'remaining_attempts': 6,
                'status': 'waiting first guess',
                'word': '______'
            }
            self.assertEqual(response.json, expected_json)
            with app.test_client() as client:
                response = client.post(f'/games/{id}/guesses', json={'letter': 'B'})
                self.assertEqual(response.status_code, 200)
                expected_response = {
                'guesses_so_far': ['b'],
                'remaining_attempts': 6,
                'status': 'in progress',
                'word': 'B_____'
                }
                self.assertEqual(response.get_json(), expected_response) 
                response = client.post(f'/games/{id}/guesses', json={'letter': 'b'})
                self.assertEqual(response.status_code, 401)
                expected_response = {'Message': 'letter already guessed'}
                self.assertEqual(response.get_json(), expected_response) 
                
    @patch('controllers.game.generate_word', mock_generate_word)
    @patch('uuid.uuid4', mock_uuid)
    def test_make_games_id_dele(self):
        id, code = start_game()
        self.assertEqual(code, 201)
        self.assertEqual(id, GAMEID)
        with app.test_client() as client:
            response = client.delete(f'/games/{id}')
            self.assertEqual(response.status_code, 204)

if __name__ == '__main__':
    unittest.main()