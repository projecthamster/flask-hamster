#!/usr/bin/env python
# - coding: utf-8 -
# Copyright (C) 2012-2013 Toms Bauģis <toms.baugis at gmail.com>
import datetime as dt
import itertools
from operator import itemgetter

from flask import Flask, request, session, redirect, url_for, abort, \
     render_template, jsonify


from flask import Flask

from hamster import db
from hamster import lib as hamster_lib
import os

# todo - unhardcode in some magic way
client = db.Storage(database_dir=os.path.expanduser("~/.local/share/hamster-applet/"))
app = Flask(__name__)

def _days_ago(days):
    return (dt.datetime.now() - dt.timedelta(days=days)).date()

def _get_facts(start_date, end_date):
    start_date = start_date.date() if isinstance(start_date, dt.datetime) else start_date
    end_date = end_date.date() if isinstance(end_date, dt.datetime) else end_date

    facts = client.get_facts(start_date, end_date, "")
    res = [(date, list(facts))
                for date, facts in itertools.groupby(facts, itemgetter("date"))]
    return res

@app.route("/")
def hello():
    return render_template("index.html",
                           activities=client.get_activities(),
                           todays_facts=client.get_todays_facts(),
                           before=reversed(_get_facts(_days_ago(10), _days_ago(1))),
                           today=dt.datetime.today().date(),
                           )


def _render_dates(start_date, end_date=None):
    end_date = end_date or start_date
    facts = _get_facts(start_date, end_date)
    facts = reversed(facts) # have most recent date first
    return render_template("index.html",
                           just_facts=True,
                           facts=facts,
                           today=dt.datetime.today().date())


@app.route('/more_facts', defaults={'page': None})
@app.route("/more_facts/<int:page>")
def more_facts(page=None):
    per_page = 10
    start_date = _days_ago((page + 1) * per_page)
    end_date = _days_ago(page * per_page + 1)
    return _render_dates(start_date, end_date)


@app.route("/recent")
def recent(fragment):
    """returns list of activities and categories sorted by recency"""
    # it would be much easier to return generated html pieces here
    # but web is slower than local javascript and we need to react instantaneously
    # to input. so this is why we have a /recent instead of /autocomplete
    pass


@app.route('/activities', methods=['POST'])
def activities():
    """create new activity. returns day that was changed (for insta-update)"""
    activity = request.form.get("activity")
    if not activity:
        return "no can do" # TODO - return 405 or something

    client.add_fact(activity, None, None)
    activity = hamster_lib.Fact(activity)
    start_time = activity.start_time or dt.datetime.now()

    day = _render_dates(start_time)

    return jsonify(date=start_time.strftime("%Y-%m-%d"), rendered=day)




if __name__ == "__main__":
    #app.debug = True
    app.run()
