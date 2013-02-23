function parseTime(timeorDelta) {
    if (!timeorDelta)
        return null;

    var res = new Date();
    if (timeorDelta.indexOf("-") == 0) {
        // return delta from current time minus specified minutes
        res = new Date(res - 0 + (parseInt(timeorDelta) * 1000 * 60));
    } else {
        var timeParts = timeorDelta.split(":");
        res.setHours(timeParts[0]);
        res.setMinutes(timeParts[1] || 0)
    }
    return res;
}


function Activity(fragment) {
    var activity = {
        unparsed: fragment,
        startTime: null,
        endTime: null,
        activityUnparsed: null,
        activity: null,
        category: null,
        tags: null,
        comment: null
    };

    // tries to figure out activity info parts from the string
    // syntax: [hh:mm[-hh:mm] / -mm] activity[@category] #tag1 #tag2 #tag3 comment
    if (!fragment)
        return activity;

    var parts = fragment.split(" ").reverse(); //reverse as pop pops from the end
    var part = parts.pop();

    var timeRegexp = /^[1-9|\-|\:].*$/ig; //[hh:mm[-hh:mm] / -mm]
    if (timeRegexp.test(part)) {
        // we have ourselves a time
        var startTime = part,
            endTime;
        if (part.indexOf("-", 1) > 0) {
            // startTime-endTime
            startTime = part.substring(0, part.indexOf("-", 1));
            endTime = part.substring(part.indexOf("-", 1) + 1);
        }
        activity.startTime = parseTime(startTime);
        activity.endTime = parseTime(endTime);

        activity.activityUnparsed = parts.pop(); // the next part is activity
    } else {
        activity.activityUnparsed = part;
    }

    if (!activity.activityUnparsed)
        return activity;

    activity.activity = activity.activityUnparsed.split("@")[0]
    if (activity.activityUnparsed.indexOf("@") > 0)
        activity.category = activity.activityUnparsed.split("@")[1]

    // tags and comment
    var tags = [];
    var comment = [];
    while (parts.length > 0) {
        part = parts.pop();
        if (part.indexOf("#") == 0) {
            tags.push(part.substring(1));
        } else {
            comment.push(part);
        }
    }
    activity.tags = tags;
    activity.comment = comment.join(" ");

    return activity;
}

function flashUpdate(container) {
    $(container).css({backgroundColor: "#FFFD00"})
                .animate({backgroundColor: "#fafafa"}, "slow", function(){
                    $(container).css({backgroundColor: ""}); // unset at the end
                })

}
