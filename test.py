import os

from py3xui import Api, Client

os.environ["XUI_HOST"] = "http://45.145.163.190:41322/bbVpkaCETNp4o8z"
os.environ["XUI_USERNAME"] = "MrPavlik"
os.environ["XUI_PASSWORD"] = "7a31ebba"

api = Api(host=os.environ["XUI_HOST"],
          username=os.environ["XUI_USERNAME"],
          password=os.environ["XUI_PASSWORD"])
api.login()

print(dir(Client))

client_by_email = api.client.get_by_email("MrPavlik")
print(f"Client by email has ID: {client_by_email}")
