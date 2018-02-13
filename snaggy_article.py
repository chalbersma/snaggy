import newspaper
import urllib.parse

'''
Class for dealing with articles
'''

class article:
    def __init__(self, url="", keep_html=True):
        self.config = newspaper.Config()
        self.config.keep_article_html = True

        self.url = url

        # Validate URL
        try:
            self.parse_result = urllib.parse.urlparse(self.url)
            print(self.parse_result)
        except Exception as e :
            self.parse_result = False
            self.article_data = dict()
        else :
            # It's okay to Attempt a parse
            self.article_data = self.extract()
        finally:
            # Any Future Cleanup Goes Here
            self.article_data["url"] = url
            pass

    def extract(self):
        article = newspaper.Article(url=self.url, config=self.config)
        article.download()
        article.parse()

        article_data = dict()

        article_data["title"]=article.title

        article_data["text"]=article.text

        article_data["topimage"]=article.top_image

        article_data["authors"]=article.authors

        article_data["date"] = article.publish_date

        article_data["keywords"] = article.keywords

        return article_data
