from pathlib import Path
import config


def load_lecture_texts(path_lectures):
    lecture_texts = {}
    for txt_file in sorted(Path(path_lectures).glob('*.txt')):
        with open(txt_file, 'r', encoding='utf-8') as f:
            lecture_texts[txt_file.name] = f.read()
    return lecture_texts

def load_exercise_texts(path_exercises):
    exercise_texts = {}
    for txt_file in sorted(Path(path_exercises).glob('*.txt')):
        with open(txt_file, 'r', encoding='utf-8') as f:
            exercise_texts[txt_file.name] = f.read()
    return exercise_texts

def load_forum_texts(path_forum):
    forum_texts = {}
    for txt_file in sorted(Path(path_forum).glob('*.txt')):
        with open(txt_file, 'r', encoding='utf-8') as f:
            forum_texts[txt_file.name] = f.read()
    return forum_texts
