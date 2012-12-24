#!/usr/bin/env python
# - coding: utf-8 -
# Copyright (C) 2012 Toms Bauģis <toms.baugis at gmail.com>

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template


from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("base.html")


@app.route("/recent")
def recent(fragment):
    """returns list of activities and categories sorted by recency"""
    # it would be much easier to return generated html pieces here
    # but web is slower than local javascript and we need to react instantaneously
    # to input. so this is why we have a /recent instead of /autocomplete
    pass

if __name__ == "__main__":
    app.run()
