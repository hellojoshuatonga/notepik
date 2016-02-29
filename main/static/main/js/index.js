/*
 * @file: index.js
 * @author: Joshua Tonga
 * @date: January 20, 2016
 *
 * */

$(document).ready(function() {
    // Elements
    //    - Buttons
    var postBtn = document.getElementById("post-btn");
    var $postBtn = $(postBtn);
    var postNoteBtn = document.getElementById("post-key-btn");
    var closeKeyFromBtn = document.getElementById("close-key-form-btn");
    var addToVaultBtn = $(".add-to-vault-btn");
    var vaultBtn = document.getElementById("vault");
    //    - Input 
    var noteBox = document.getElementById("notebox"); // container of note-textarea
    var noteTextArea = document.getElementById("note-textarea");
    var $noteTextArea = $(noteTextArea);
    var $searchInput = $("#search-textinput");
    var keyInput = document.getElementById("key-input") // Input element for key 
    var keySubmit = document.getElementById("key-submit");
    var $searchInput = $("#search-textinput");
    //    - Form
    var popupKeyForm = document.getElementById("popup-key-form");
    var keySubmitForm = document.getElementById("key-submit-form");
    var postNoteForm = document.getElementById("post-note-form");
    //    - Label
    var keySubmitLabel = document.getElementById("key-submit-label");
    var keyLabel = document.getElementById("key-label");
    //    - Container
    var postedNotes = document.getElementById("posted-notes"); // Container for our notes
    var $postedNotes = $(postedNotes);
    var $noteBoxBottomPanel = $("#notebox-bottom-panel");
    //    - Tooltips
    var noteboxTooltip = $('.notebox-tooltip');

    // Variable constants
    //     - Initials
    var noteBoxInitialHeight = 0;
    var postedNotesInitialMarginTop = 0;
    //     - Misc
    var noteBoxOffset = 75;
    var postedNotesOffset = 100;
    var windowOffset = 100;
    var growLimit = 500;
    var paginationOffset = 12;
    var notesCurrentPage = 2; // start with page 2
    var $window = $(window);
    var nextSearchedNotesUrl;

    // Jquery version of variables
    var _noteTextArea;
    var _keyInput;

    //******************************************************************************** 
    // ANIMATIONS
    //******************************************************************************** 
    
    /* 
     * Hide the post button and max width search text input
     * */
    $searchInput.focus(function() {
        togglePostButton("hide");

        // Remove readonly. We use readonly because of fucking auto filling of this input
        $searchInput.removeAttr("readonly");
    }); // end of searchInput focus

    /* 
     * Show the post button when search input not in focus
     * */
    $searchInput.focusout(function() {
        togglePostButton("show");
    }); // end of searchInput focusout

    //******************************************************************************** 
    // UTILS
    //******************************************************************************** 
    
    /*
     * Toggle post button in notebox bottom panel
     *
     * @arg show or hide
     * */
    var togglePostButton = function(action) {
        var buttonWidth = $postBtn.width();
        var $searchIcon = $("#search-icon");
        // Show
        if (action == "hide") {
            $postBtn.animate({
                "margin-right": -buttonWidth + "px"
            }, {
                duration: 100,
                easing: "easeOutQuint",
                complete: function() {
                    $(this).fadeOut(100);
                },
            });

            $searchIcon.css("color", "rgba(34, 162, 185, 0.7)");
        } else if (action == "show") {
            // Hide
            $postBtn.css("margin-right", -buttonWidth + "px");
            $postBtn.show();
            $postBtn.animate({
                "margin-right": "0px",
            }, {
                duration: 100,
                easing: "easeOutQuint",
            });

            $searchIcon.css("color", "rgb(191, 190, 190)");
        } else {
            return null;
        }

    }; // end of togglePostButton

    /* 
     * Register function to onscroll event 
     * */
    var loadOnScroll = function(callback) {
        // Remove last event handler first
        $window.off("scroll");

        $window.on("scroll", function() {
            if ($window.scrollTop() + $window.height() == $(document).height()) {
                callback();
            }
        }); // end of window
    }; // end of loadOnScroll


    /*
     * Render other pages of searched notes
     *
     * */
    var renderSearchedNotesNext = function() {
        // Check if search input is null. if it is not null then we will
        // render next page of searched notes
        if ($searchInput.val() == "") {
            alert("[!] Query is null");
            return;
        }

        if (nextSearchedNotesUrl == "") {
            alert("[!] No more searched notes: " + nextSearchedNotesUrl);
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
                nextSearchedNotesUrl = json.next;
                console.log("[+] Next searched notes url: " + nextSearchedNotesUrl);

                // Render the notes
                $.each(json.results, function(index, note) {
                    if (isNoteAlreadyRendered(note.id, "notes-bottom-button") == true) {
                        console.log("[!] Note is already in the dom: " + note.id);
                        return true;
                    }

                    // Append the rendered data to notesHtml
                    notesHtml += jsonToNote(note);
                }); // end of each

                // Put it on to the dom
                $postedNotes.append(notesHtml);
            }, 
            error: function(xhr) {
                alert("174: " + xhr.status + ": " + xhr.responseText);
            },
        }); // end of ajax


    }; // end of renderSearchedNotesNext

    /* 
     * Render default notes 
     * */
    var renderNotes = function() {
        $.ajax({
            // start in page 2 because we already rendered the first page
            url: "/api/notes/?page=" + notesCurrentPage,
            type: 'get',
            dataType: 'json',
            statusCode: {
                404: function(xhr) {
                    // No more older posts
                },
            },
            beforeSend: function() {
                // Show the animation
                console.log("[!] Loading animation showed!");
                toggleNotesLoadingAnim('show');
            },
            success: function(result) {
                // Point to next page
                notesCurrentPage++;

                var notesHtml = "";
                // Iterate through the result
                $.each(result.results, function(index, data) {
                    // Check if it's already in the dom
                    if (isNoteAlreadyRendered(data.id) == true) {
                        console.log("[!] Note is already in the dom: " + data.id);
                        return true; // continue to next data
                    }


                    notesHtml += jsonToNote(data);
                    
                }); // end of each
                
                $postedNotes.append(notesHtml);

            },
            complete: function() {
                // Hide loading animation
                console.log("[!] Loading animation hid");
                toggleNotesLoadingAnim('hide');
            },
        });
    }; // end of renderNotes

    
    /* 
     * Show the key form
     *
     * */
    var showKeyForm = function(eventHandler, customLabel) {

        var lightBoxKey = document.getElementById("lightbox-key");
        var dimmer = document.createElement("div");
        var closeBtn = document.getElementById("lightbox-key-close");
        var _keySubmitLabel = $(keySubmitLabel);
        var $keySubmitBtn = $("#key-submit-btn");

        // Set custom label
        $keySubmitBtn.text(customLabel)

        dimmer.style.width = window.innerWidth + "px";
        dimmer.style.height = window.innerHeight + "px";
        dimmer.className = "dimmer";

        dimmer.onclick = function() {
            document.body.removeChild(this);
            lightBoxKey.style.visibility = "hidden";
        };

        closeBtn.onclick = function() {
            document.body.removeChild(dimmer);
            lightBoxKey.style.visibility = "hidden";
        };

        document.body.appendChild(dimmer);

        lightBoxKey.style.visibility = "visible";

        // Reset 
        console.log("[!] Keysubmit label: " + _keySubmitLabel.text());
        if (_keySubmitLabel.text() != "Key") {
            _keySubmitLabel.text("Key");
            $(keySubmit).css("border-bottom-color", "rgba(191, 190, 190, 0.42)");
        }

        keySubmit.value = "";
        keySubmit.focus();
        console.log("[!] Keysubmit: " + keySubmit);

        keySubmitForm.onsubmit = eventHandler;
    }; // end of showKeyForm
    

    /* 
     * Convert json to hash-panel for category information
     *
     * */
    var jsonToHashtag = function(json, searchQuery) {
        var hashtagHtml = "";

        hashtagHtml += '<section id="hashtag-panel">';
        hashtagHtml += '<div id="hashtag-main">';
        hashtagHtml += '<h1 id="hashtag">' + searchQuery + '</h1>';
        hashtagHtml += '</div>'; // end of hashtag-main


        hashtagHtml += '<div id="hashtag-info">';
        hashtagHtml += '<ul>';
        hashtagHtml += '<li><strong>' + json.notes_count + 
            '</strong> notes found</li>';

        // Put other categories

        console.log("[!] Categories: " + json.categories);
        if (json.results.length != 0) {
            hashtagHtml += '<li>';
            hashtagHtml += '<p>Other categories also included by users</p>';
            $.each(json.results, function(index, category) {
                hashtagHtml += '<a class="other-hashtags" href="#">#' + 
                    category.category + '</a>';
            }); // end of each
            hashtagHtml += '</li>';
        }

        hashtagHtml += '</ul>';
        hashtagHtml += '</div>'; // end of hashtag-info
        hashtagHtml += '</section>'; // end of section

        return hashtagHtml;
    }; // end of jsonToHashtag


    /*
     * Convert json object to a notes html template
     *
     * @arg json - json to get values from
     * @return noteHtml - html template of note with values
     * */
    var jsonToNote = function(json) {
        var noteHtml = "";
        noteHtml += '<div class="notes">';
        noteHtml += '<p class="note-date">' + json.date_created_timeago + '</p>';
        
        // Truncate the note message
        if (json.note.length > readMoreSize) {
            noteHtml += '<p class="note-message"><p class="note-short">' +
                json.note.substring(0, readMoreSize) + '...</p><p class="note-full"' + 
                'style="display: none;">' + json.note + '</p></p>';
            noteHtml += '<button class="read-more">' + 
                '<i class="fa fa-chevron-circle-down"></i>Read more</button>';
        } else {
            noteHtml += '<p class="note-message">' + json.note + '</p>';
        }


        if (json.categories.length != 0) {
            console.log("[!] Categories detected!: " + json.categories);
            noteHtml += '<div class="note-categories">';

            $.each(json.categories, function(index, category) {
                noteHtml += '<a href="#" class="note-category">' + 
                    category.category + '</a>';
                console.log("[+] Adding category: " + category.category)
            });

            noteHtml += '</div>' // end of note categories
        }

        noteHtml += '<div class="notes-bottom-panel">';

        noteHtml += '<div class="add-to-vault-count fa fa-archive">';
        noteHtml += '<span>';
        if (json.reposters_count != 0) {
            noteHtml += json.reposters_count;
        }
        noteHtml += '</span>'; 
        noteHtml += '</div>'; // end of class add-to-vault

        noteHtml += '<button class="bottom-panel-button add-to-vault-btn" data-notepk="' + 
            json.id + '">';
        noteHtml +=  '<i class="fa fa-plus"></i>';
        noteHtml += 'Add to vault';
        noteHtml += '</button>';

        noteHtml += '</div>'; // end of class notes-bottom-panel

        noteHtml += '</div>'; // end of class notes

        return noteHtml;
    }; // end of jsonToNote


    //******************************************************************************** 
    // Event handlers
    //******************************************************************************** 
    
    /* 
     * Add to vault event handler for key form 
     *
     * */
    var addToVaultEventHandler = function(event) {
        event.preventDefault();

        var lightBoxKey = document.getElementById("lightbox-key");
        var dimmer = document.getElementsByClassName("dimmer")[0];

        var error_400 = function(xhr) {
            // Wrong key
            $("#key-submit-label").text('Wrong key');
            $("#key-submit").css("border-bottom-color", "rgba(231, 76, 60, 0.72)");
        };

        console.log("[!] Getting key...");
        $.when(getTokenWithKey(keySubmit.value, error_400)).done(function(data) {
            var lightBoxKey = document.getElementById("lightbox-key");

            console.log(JSON.stringify(data));

            // Save token and hide key form
            console.log("[!] Saving token : " + data.token);
            saveToken(data.token);

            document.body.removeChild(dimmer);
            lightBoxKey.style.visibility = "hidden";
        }); // end of when


        return false;
    }; // end of addToVaultEventHandler

    /* 
     * Get vault event handler for key form
     *
     * */
    var getVaultEventHandler = function(event) {
        event.preventDefault();

        var lightBoxKey = document.getElementById("lightbox-key");
        var dimmer = document.getElementsByClassName("dimmer")[0];

        /* Handler for 400 status code error */
        var error_400 = function(xhr) {
            // Wrong key
            $("#key-submit-label").text('Wrong key');
            $("#key-submit").css("border-bottom-color", "rgba(231, 76, 60, 0.72)");
        };

        console.log("[!] Getting token...");
        $.when(getTokenWithKey(keySubmit.value, error_400))
            .done(function(data) {
                console.log("[+] Saving new token: " + data.token);
                saveToken(data.token);
        });

        console.log("[!] Getting vault page...");
        $.when(function() {
            return $.ajax({
                url: '/api/vault/get_vault_url/',
                type: 'post',
                data: {key: keySubmit.value},
                dataType: 'json',
                statusCode: {
                    400: error_400,
                },
            }); // end ajax
        }()).done(function(data) {
            console.log(JSON.stringify(data));

            // Decrement the session counter before redirecting
            decrementBrowserTabCount();
            
            // Redirect to vault page
            window.location.replace("/vault/" + data.encoded_url);
            return false;
        });

        //document.body.removeChild(dimmer);
        //lightBoxKey.style.visibility = "hidden";
        
        return false;
    };

    
    /*
     * Resize the notebox based on the value of it
     * @global function
     *
     * */
    var resize = function() {
        // Reset the height of the modified elements
        noteTextArea.style.height = "";
        noteTextArea.style.height = Math.min(noteTextArea.scrollHeight,
                growLimit) + "px";
        //console.log("note-textarea: height=" + noteTextArea.style.height);

        // Same as above
        noteBox.style.height = "";
        noteBox.style.height = Math.min(noteTextArea.scrollHeight, growLimit)
                                + noteBoxOffset + "px";
        //console.log("notebox: height=" + noteBox.style.height);

        // Reset margin-top
        postedNotes.style.marginTop = "";
        postedNotes.style.marginTop = Math.min(noteTextArea.scrollHeight, 
                growLimit) + postedNotesOffset + "px";
        //console.log("posted-notes: margin-top=" + postedNotes.style.marginTop);

        // Initialize once the height of noteBox and the marginTop of posted-notes
        if (noteBoxInitialHeight == 0) {
            // Get the height of textarea without value for minimum height
            if (noteTextArea.value.length != 0) {
                //console.log("Text area with data");

                tmp_value = noteTextArea.value;
                noteTextArea.value = '';

                // Reset the height
                noteTextArea.style.height = "";
                noteTextArea.style.height = Math.min(noteTextArea.scrollHeight,
                        growLimit) + "px";

                noteBox.style.height = "";
                noteBox.style.height = Math.min(noteTextArea.scrollHeight,
                        growLimit) + noteBoxOffset + "px";
                noteBoxInitialHeight = noteBox.clientHeight;

                postedNotes.style.marginTop = "";
                postedNotes.style.marginTop = Math.min(noteTextArea.scrollHeight,
                        growLimit) + postedNotesOffset + "px";
                postedNotesInitialMarginTop = $("#posted-notes").css('margin-top');

                // Put the data back in text area
                noteTextArea.value = tmp_value;

            } else {
                //console.log("Text area without data");
                noteBoxInitialHeight = noteBox.clientHeight;
            } // end of if noteTextArea
        }  // end of if noteBoxInitialHeight

        // Save the first margin-top value of posted-notes
        if (postedNotesInitialMarginTop == 0) {
            postedNotesInitialMarginTop = $('#posted-notes').css('margin-top');
        }

        // Scroll along when user typing a lot
        if (noteBox.scrollHeight >= window.innerHeight - windowOffset) {
            window.scrollTo(0, window.innerHeight - (windowOffset * 3));
        }

    } // end of resize function

    /*
     * Toggle show/hide of the key form in the notebox
     *
     * @global function
     *
     * */
    toggleKeyForm = function(clear, dont_flip) {
        clear = clear || false;
        dont_flip = dont_flip || false;

        // Clear the input, textarea, etc
        if (clear === true) {
            noteTextArea.value = "";
            keyInput.value = "";

            // Don't show the key form anymore
            if (dont_flip === true) {
                return false;
            }
        }

        // Show the key form
        if (popupKeyForm.style.display == 'none') {
            popupKeyForm.style.display = 'block';
            //console.log("Key form showed!");

            // Focus the input in key-input
            keyInput.focus();

            // Reset the height and margin-top to default (initial)
            noteBox.style.height = noteBoxInitialHeight + "px";
            noteTextArea.style.height = (noteBoxInitialHeight - noteBoxOffset) 
                                    + "px";
            postedNotes.style.marginTop = postedNotesInitialMarginTop;
        } else {
            // Hide the key form
            popupKeyForm.style.display = 'none';
            //console.log('Key form hid!');

            // Focus the input in note-textarea
            noteTextArea.focus();

            // Resize it again because they click back button
            resize();
        }
    } // end of toggleKeyForm




    //************************************************************************* 
    // Register event handlers
    //************************************************************************* 


    /*
     * Show the post button if it's hidden when the focus is in note
     * text area
     * */
    $noteTextArea.focus(function() {
        if ($postBtn.css("display") == "none") {
            console.log("[!] Showing post buton...");
            togglePostButton("show");
        }
    }); // end of noteTextArea onfocus
    
    /*
     * Everytime the user type in the note box, it will resize according to the value
     *
     * */
    noteTextArea.onkeyup = function() {
        resize();
        //console.log("User typing...");
    }; // end of noteTextArea onykeyup

    /*
     * Don't submit anything when user press enter
     * */
    postNoteForm.onsubmit = function(event) {
        event.preventDefault();
        console.log("[!] Preventing post note form to submit...");
        return false;
    }; // end of postNoteForm onsubmit


    /* 
     * Search notes while typing
     *
     * */
    $searchInput.keyup(function(event) {
        // Don't execute if it's not number or letters
        // Keycodes used below: letters, numbers, backspace, enter
        if ((event.which >= 48 && event.which <= 105) || event.which == 8 ||
                event.which == 13) {

            delay(function() {
                
                // Reset notes current page for rendering default notes later
                if (notesCurrentPage != 1) {
                    notesCurrentPage = 1;
                }
                var searchQuery = $searchInput.val();

                // Check if search query is null
                if (searchQuery == "") {
                    // Clear old notes
                    $postedNotes.empty();

                    // Render default notes
                    renderNotes();

                    // Re-register onscroll event
                    console.log("[!] Registering renderNotes onscroll");
                    loadOnScroll(renderNotes);
                    return;
                }


                // Registering new event for onscroll event
                console.log("[!] Registering renderSearchedNotesNext onscroll");
                loadOnScroll(renderSearchedNotesNext);


                // Search now!
                $.ajax({
                    url: "/api/notes/search/?query=" + 
                        encodeURIComponent(searchQuery),
                    method: "get",
                    dataType: "json",

                    beforeSend: function() {
                        // Remove all notes first
                        $postedNotes.empty();

                        // Show the animation
                        toggleNotesLoadingAnim("show");
                    },
                    success: function(json) {
                        // Show message when result is empty
                        if (json.results.length <= 0) {
                            $postedNotes.prepend("Didn't match any notes");
                            return;
                        }

                        var notesHtml = "";

                        // Extract the next url
                        nextSearchedNotesUrl = json.next;
                        console.log("[+] Next url: " + nextSearchedNotesUrl);

                        // Render the notes
                        $.each(json.results, function(index, note) {
                            if (isNoteAlreadyRendered(note.id) == true) {
                                console.log("[-] Note is already in the dom: " + note.id);
                                return true; // continue to next note
                            } // end of if

                            // Append the data to notesHtml
                            notesHtml += jsonToNote(note);
                        }); // end of each

                        // Now add to the dom
                        $postedNotes.prepend(notesHtml);
                    },
                    error: function(xhr) {
                        // TODO
                        alert("651: " + xhr.responseText + ": " + xhr.status);
                    },
                    complete: function() {
                        // Hide loading animation
                        toggleNotesLoadingAnim("hide");


                        // Get information of category if it's a search by category
                        if (searchQuery[0] == "#") {
                            console.log("[!] Getting categoriy info of " + 
                                    searchQuery);
                            $.ajax({
                                url: "/api/categories/get_info/?query=" + 
                                    encodeURIComponent(searchQuery),
                                method: "get",
                                dataType: "json",

                                success: function(result) {
                                    console.log(JSON.stringify(result));

                                    console.log("Rendering category information...");
                                    $postedNotes.prepend(jsonToHashtag(result, 
                                                searchQuery));
                                },
                                error: function(xhr) {
                                    alert("692: " + xhr.status + ": " + xhr.responseText);
                                },
                            }); // end of ajax
                        } // end of if searchQuery == #

                    },
                }); // end of ajax





            }, 1000); // 1 second delay, end of delay

        } else {
            console.log("[!] Key pressed: " + event.which);
            return;
        } // end of if event.which

    }); // end of searchInput

    /* 
     * Toggle hide key form
     *
     * */
    closeKeyFromBtn.onclick = function() {
        toggleKeyForm();
        //console.log("Back button clicked!");
    };


    /* 
     * Open lightbox for key submission
     *
     * */
    vaultBtn.onclick = function() {
        showKeyForm(getVaultEventHandler, "Open");
    };


    /* 
     * Read more click handler
     *
     * */
    $(postedNotes).on('click', '.read-more', function() {
        var $this = $(this);

        // Show the full note
        $this.siblings('.note-short').hide();
        $this.siblings('.note-full').show();

        // Remove the "Read more" button
        $this.remove();
    });
    

    
    /* 
     * Add note to vault
     *
     * NOTE: Even it's dynamically added to the dom we can still add th event
     * handler using this method
     * */
    $('body').on('click', '.add-to-vault-btn', function() {
        var token;
        var caller = $(event.target);
        var _addToVaultBtn = caller.contents().filter(function() {
                        return this.nodeType === 3;
                    })[0];

        var add_to_vault_count = caller.siblings().children().text()
        if (add_to_vault_count.trim() == "" ||
                add_to_vault_count.trim().length == 0) {
            add_to_vault_count = 0
        }

        console.log("[+] Note id: " + caller.data("notepk"));

        token = getToken();
        console.log("[+] Token: " + token);

        // If we don't have token we will get one
        if (token == null) {
            // Show the key form and get token
            console.log("[!] Showing the key form");
            showKeyForm(addToVaultEventHandler, "Authenticate");
        }

        if (_addToVaultBtn.textContent == "Add to vault") {
            // if we got a local token 
            $.ajax({
                url: "/api/notes/" + caller.data("notepk") + "/add_to_vault/",
                type: 'get',
                dataType: 'json',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("Authorization", "JWT " + token);
                },
                statusCode: {
                    400: function(xhr) {
                        // Maybe already added or you're the author
                        //caller.contents().filter(function() {
                            //return this.nodeType === 3;
                        //})[0].textContent = 'Already added';
                        _addToVaultBtn.textContent = "Already added";
                        setTimeout(function() {
                            _addToVaultBtn.textContent = "Remove from vault";
                        }, 500) // delay 500 ms
                    },
                    401: function(xhr) {
                        //  When the token expired get new token
                        //  TODO
                    },
                },
                success: function(data) {
                    add_to_vault_count = parseInt(add_to_vault_count) + 1;
                    if (add_to_vault_count == 0) {
                        add_to_vault_count = "";
                    }
                    caller.siblings().children().text(add_to_vault_count);
                    console.log("[+] Added to vault: " + add_to_vault_count);
                    _addToVaultBtn.textContent = "Remove from vault";
                },
                error: function(xhr) {
                    alert("770: " + xhr.responseText + ": " + xhr.status);
                },
            });
        } else if (_addToVaultBtn.textContent == "Remove from vault") {
            // Remove this from vault
            console.log("[-] Removing from vault...");
            $.ajax({
                url: "/api/notes/" + caller.data("notepk") + "/remove_from_vault/",
                type: 'get',
                dataType: 'json',
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("Authorization", "JWT " + token);
                },
                statusCode: {
                    400: function(xhr) {
                        console.log("[!] Error: " + xhr.status);
                    },
                    401: function(xhr) {
                        // Token expired
                        console.log("[!] Error: " + xhr.status);
                    },
                },
                success: function(data) {
                    add_to_vault_count = parseInt(add_to_vault_count) - 1;
                    // If vault count <= 0 then vault count = ''
                    if (add_to_vault_count <= 0) {
                        add_to_vault_count = '';
                        caller.parent().parent().remove();
                    }
                    
                    caller.siblings().children().text(add_to_vault_count);
                    _addToVaultBtn.textContent = "Add to vault";
                },
                error: function(xhr) {
                    alert("804: " + xhr.responseText + ": " + xhr.status);
                    console.log("data: " + JSON.stringify(data));
                },
            });
        } else if (_addToVaultBtn.textContent == "Already added") {
            _addToVaultBtn.textContent = "Remove from vault";
        }

    }); // end of addToVaultBtn
    
    
    /*
     * Send the note to server
     *
     * */
    postNoteBtn.onclick = function() {

        // Check if key input is not empty
        if (keyInput.value.trim().length == 0) {
            _keyInput = $(keyInput);
            $("#key-label").text("Please enter your key");
            _keyInput.css("border-bottom-color", "rgba(231, 76, 60, 0.72)");
            return false;
        } else {
            // Note is not empty. If it just a corrected error then we revert the changes we made
            if (_keyInput != null) {
                _keyInput.attr("placeholder", "Relax and take notes");
                _keyInput.css("border-bottom-color", "rgba(191, 190, 190, 0.42)");
                _keyInput = null;
            }
        } // end of else


        var note = {
            note: noteTextArea.value,
        };


        /*
         * 400 error handler for getTokenWithKey
         *
         * */
        var error_400 = function(xhr) {
            $(keyLabel).text("Wrong key");
            $(keyInput).css("border-bottom-color", "rgba(231, 76, 60, 0.72)");
            console.log(xhr.status + ": Bad password");
        };


        $.when(getTokenWithKey(keyInput.value, error_400)).done(function(data) {
            $.ajax({
                url: '/api/notes/',
                type: 'post',
                dataType: 'json',
                data: note,
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("Authorization", "JWT " + data.token);
                },
                success: function(result) {
                    console.log("[+] Success: " + result);
                    var container = $(postedNotes);
                    
                    container.prepend(jsonToNote(result));

                    // Save the token in the session
                    saveToken(data.token);
                    console.log("[!] Just saved it in session and local");
                    
                    // Clear the input element
                    toggleKeyForm(true);
                },
                error: function(xhr) {
                    // TODO: Remove this alert
                    alert("877: " + xhr.responseText + ": " + xhr.status);
                },
            }); // end of ajax
        }); // end of when
    }; // end of postNoteBtn onclick


    /* 
     * Submit the note when we already have a token else show the key form
     *
     * */
    postBtn.onclick = function() {
        //console.log("Post button clicked!")
        var categories;
        var token = getToken();

        console.log("[+] Token: " + token);

        // Check if note is not empty
        if (noteTextArea.value.trim().length == 0) {
            _noteTextArea = $(noteTextArea);
            _noteTextArea.attr("placeholder", "Take some note");
            _noteTextArea.css("border-bottom-color", "rgba(231, 76, 60, 0.72)");
            return false;
        } else {
            // Note is not empty. If it just a corrected error then we revert the changes we made
            if (_noteTextArea != null) {
                _noteTextArea.attr("placeholder", "Relax and take notes");
                _noteTextArea.css("border-bottom-color", "rgba(191, 190, 190, 0.42)");
                _noteTextArea = null;
            }
        } // end of else

        // Extract categories from note
        categories = extractCategories(noteTextArea.value);

        // Check if categories length is greater than 12
        if (categories !== null) {
            for (var i=0; i < categories.length; i++) {
                if (categories[i].length > 15) {
                    // Show error
                    console.log(categories[i] + "length is greater than 15");
                    noteboxTooltip.tooltipster('content',
                            'Categories should not be longer than 15 characters');
                    noteboxTooltip.tooltipster('show');

                    setTimeout(function() {
                        noteboxTooltip.tooltipster('hide');
                    }, 3000);
                    return false
                }
            } // end of for
        } // end of if



        // Submit the note using the token
        if (token && token !== 'null') {
            var data = {
                note: noteTextArea.value,
            };
        
            $.when(function() {
                return $.ajax({
                    url: '/api/notes/',
                    type: 'post',
                    data: data,
                    dateType: 'json',
                    beforeSend: function(xhr) {
                        xhr.setRequestHeader("Authorization", "JWT "
                                + token);
                    },
                    statusCode: {
                        401: function(xhr) {
                            // Unauthorized. This means the token is expired s
                            // we need to get a new token. Flip the key form
                            console.log("[!] No token. Key form!");
                            console.log("[!] Or expired token");
                            
                            // Clear the storage
                            console.log("[!] Clearing storages...");
                            localStorage.clear();
                            sessionStorage.clear();

                            // Increment browser tab count
                            console.log("[+] Incrementing browser tab count");
                            incrementBrowserTabCount();

                            // Click the post button
                            console.log("[+] Clicking the post button...");
                            $postBtn.trigger("click");

                            //toggleKeyForm();
                        },
                    },
                    error: function(xhr) {
                        alert("973: " + xhr.status + ": " + xhr.responseText);
                    },
                });
            }()).done(function(data) {
                console.log("[!] Success: " + data);
                console.log("[+] Note: " + data.note);

                var container = $(postedNotes);

                // Add it now to the container
                container.prepend(jsonToNote(data));

                // Just clear the input. Don't flip
                toggleKeyForm(true, true); // clear=true, dont_flip=true
            });

        } else {
            // We don't have a token mom. Show the form!
            console.log("[!] Toggle key form");
            toggleKeyForm();
        }

    };
    
    //************************************************************************* 
    //************************************************************************* 
    // Call functions one time after the page loaded
    


    /*
     * Get older notes when scroll reached bottom
     * */
    
    
    // Resize when page load
    resize();
    //console.log("Function resize called");
    
    // Enable tooltip for notebox
    $('.notebox-tooltip').tooltipster({
        trigger: 'custom',
        theme: 'notepik-theme',
        autoClose: true,
        animation: 'swing',
    }); // end of enable tooltip

    // Default on scroll event
    loadOnScroll(renderNotes);

}); // end of document.ready


