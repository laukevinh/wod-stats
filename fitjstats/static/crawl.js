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
