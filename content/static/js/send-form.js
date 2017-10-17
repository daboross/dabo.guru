function sendSuccess(data, textStatus, jqXHR) {
    var $value = $("#send-value");
    $value.show();
    if (textStatus === "success") {
        $value.html("Success!");
    } else {
        $value.html("Error " + data.statusText + "!");
    }
}

function sendFail(data, textStatus, jqXHR) {
    var $value = $("#send-value");
    $value.show();
    $value.html("Failure: " + textStatus + ":" + jqXHR.textStatus + ":" + data);
}

function sendData() {
    var sendForm = $("#send-form");
    var request = $.ajax({
        url: "/notify/",
        type: "POST",
        data: sendForm.val(),
        complete: sendSuccess,
        contentType: "text/plain;charset=UTF-8",
    });
    request.done(sendSuccess);
    request.fail(sendFail);
    sendForm.hide();
    $("#send-button").hide();
    var sendValue = $("#send-value");
    sendValue.show();
}
