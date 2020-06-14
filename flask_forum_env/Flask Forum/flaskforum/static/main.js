// navigation popup menu 
$(function() { // clicking on the navigation picture will toggle the navigation pop up
    $(".nav-picture").on("click", function() {
        $("#navigation-popup").toggle();
    });
});

$(document).on("click" ,event ,function() { // clicking anything outside of the navigation popup will cause the navigation popup to hide
    let target = event.target;
    if(!($(target).closest("#navigation-popup").length > 0 || $(target).closest('.nav-picture').length > 0)) { // clicking the navigation picture will not hide the navigation popup as this is already handled by another method
        $("#navigation-popup").css("display","none");
    }
});


// --- *global variable start* ---
let prevPopup = null;

// show popup form for updating comment
$(function() {
    $(".comment-dots.vertical-dots").on("click", function() {
        let popup = $(this).closest(".comment-form").find(".dot-popup");  
        if(prevPopup===null) { // if there is no prev element that was clicked just change the clicked element into display block
            popup.css("display","block");
        }
        else if(prevPopup.get(0)===popup.get(0)) { // if the previous clicked element is the same then toggle that element
            popup.toggle();
        }
        else { // if prev element has been clicked and prev element and current element been clicked are different then change the prev element to none and current element to block
            prevPopup.css("display","none");
            popup.css("display","block");
        }
        prevPopup = popup;  
    });
});

// show popup form for updating reply
$(function() {
    $(".reply-dots.vertical-dots").on("click", function() {
        let popup = $(this).closest(".user-reply").find(".dot-popup");
        if(prevPopup===null) {
            popup.css("display","block");
        }
        else if(prevPopup.get(0)===popup.get(0)) { 
            popup.toggle();
        }
        else {
            prevPopup.css("display","none");
            popup.css("display","block");
        }
        prevPopup = popup; 
    });
});

$(document).on("click" ,event ,function() { // if you click anywhere else other than the three vertical dots or the popup from clicking the vertical dots than hide the previously selected popup
    let target = event.target;
    if(!($(target).closest(".dots-popup-boundary").length > 0)) {
        if(prevPopup!==null) {
            prevPopup.css("display","none");
        }
    }
});

// --- *global variable end* ---

// report reply
$(function() {
    $(".reply-dots.dot-report-container").on("click", function() {
        let popup = $(this).closest(".user-reply");
        $(this).closest(".dot-popup").css("display","none");
    });
});

// report comment
$(function() {
    $(".comment-dots.dot-report-container").on("click", function() {
        let popup = $(this).closest(".comment-content");
        $(this).closest(".dot-popup").css("display","none");
    });
});

// update reply
$(function() {
    $(".reply-dots.dot-update-container").on("click", function() {
        let popup = $(this).closest(".user-reply");
        let content = $(popup).find(".user-reply-content").text();
        $(this).closest(".dot-popup").css("display","none");
        $(popup).find(".content-update-reply").val(content);
        $(popup).find(".updateForm-reply").removeClass("hide"); 
    });
});

// update comment
$(function() {
    $(".comment-dots.dot-update-container").on("click", function() {
        let popup = $(this).closest(".comment-content");
        let content = $(popup).find(".user-comment-content").text();
        $(this).closest(".dot-popup").css("display","none");
        $(popup).find(".content-update-comment").val(content);
        $(popup).find(".updateForm-comment").removeClass("hide"); 
    });
});

// hide popup form for updating comments
$(function() {
    $(".cancel-comment").on("click", function() {
        $(this).closest(".updateForm-comment").addClass("hide");
    });
});

// hide popup form for updating reply
$(function() {
    $(".cancel-reply-update").on("click", function() {
        $(this).closest(".updateForm-reply").addClass("hide");
    });
});

// hover over these comment to see three vertical dots
$(function() {
    $(".comment-form").on("mouseover", function() {
        $(this).find(".comment-header .vertical-dots").css("display", "block");
    });
});

// move mouse out of comment to hide three vertical dots
$(function() {
    $(".comment-form").on("mouseleave", function() {
        $(this).find(".comment-header .vertical-dots").css("display", "none");
    });
});

// hover over these reply to see three vertical dots
$(function() {
    $(".user-reply").on("mouseover", function() {
        $(this).find(".reply-header .vertical-dots").css("display", "block");
    });
});

// move mouse out of reply to hide three vertical dots
$(function() {
    $(".user-reply").on("mouseleave", function() {
        $(this).find(".reply-header .vertical-dots").css("display", "none");
    });
});

// clicking reply will show reply comment form
$(function() {
    $(".reply-comment").on("click", function() {
        $(this).siblings(".add-reply-comment").removeClass("hide");
    });
});

// click cancel to hide reply comment form
$(function() {
    $(".cancel-reply").on("click", function() {
        $(this).closest(".add-reply-comment").addClass("hide");
    });
});

// show all replies for a specific comment
$(function() {
    $(".reply-view-more").on("click", function() {
        $(this).siblings(".reply-content").removeClass("hide");
        $(this).siblings(".reply-view-less").removeClass("hide");
        $(this).addClass("hide");
    });
});

// hide all replies for specific comment
$(function() {
    $(".reply-view-less").on("click", function() {
        $(this).siblings(".reply-content").addClass("hide");
        $(this).siblings(".reply-view-more").removeClass("hide");
        $(this).addClass("hide");
    });
});

// changes follow button to LEAVE to signify that clicking this button will unfollow the forum
$(function() {
    $(".forum-unjoin").on("mouseover", function () {
        $(this).text("LEAVE");
    });
});

// changes back to JOINED when mouse is moved out of button to signify the user has already followed this forum
$(function() {
    $(".forum-unjoin").on("mouseleave", function () {
        $(this).text("JOINED");
    });
});

// hide popup confirm delete post form
function closePopup(source) {
    $("body").css("overflow","scroll")
    $("#popup").css("display","none")
}

// show popup confirm delete post form
function openPopup(source) {
    $("body").css("overflow","hidden")
    $("#popup").css("display","block")
}

