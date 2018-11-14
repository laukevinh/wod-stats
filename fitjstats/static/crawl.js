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

var btnToday = document.getElementById("getToday");
btnToday.addEventListener("click", showToday());

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

function showOnly(e, cls) {
    if (e.classList.contains('inactive')) {
        e.classList.replace('inactive', 'active');
    } else {
        e.classList.replace('active', 'inactive');
    }
    var cards = document.getElementsByClassName("card");
    for (var i=1; i<cards.length; i++) {
        if (!cards[i].classList.contains(cls)) {
            if (cards[i].style.display != "none") {
                cards[i].style.display = "none";
            } else {
                cards[i].style.display = "flex";
            }
        }
    }
}

function addFlex(selector) {
    var items = document.getElementsByClassName(selector);
    for (var i=0; i<items.length; i++) {
        items[i].addEventListener("click", function() {
            if (this.classList.contains('collapsed')) {
                this.classList.replace('collapsed', 'expanded');
            } else {
                this.classList.replace('expanded', 'collapsed');
            }
        });
    }
}

addFlex("card");

