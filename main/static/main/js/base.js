/*
 * Global constants
 *
 * */
var readMoreSize = 400; // max size to show read more button

var $window = $(window);

/* Call functions, initialize, etc */
$(document).ready(function() {
    var csrftoken = getCookie('csrftoken'); 
    
    // Add count to browser sessions
    incrementBrowserTabCount();

    /*
     * Activate tooltipster for beautiful tooltip
     *
     * */
    $('.tooltip').tooltipster();


    /* 
     * Setup ajax for jquery here. 
     * */
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }); // end of ajaxSetup


    /* 
     * Check if counter == 1 for every 30 sec
     * If the counter is equal to 1 then we will set a new interval
     * for refreshing token in every 7 mins
     *
     * */
    setInterval(function() {
        // Only 1 session can get the token
        var counter = parseInt(localStorage.getItem("session:counter") || 0, 10);
        var token = null;

        console.log("[!] Counter: " + counter);
        console.log("[!] Active intervals: " + window.activeIntervals);

        if (window.activeIntervals == 1) {
            if (counter == 1) {
                console.log("[!] Setting interval for refreshing token...");
                setInterval(function() {
                    console.log("[+] Trying to refresh token...");

                    token = getToken();
                    console.log("[!] Refreshing using token: " + token);

                    if (token != null) {
                        $.when(function() {
                            return $.ajax({
                                url: '/api/api-token-refresh/',
                                type: 'post',
                                data: {token: token},
                                dataType: 'json',
                                error: function(xhr) {
                                    console.log(xhr.status + " " + xhr.responseText);
                                },
                            });
                        }()).done(function(data) {
                            // We got a new token. Update our storage
                            console.log("[+] New token: " + data.token);
                            saveToken(data.token);
                        });
                    } else {
                        console.log("[!] Token is null!");
                    }

                }, 1000 * (60 * 3)) // 3 mins. end of setInterval
            } // end of counter == 1 and token != null
        } // end of if activeIntervals == 1
    }, 1000 * 30); // end of interval

}); // end of ready



/* 
 * Check if given note id is already in the document (page)
 *
 * @notepk id of note
 *
 * */
var isNoteAlreadyRendered = function(notepk, button) {
    var button = button || "add-to-vault-btn";

    var elem = $('.' + button + '[data-notepk=' + notepk +']');
    if (elem.length != 0) {
        return true;
    } else {
        return false;
    }
};


/* 
 * Extract categories from note
 *
 * @arg note
 * @return categories extracted categories from note
 * */
var extractCategories = function(note) {
    categories = note.match('#([a-zA-Z\\d]+)');

    // If no categories found return false
    if (categories === null) {
        return false;
    }

    // Remove pound symbol
    $.each(categories, function(index, value) {
        categories[index] = value.replace('#', '');
    });

    // Remove duplicates
    var unique_categories = categories.reduce(function(a,b){
        if (a.indexOf(b) < 0 ) {
            a.push(b);
        }

        return a;
    },[]);

    return unique_categories;

}; // end of extractCategories



/*
 * toggle show/hide notes loading animation
 *
 * */
var toggleNotesLoadingAnim = function(option) {
    var $notesLoadAnim = $("#notes-load-anim");

    if (option == 'show') {
        if ($notesLoadAnim.length != 0) {
            return false;
        }
        var loading_html = '';
        loading_html += '<div id="spinner-wrapper">';
        loading_html += '<div id="notes-load-anim" class="spinner">';
        loading_html += '<div class="double-bounce1"></div>';
        loading_html += '<div class="double-bounce2"></div>';
        loading_html += '</div>'; // end of spinner
        loading_html += '</div>'; // end of spinner wrapper

        $('#posted-notes').append(loading_html);

        $notesLoadAnim.show();
    } else if (option == 'hide') {
        $notesLoadAnim.remove();
    }
}; // end of toggleNotesLoadingAnim




/*
 *  Increment browser tab count
 *
 * */
var incrementBrowserTabCount = function() {
    // Add session counter
    var counter = parseInt(localStorage.getItem("session:counter")
            || 0, 10);
    counter++;
    console.log("[+] Browser count: incrementing: " + counter);
    localStorage.setItem("session:counter", counter);
    return counter;
}; // end of incrementBrowserTabCount

/* 
 * Decrement browser count
 *
 * */
var decrementBrowserTabCount = function() {
    var counter = parseInt(localStorage.getItem("session:counter") || 0, 10);

    if (counter >= 1) {
        counter--;
    } 

    console.log("[+] Browser count: decrementing: " + counter);
    localStorage.setItem("session:counter", counter);
    return counter;
}

/*
 * Save token to localStorage and sessionStorage
 *
 *
 * */
var saveToken = function(token) {
    sessionStorage.setItem("session:token", token);
    localStorage.setItem("session:token", token);
}; // end of saveToken

/* 
 * From django documentation to get csrf token from cookie 
 * */
var getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} // end of getCookie

var csrfSafeMethod = function (method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
} // end of csrfSafeMethod

/*
 * Will return an json object. For ajax purpose
 *
 * @arg key
 * @return $.ajax
 *
 * */
var getTokenWithKey = function(key, error_400) {
    var error_400 = error_400 || function(xhr) {
        console.log(xhr.status + " :" + xhr.responseText);
    };

    return $.ajax({
        url: '/api/api-token-auth/',
        type: 'post',
        data: {key: key},
        dataType: 'json',
        statusCode: {
            400: error_400,
        }, // end of statusCode
    });
}; // end of getTokenWithKey



/* 
 *
 * Get the token from the storage
 * 
 * @return token - Authentication token
 * */
var getToken = function() {

    var sessionToken, localToken;

    localToken = localStorage.getItem('session:token');
    sessionToken = sessionStorage.getItem('session:token');

    console.log("[+] Local token: " + localToken);
    console.log("[+] Session token: " + sessionToken)

    // Copy sessionToken to localStorage for ux browsing
    //if (sessionToken && sessionToken !== 'null') {
    if (localToken && localToken !== 'null') {
        console.log("[!] Using local token...");
        sessionStorage.setItem("session:token", localToken);
        return  localToken;
    } else if (sessionToken && sessionToken !== 'null') {
        // We got a session token. Now record it
        console.log("[!] Using session token...");
        localStorage.setItem("session:token", sessionToken);
        return sessionToken;
    } else {
        // No token kid
        return null;
    }  // end of else
    
} // end of getToken


/* delay execution */
var delay = (function(){
  var timer = 0;
  return function(callback, ms){
      clearTimeout (timer);
      timer = setTimeout(callback, ms);
    };
})();


// Original timers
window.originalSetInterval = window.setInterval;
window.originalClearInterval = window.clearInterval;
// Count of all active intervals
window.activeIntervals = 0;

/* 
 * Overide the setInterval function to count all active setIntervals
 *
 * */
window.setInterval = function(func, delay) {
    window.activeIntervals++;
    return window.originalSetInterval(func, delay);
};

window.clearInterval = function(func, delay) {
    window.activeIntervals--;
    return window.originalClearInterval(func, delay);
};



/*
 * Remove session token when all the tabs are closed
 * 
 * -- When I accidentally closed all the tabs :)
 *
 * */
$window.bind('beforeunload', function() {
    var counter = decrementBrowserTabCount();
        
    // All pages are closed, remove the session token
    console.log("[!] Counter: " + counter);
    if (counter <= 0) {
        // Handle page reloads using sessionStorage
        sessionStorage.setItem("session:token",
                localStorage.getItem("session:token"));

        localStorage.removeItem("session:token");
    }


}); // end of beforeunload

