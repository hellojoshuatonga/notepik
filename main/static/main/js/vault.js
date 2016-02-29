$(document).ready(function() {
    /************************************************************************
     ***************************** VARIABLES ********************************
     ************************************************************************/
    var $postedNotes = $('#posted-notes');
    var $searchInput = $("#search-textinput");
    var $hashtagContainer = $("#hashtag-container");

    // For pagination
    var nextSearchedNotesUrl;
    
    // Constants
    var notesCurrentPage = 2;
    var encoded_url = window.location.pathname.split("/")[2];
    var $window = $(window);



    /************************************************************************
     ***************************** UTILS ************************************
     ************************************************************************/


    /*
     * Render json note data to note html
     *
     * @arg json note date to be rendered
     * @return noteHtml the template
     *
     * */
    var jsonToNote = function(json) {
        var noteHtml = "";
        noteHtml += '<div class="notes">';

        // notes-top-panel
        noteHtml += '<div class="notes-top-panel">';
        noteHtml += '<p class="note-date">' + json.date_created_timeago + '</p>';
        noteHtml += '</div>'; // end of notes-top-panel

        // notes-center-panel
        noteHtml += '<div class="notes-center-panel">';
        // if chars are more than readMoreSize then truncate it
        if (json.note.length > readMoreSize) {
            noteHtml += '<div class="note-message">';
            noteHtml += '<p class="note-short">' + json.note.substring(0, readMoreSize) + '...</p>';
            noteHtml += '<p class="note-full" style="display:none;">' +
                json.note + '</p>';
            noteHtml += '</div>'; // end of note-message
            noteHtml += '<button class="read-more"><i class="fa fa-chevron-circle-down"></i>Read more</button>';
        } else {
            noteHtml += '<div class="note-message">';
            noteHtml += '<p>' + json.note + '</p>';
            noteHtml += '</div>'; // end of note-message
        }
        noteHtml += '</div>'; // end of notes-center-panel

        // note-categories
        if (json.categories.length != 0) {
            noteHtml += '<div class="note-categories">';

            // Loop through categories
            $.each(json.categories, function(index, category) {
                noteHtml += '<a class="note-category" href="#">' + category.category + '</a>';
            });
            

            noteHtml += '</div>'; // end of note-categories
        }


        // notes-bottom-panel
        noteHtml += '<div class="notes-bottom-panel">';
        noteHtml += '<div class="add-to-vault-count fa fa-archive">';
        noteHtml += '<span class="reposters-count">';
        if (json.reposters_count != 0) {
            noteHtml += json.reposters_count;
        }
        noteHtml += '</span>';
        noteHtml += '</div>'; // end of add-to-vault-count
        
        noteHtml += '<button class="notes-bottom-button" data-notepk="' +
            json.id + '"><i class="fa fa-minus"></i>Remove from vault</button>';
        noteHtml += '</div>'; // end of notes-bottom-panel

        noteHtml += '</div>'; // end of notes

        return noteHtml;

    }; // end of jsonToNote


    /*
     *  Convert json object to hashtag panel
     *
     * @return hashtagHtml
     * */
    var jsonToHashtag = function(json, searchQuery) {
        var hashtagHtml = "";

        hashtagHtml += '<section id="hashtag-panel">';
        hashtagHtml += '<div id="hashtag-main">';
        hashtagHtml += '<h1 id="hashtag">' + searchQuery + '</h1>';
        hashtagHtml += '</div>'; // end of hashtag-main

        hashtagHtml += '<div id="hashtag-info">';
        hashtagHtml += '<ul>';
        hashtagHtml += '<li><strong>' + json.notes_count + '</strong> notes found</li>';

        if (json.results.length != 0) {
            hashtagHtml += '<li><p>Other categories you also included</p>';
        
            $.each(json.results, function(index, category) {
                hashtagHtml += '<a class="other-hashtags" href="#">#' + category.category + '</a>';
            });
            hashtagHtml += '</li>';
        }

        hashtagHtml += '</ul>';
        hashtagHtml += '</div>'; // end of hashtag-info
        hashtagHtml += '</section>'; // end of hashtag-panel

        return hashtagHtml;
    }; // end of jsonToHashtag


    /* 
     * Register function on sroll 
     *
     * */
    var loadOnScroll = function(callback) {
        // Remove last event handler first
        $window.off("scroll");

        $window.on('scroll', function() {
            if ($window.scrollTop() + $window.height() == $(document).height()) {
                callback();
            } // end of if
        }); // end of window
    };


    /* 
     * extract the next page url for pagination of searched notes 
     *
     * this will product something like this:
     * /api/vault/search/?encoded_url=1TdcKe&page=2&query=yourquery
     *
     * NOTE: This is not necessary
     * */
    var extractNextSearchedUrl = function(url) {
        var extracted;
        if (url != null) {
            extracted = url.split("/")
                .slice(3).join().replace(new RegExp(",", "g"), "/");
            return "/" + extracted;
        } else {
            return "";
        }

    } // end of extractNextSearchedUrl

    /*
     * Render other pages of searched notes
     *
     * */
    var renderSearchedNotesNext = function() {

        // Check if search input is null. if it is not null then we will
        // render next page searched notes
        if ($searchInput.val() == "") {
            alert("renderSearchNotesNext input is null!!!!!!!");
            return;
            //loadOnScroll(renderNotes);
        }

        if (nextSearchedNotesUrl == "") {
            alert("no more searched notes!: " + nextSearchedNotesUrl);
            return;
        }

        console.log("[+] Next searched notes url: " + nextSearchedNotesUrl);

        $.ajax({
            url: nextSearchedNotesUrl,
            method: "get",
            dataType: "json",

            success: function(json) {
                var notesHtml = "";

                // Extract the next url
                nextSearchedNotesUrl = extractNextSearchedUrl(json.next);
                console.log("[+] Next searched notes url: " + nextSearchedNotesUrl);

                // Render the notes
                $.each(json.results, function(index, note) {

                    if (isNoteAlreadyRendered(note.id, 'notes-bottom-button') == true) {
                        console.log("[!] Note is already in the dom: " + note.id);
                        return true; // continue to next data
                    }

                    // Append the rendered data to notesHtml
                    notesHtml += jsonToNote(note);
                }); // end of each

                // Now, append it to the container
                $postedNotes.append(notesHtml);
            },
            error: function(xhr) {
                alert("176: " + xhr.status + ": " + xhr.responseText);
            },

        }); // end of ajax

    }; // end of renderSearchedNotesNext

    /* 
     * Render notes from database  
     *
     * */
    var renderNotes = function() {
        $.ajax({
            // start in page 2 because we already rendered the first page
            url: "/api/notes/get_vault_notes/?encoded_url=" + encoded_url + 
                "&page=" + notesCurrentPage,
            method: 'get',
            dataType: 'json',
            statusCode: {
                404: function(xhr) {
                    // No more older posts
                    alert("196: " + xhr.status + ": " + xhr.responseText);
                },
            },
            beforeSend: function() {
                // Show the animation
                toggleNotesLoadingAnim('show');
            },
            success: function(result) {
                // Point to next page
                notesCurrentPage++;

                var notesHtml = "";
                // Iterate through the result
                $.each(result.results, function(index, data) {
                    // Check if it's already in the dom
                    if (isNoteAlreadyRendered(data.id, 'notes-bottom-button') == true) {
                        console.log("[!] Note is already in the dom: " + data.id);
                        return true; // continue to next data
                    }

                    //var noteHtml = jsonToNote(data);

                    notesHtml += jsonToNote(data);
                    
                }); // end of each
                
                $postedNotes.append(notesHtml);

            },
            complete: function() {
                // Hide loading animation
                toggleNotesLoadingAnim('hide');
            },
            error: function(xhr) {
                // TODO: 404 means no more results
                alert("232: " + xhr.status + " : " + xhr.responseText);
            },
        });
    } // end of renderNotes

    /************************************************************************
     ***************************** EVENT HANDLERS ***************************
     ************************************************************************/

    $searchInput.focus(function() {
        // Remove readonly. We use readonly because of fucking auto filling of this input
        $searchInput.removeAttr("readonly");
    });

    /* Search notes when user typing */
    $searchInput.keyup(function(event) {
        // Don't execute if it's not number or letters
        // Key codes:http://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes
        // keycodes used below: Letters, numbers, backspace, enter
        if ((event.which >= 48 && event.which <= 105) || event.which == 8 || 
                event.which == 13) {

            // Search notes from api
            delay(function() {
                // Reset notes current page for rendering default notes
                notesCurrentPage = 1;
                var searchQuery = $searchInput.val();

                // Check if search query is null
                if (searchQuery == "") {
                    // Render notes created and reposted sort by datetime decrement
                    // Clear old notes
                    $postedNotes.empty();

                    renderNotes();


                    // Empty the hashtag panel
                    $hashtagContainer.empty();

                    // Reregister onscroll event
                    console.log("[!] Registering renderNotes onscroll");
                    loadOnScroll(renderNotes);
                    return;
                }

                // Register new event for onscroll event
                console.log("[!] Registering renderSearchedNotesNext onscroll");
                loadOnScroll(renderSearchedNotesNext);

                var url = "/api/vault/search/?encoded_url=" + encoded_url +
                    "&query=" + encodeURIComponent(searchQuery);

                console.log("[+] Encoded url: " + encoded_url);
                console.log("[+] Url: " + url);


                $.ajax({
                    url: url,
                    method: "get",
                    dataType: "json",
                    
                    beforeSend: function() {
                        // Remove all notes first
                        $postedNotes.empty();
                        // Show the animation
                        toggleNotesLoadingAnim('show');
                    },
                    success: function(json) {
                        // Show message when result is empty
                        if (json.results.length <= 0) {
                            $postedNotes.prepend("Didn't match any notes");
                            return;
                        } 
                        var notesHtml = "";

                        // Extract the next url
                        nextSearchedNotesUrl = extractNextSearchedUrl(json.next);
                        console.log("[+] Next url: " + nextSearchedNotesUrl);

                        // Render the notes
                        $.each(json.results, function(index, note) {

                            if (isNoteAlreadyRendered(note.id, 'notes-bottom-button') == true) {
                                console.log("[-] Note is already in the dom: " + note.id);
                                return true; // continue to next data
                            }

                            // Append the rendered data to notesHtml
                            notesHtml += jsonToNote(note);
                        }); // end of each

                        // Now, prepend it to the container
                        $postedNotes.prepend(notesHtml);
                    },
                    error: function(xhr) {
                        // TODO
                        alert("315: " + xhr.responseText + ": " + xhr.status);
                    },
                    complete: function() {
                        // Hide loading animation
                        toggleNotesLoadingAnim('hide');

                        if (searchQuery[0] == "#") {
                            $.ajax({
                                url: "/api/categories/get_info/?query=" + 
                                    encodeURIComponent(searchQuery),
                                method: "get",
                                dataType: "json",

                                success: function(result) {
                                    console.log("Rendering category information...");
                                    $hashtagContainer.empty().prepend(jsonToHashtag(result, 
                                                searchQuery));
                                },
                                error: function(xhr) {
                                    alert("374: " + xhr.status + ": " + xhr.responseText);
                                },

                            }); // end of ajax
                        }
                    },
                }); // end of ajax

            }, 1000); // 1 second delay.  end of delay
        } else {
            console.log("[!] Key pressed: " + event.which);
            return;
        }


    }); // end of searchInput keyup
        

    /* 
     * For read more. Handler
     *
     * */
    $($postedNotes).on('click', '.read-more', function() {
        console.log("[!] Read more clicked");
        var $this = $(this);

        // Show the full note
        $this.siblings().children('.note-short').hide();
        $this.siblings().children('.note-full').show();

        // Remove the "Read more" button
        $this.remove();
    }); // end of read more handler

    /* Remove from vault button */
    $('body').on('click', '.notes-bottom-button', function() {
        var token = getToken();
        var caller = $(event.target);

        var _addToVaultBtn = caller.contents().filter(function() {
            return this.nodeType === 3;
        })[0];

        console.log("[+] Token: " + token);
        if (token == null) {
            alert("You don't have token");
            return;
        }

        if (_addToVaultBtn.textContent == "Remove from vault") {
            console.log("[-] Removing from vault...");

            $.ajax({
                url: "/api/notes/" + caller.data("notepk") + "/remove_from_vault",
                type: "get",
                dataType: "json",
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("Authorization", "JWT " + token);
                    _addToVaultBtn.textContent = "Removing note...";
                },
                //statusCode: {
                    //400: function(xhr) {
                        //// TODO
                        //alert(xhr.responseText + ": " + xhr.status);
                        //_addToVaultBtn.textContent = "Remove from vault";
                    //},
                    //401: function(xhr) {
                        //// TODO
                        //alert(xhr.responseText + ": " + xhr.status);
                        //_addToVaultBtn.textContent = "Remove from vault";
                    //},
                //},
                success: function(data) {
                    // Remove from vault
                    console.log("[-] Removing note: " + caller.data("notepk"));
                    // Remove the notes class of this element
                    caller.parent().parent().remove();
                },
                error: function(xhr) {
                    // TODO
                    alert("393: " + xhr.responseText + ": " + xhr.status);
                    _addToVaultBtn.textContent = "Remove from vault";
                },
            }); // end of ajax
        } // end of if

    }); // end of .notes-bottom-button handler


    /*
     * Don't do anything when the user press enter in search text input
     *
     * */
    $("#search-form").submit(function(event) {
        event.preventDefault();
        return false;
    });

    /* 
     * Load notes when user scroll until end
     *
     * */
    loadOnScroll(renderNotes);


});  // end of document ready
