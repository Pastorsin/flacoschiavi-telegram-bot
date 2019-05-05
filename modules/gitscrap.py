from bs4 import BeautifulSoup
import urllib.request


class GitScrap():

    def __init__(self):
        self.URL = "https://github.com/Pastorsin/" + \
            "test-repo/commits/master"
        self.exec_scrap()
        self.last_commits = self.get_commits_info()

    def exec_scrap(self):
        self.soup = BeautifulSoup(self.get_html(), 'html.parser')

    def get_html(self):
        request = urllib.request.Request(self.URL)
        html = urllib.request.urlopen(request).read()
        return html

    def get_commits_info(self):
        autor_with_commit = zip(self.get_autor_names(),
                                self.get_commits_text())
        return set(autor_with_commit)

    def get_autor_names(self):
        autor_names = map(lambda autor: autor['aria-label'], self.get_autors())
        return list(autor_names)

    def get_autors(self):
        autors = self.soup.find_all('div', {'class': 'AvatarStack-body'})
        return autors

    def get_commits_text(self):
        commits_text = map(lambda commit: commit.text, self.get_commits())
        return list(commits_text)

    def get_commits(self):
        commits = self.soup.find_all(
            'a', {'class': 'message js-navigation-open'})
        return commits

    def there_new_commits(self):
        return bool(self.get_new_commits())

    def get_new_commits(self):
        return self.get_commits_info().difference(self.last_commits)

    def update_commits(self):
        self.last_commits = self.get_commits_info()
