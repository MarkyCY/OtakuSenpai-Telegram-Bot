from translate import Translator

def translate(q):
    text = q[:499]
    translator = Translator(to_lang="es")
    translation = translator.translate(f"{text}...")
    return translation