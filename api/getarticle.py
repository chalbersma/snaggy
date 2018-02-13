#!/usr/bin/env python3

'''
getarticle - It's the part of this api that actually calls newspaper and
  snaggy_article and grabs the things.

```swagger-yaml
/getarticle/ :
  get:
    description: |
      Returns parsed article for a particular URL.
    responses:
      200:
        description: OK
    parameters:
      - name: url
        in: path
        description: |
          The URL you wish to check against. Encapsulate it in quotes to avoid
          issues with special characters.
        schema:
          type: string
        required: true
```

'''

import flask
import snaggy_article

getarticle = flask.Blueprint('api_getarticle', __name__)

@getarticle.route("/getarticle", methods=['GET'])
@getarticle.route("/getarticle/", methods=['GET'])
def api_getarticle(url = None):

    errors = False

    meta_info = dict()
    error_dict = dict()
    data_dict = dict()
    links_info = dict()

    if "url" in flask.request.args :
        url = flask.request.args["url"]
    else :
        errors = True
        error_dict["nourl"] = "No URL Specified."

    this_article = snaggy_article.article(url=url)

    if this_article.parse_result != False :
        # Article Parsed Successfully
        data_dict = this_article.article_data
    else :
        errors = True
        error_dict["article_parse_error"] = "Error Parsing Article."

    if errors == False :
        return flask.jsonify(meta=meta_info, data=data_dict, links=links_info)
    else :
        return flask.jsonify(meta=meta_info, errors=error_dict, links=links_info)



