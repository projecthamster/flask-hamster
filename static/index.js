var prevPhase = "time-or-activity";

var currentMonth = null,
    currentYear = null;



function currentPhase() {
    parts = ["time-or-activity", "activity", "category", "comment-and-tags"]


    // tries to figure out at which input part are we right now
    var activity = Activity($(".activity-input input").val());
    var lastChar = activity.unparsed.substring(activity.unparsed.length-1);

    if (!activity.unparsed) {
        return 0;
    }

    var index = 0;
    if (!activity.activity) {
        index = 0;
    } else if (!activity.comment && activity.tags.length==0) {
        if (activity.unparsed.indexOf("@") == -1) {
            index = 1
        } else {
            index = 2
        }
        if (lastChar == " ")
            index +=1;
    } else if (activity.comment || activity.tags.length > 0) {
        index = 3;
    }

    if (lastChar == " ") {
        index += 1;
    }
    return parts[Math.min(index, parts.length-1)]
}

function checkMonthYear() {
    /* runs through all the fresh rows and in case when the
     * month or year changes add the year/month indicator
     */

    $(".fresh").each(function(i, row) {
        row = $(row);
        var year = row.attr("year"),
            month = row.attr("month");
        var before = $(".before");

        if (year != currentYear || month != currentMonth) {
            var dates = $('<span class="span5 yearmonth" />')

            if (row[0] != before.children().first()[0])
                row.addClass("new-month")

            if (year != currentYear) {
                row.addClass("new-year")
                dates.append($('<span class="year" />').text(year))
            }

            dates.append($('<span class="month" />').text(month))

            row.append(dates);
            currentMonth = month;
            currentYear = year;
        }

        row.removeClass("fresh");
    })
}

