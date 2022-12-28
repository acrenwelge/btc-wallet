from os.path import expanduser

class UserService:

  filepath = expanduser('~/.wallet/password.txt')

  def validate_password(self, pw: str):
    file_pw = self.get_pw_from_file()
    if pw == file_pw:
      return True
    else:
      return False

  def get_pw_from_file(self):
    with open(self.filepath, 'r') as f:
      return f.read().rstrip('\n')

  def save_pw(self, newpw: str):
    with open(self.filepath, 'w') as f:
      f.write(newpw)