import uuid
import random

from flask import (Blueprint, abort, jsonify, request)
from werkzeug.exceptions import HTTPException

mod = Blueprint('games', __name__, url_prefix='/games')

games = {}

word_list = ['Banana', 'Canine', 'Unosquare', 'Airport']

def generate_word():
    return random.choice(word_list)

def mask_word(word, guessed_letters):
    masked_word = []
    for letter in word:
        if letter.lower() in guessed_letters:
            masked_word.append(letter)
        else:
            masked_word.append('_')
    return masked_word

def is_valid_guess(guess):
    if not guess.isalpha() or len(guess) != 1:
        return False
    return True

def check_correct_guess(guess, game, word):
    if guess not in game['guessed_letters']:
        game['guessed_letters'].append(guess)
        if guess not in word.lower():
            game['attempts']-=1
            
def update_game_status(game):
    if game['attempts'] == 0:
        return 'lost'
    if ('_') in (''.join(game['masked_word'])):
        return 'in progress'
    else:
        return 'won'
    
def api_output(game):
    api_output = {'guesses_so_far': game['guessed_letters'],
        'remaining_attempts': game['attempts'],
        'status': game['game_status'],
        'word': ''.join(game['masked_word'])
    }
    return api_output

@mod.route('/', methods=['POST'])
def start_game():
    game_id = str(uuid.uuid4())
    word = generate_word()
    games[game_id] = {
        'word': word,
        'guessed_letters': [],
        'attempts': 6,
        'game_status': 'waiting first guess',
        'masked_word': ''
    }
    return game_id, 201
    
@mod.route('/<string:game_id>', methods=['GET', 'DELETE', 'POST'])
def get_game_state(game_id):
    game = games.get(game_id)
    if request.method == 'DELETE':
        game.clear()
        return jsonify({'message:': 'Game deleted'}), 204
    if game is None:
        abort(404)
    game['masked_word'] = mask_word(game['word'], game['guessed_letters'])
    return jsonify(api_output(game))

@mod.route('/<string:game_id>/guesses', methods=['POST'])
def make_guess(game_id):
    game = games.get(game_id)
    if game is None:
        abort(404)
    if not request.json or 'letter' not in request.json:
        abort(400)
        
    guess = request.json['letter'].lower()
    if not is_valid_guess(guess):
        return jsonify({'Message': 'Guess must be supplied with 1, letter'}), 400
    if guess in game['guessed_letters']:
        return jsonify({'Message': 'letter already guessed'}), 401
    
    word = game['word']
    check_correct_guess(guess, game, word)
    game['masked_word'] = mask_word(word, game['guessed_letters'])
    game['game_status'] = update_game_status(game)
    
    if game['game_status'] == 'won':
        return jsonify({'Message': 'Congratulations! You have guessed the word correctly.'}), 200
    if game['game_status'] == 'lost':
        return jsonify({'Error': 'No more attempts left, game over'}), 422
    
    return api_output(game)