function showToday() {
    var date = new Date();
    document.getElementsByName("year")[0].value =  date.getFullYear();
    document.getElementsByName("month")[0].value =  date.getMonth() + 1;
    document.getElementsByName("day")[0].value =  date.getDate();
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

function buildUrl(YYYY, MM, DD) {
    if (MM.length < 2 && MM<10)
        MM = '0'+MM
    if (DD.length < 2 && DD<10)
        DD = '0'+DD
    return "https://crossfit.com/comments/api/v1/topics/mainsite." + YYYY + MM + DD + "/comments";
}

function getUrl() {
    return buildUrl(
        document.getElementsByName("year")[0].value,
        document.getElementsByName("month")[0].value,
        document.getElementsByName("day")[0].value
    )
}

function getComments(url) {
    var init = {method: "GET", mode: "no-cors"};
    var data = fetch(url, init)
        .then(resp => resp.json())
        .catch(error => console.error('Error: ', error)); 
    document.getElementById("comments").innerHTML = data;
    
}
