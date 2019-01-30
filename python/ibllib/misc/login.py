import tkinter as tk


def login(title='Enter Credentials', default_username=None, default_passwd=None, add_fields=None):
    class Toto:
        def __init__(self, root, default_username=None, default_passwd=None, title=None,
                     add_fields=None):
            self.add_fields = add_fields or []
            self.var1 = tk.StringVar()
            self.root = root
            # self.root.geometry('300x160')
            self.root.title(title)
            # frame for window margin
            self.parent = tk.Frame(self.root, padx=10, pady=10)
            self.parent.pack(fill=tk.BOTH, expand=True)
            # entrys with not shown text
            self.add_entries = []
            for fname in self.add_fields:
                self.add_entries.extend([self.make_entry(self.parent, fname + ":", 42, show="")])

            self.user = self.make_entry(self.parent, "User name:", 42, show='',
                                        default=default_username)
            self.password = self.make_entry(self.parent, "Password:", 42, show="*",
                                            default=default_passwd)
            # button to attempt to login
            self.button = tk.Button(self.parent, borderwidth=4, text="Login", width=42, pady=8,
                                    command=self.get_value)
            self.button.pack(side=tk.BOTTOM)
            self.user.focus_set()
            self.USR = None
            self.MDP = None
            self.root.bind('<Return>', self.push_enter)
            # do not reproduce vim behaviour
            self.root.protocol("WM_DELETE_WINDOW", self.get_value)

        def make_entry(self, _, caption, width=None, default='', **options):
            tk.Label(self.parent, text=caption).pack(side=tk.TOP)
            entry = tk.Entry(self.parent, **options)
            if width:
                entry.config(width=width)
            entry.pack(side=tk.TOP, padx=10, fill=tk.BOTH)
            if default:
                entry.insert(0, default)
            return entry

        def push_enter(self, _):
            self.get_value()

        def get_value(self):
            self.USR = self.user.get()
            self.MDP = self.password.get()
            self.ADD = []
            for entry in self.add_entries:
                self.ADD.extend([entry.get()])
            self.root.destroy()
            self.root.quit()

    root = tk.Tk()
    toto = Toto(root, title=title, default_passwd=default_passwd,
                default_username=default_username, add_fields=add_fields)
    root.mainloop()
    return [toto.USR] + [toto.MDP] + toto.ADD

# from ibllib.misc import login
# a, b =login.login(default_passwd='tutu', default_username='turluser')
# a, b =login.login(default_passwd='tutu', default_username='turluser', title='supertitre')
# a, b, add1, add2 =login.login(default_passwd='tutu', default_username='turluser',
#                               title='supertitre', add_fields=['tuasdf', 'adfasdf'])