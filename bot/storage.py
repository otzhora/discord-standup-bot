import os
import pickle


class Storage:
    def __init__(self, storage_filename, bot,  *args, **kwargs):
        self.storage_path = f"{os.getcwd()}/{storage_filename}"
        self.ids = set()
        self.users = {}

        try:
            with open(self.storage_path, "rb") as f:
                self.ids = pickle.load(f)
            for id in self.ids:
                self.users[id] = bot.get_user(id)
        except IOError:
            print(f"Cannot read file {self.storage_path}\n")

            try:
                with open(self.storage_path, 'wb') as f:
                    pickle.dump(self.ids, f)
            except IOError:
                print(f"Cannot create file {self.storage_path}")

    def __setitem__(self, key, value):
        self.users[key] = value
        self.ids.add(key)

        try:
            with open(self.storage_path, "wb") as f:
                pickle.dump(self.ids, f)
        except IOError:
            print(f"Cannot read file {self.storage_path}, so changes not saved on disk.")

    def __getitem__(self, item):
        return self.users[item]

    def __contains__(self, item):
        return item in self.users

    def values(self):
        return self.users.values()
