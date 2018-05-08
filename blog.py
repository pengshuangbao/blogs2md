class Blog:
    def __init__(self, title, link, date, view, comment, page_index):
        self._comment = comment
        self._view = view
        self._date = date
        self._link = link
        self._title = title
        self._page_index = page_index

    def __repr__(self):
        return repr((self.title, self.link, self.date, self.view, self.comment, self.page_index))

    @property
    def title(self):
        return self._title

    @property
    def page_index(self):
        return self._page_index

    @property
    def link(self):
        return self._link

    @property
    def date(self):
        return self._date

    @property
    def view(self):
        return self._view

    @property
    def comment(self):
        return self._comment
