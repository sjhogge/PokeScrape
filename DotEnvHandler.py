from os.path import join, dirname

repl = True

def set_environ():
  if not repl:
    from dotenv import load_dotenv
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)