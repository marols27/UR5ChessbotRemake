import gtts
import os

# Language in which you want to convert
language = 'en-au'

# Overwrite existing files if they already exist
def save_speech(text, filename):
    speech = gtts.gTTS(text=text, lang=language, slow=False, )
    speech.save(filename)

def overwrite_existing_files():
    text = "Welcome to the Chess Robot! Please select the difficulty level you would like to play against."
    save_speech(text, "welcome.mp3")

    text = "Easy"
    save_speech(text, "easy.mp3")

    text = "Medium"
    save_speech(text, "medium.mp3")

    text = "Hard"
    save_speech(text, "hard.mp3")

    text = "Cheater that's not a legal move"
    save_speech(text, "illegal_move.mp3")

    text = "The pieces are not in their correct starting positions"
    save_speech(text, "incorrect_starting_positions.mp3")

# Call the function to overwrite existing files
overwrite_existing_files()