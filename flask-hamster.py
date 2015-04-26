#!/usr/bin/env python
# - coding: utf-8 -
# Copyright (C) 2012-2013 Toms Bauģis <toms.baugis at gmail.com>
import datetime as dt
import itertools
from operator import itemgetter

import json
import flask
from flask import request, session, redirect, url_for, abort, render_template
from flask import Flask

from hamster import db
from hamster import lib as hamster_lib
import os

events = []
# todo - unhardcode in some magic way
class StorageWithEvents(db.Storage):
    def facts_changed(self):
        events.append("hello")

client = StorageWithEvents(database_dir=os.path.expanduser("~/.local/share/hamster-applet/"))



app = flask.Flask(__name__)
import time

def _days_ago(days):
    return (dt.datetime.now() - dt.timedelta(days=days)).date()

def _get_facts(start_date, end_date):
    start_date = start_date.date() if isinstance(start_date, dt.datetime) else start_date
    end_date = end_date.date() if isinstance(end_date, dt.datetime) else end_date

    facts = client.get_facts(start_date, end_date, "")
    res = [(date, list(facts))
                for date, facts in itertools.groupby(facts, itemgetter("date"))]
    return res

def event_stream():
    if events:
        while events:
            yield "data: %s\n\n" % events.pop(0)

@app.route('/stream')
def stream():
    return flask.Response(event_stream(),
                          mimetype="text/event-stream")

@app.route("/")
def index():
    todays_facts=client.get_todays_facts()
    last_activity = todays_facts[-1] if todays_facts and not todays_facts[-1]['end_time'] else None

    return render_template("index.html",
                           activities=client.get_activities(),
                           last_activity=last_activity,
                           before=reversed(_get_facts(_days_ago(10), _days_ago(1))),
                           today=dt.datetime.today().date(),
                           )


@app.route("/json_all")
def json_all():
    facts=client.get_facts(dt.date(2007,1,1), dt.datetime.now().date(), "")
    facts = reversed(facts)

    res=[]
    for fact in facts:
        fact['start_time'] = fact['start_time'].strftime("%Y-%m-%d %H:%M:%S")
        if fact['end_time']:
            fact['end_time'] = fact['end_time'].strftime("%Y-%m-%d %H:%M:%S")
        fact['delta'] = int(fact['delta'].total_seconds() // 60)
        fact['date'] = fact['date'].strftime("%Y-%m-%d %H:%M:%S")
        res.append(fact)
    return json.dumps(res)


@app.route("/stats")
def stats():
    facts=client.get_facts(dt.date(2007,1,1), dt.datetime.now().date(), "")
    return render_template("stats.html",
                           facts=facts,
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

    return flask.jsonify(date=start_time.strftime("%Y-%m-%d"), rendered=day)

@app.route('/today', methods=['GET'])
def today():
    facts = client.get_todays_facts()
    if not facts:
        return ""

    date = facts[0]["date"]
    today = render_template("index.html",
                            just_facts=True,
                            facts=[(date, facts)])
    last_activity = facts[-1]
    if not last_activity["end_time"]:
        # TODO - what's going on here - why isn't __iter__ in hamster_lib taking care of this?
        last_activity['start_time'] = last_activity['start_time'].strftime("%H:%M")
        delta_minutes = last_activity['delta'].total_seconds() / 60
        last_activity['delta'] = "%02d:%02d" % (delta_minutes / 60,
                                                delta_minutes % 60)
        del last_activity['date']
    else:
        last_activity = None



    return flask.jsonify(date=date.strftime("%Y-%m-%d"),
                         rendered=today,
                         last_activity=last_activity)




if __name__ == "__main__":
    #app.debug = True
    print "Pretty sure i'm running on http://127.0.0.1:5000"
    app.run()
