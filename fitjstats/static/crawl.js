function showToday() {
    var date = new Date();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    if (month < 10)
        month = "0" + month;
    if (day < 10)
        day = "0" + day
    document.getElementsByName("YYYY")[0].value = date.getFullYear();
    document.getElementsByName("MM")[0].value = month;
    document.getElementsByName("DD")[0].value = day;
}

function display(id, dates) {
    document.getElementById(id).innerHTML = "";
    for (var i = 0; i < dates.length; i++) {
        var str;
        if ((i + 1) % 7 == 0)
            str = "<br>";
        else
            str = " ";
        document.getElementById(id).innerHTML += dates[i] + str;
    }
}

function showCalendar() {
    var today = new Date();
    var firstDateOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    var firstDayOfMonth = firstDateOfMonth.getDay();
    var daysInMonth = new Date(today.getFullYear(), today.getMonth()+1, 0).getDate();
    var lastDayOfMonth = (firstDayOfMonth + daysInMonth - 1) % 7;
    var dates = [];

    for (var i = firstDayOfMonth; i>0; i--)
        dates.push(new Date(firstDateOfMonth - i).getDate())
    for (var i = 1; i<=daysInMonth; i++)
        dates.push(i);
    for (var i = 1; i < 7-lastDayOfMonth; i++)
        dates.push(i);

    display("calendar", dates);
}

function flex(e) {
    if (e.classList.contains('collapsed')) {
        e.classList.replace('collapsed', 'expanded');
    } else {
        e.classList.replace('expanded', 'collapsed');
    }
}

