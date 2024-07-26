function application_approve(user_id, type, fname, lname, password, image_name, wages_hr, status) {
    // Prepare the data to send to the backend
    var data = {
        user_id: user_id,
        type: type,
        fname: fname,
        lname: lname,
        password: password,
        image_name: image_name,
        wages_hr: wages_hr,
        status: status
    };

    // Send an AJAX request to the Flask backend
    $.ajax({
        type: "POST",
        url: "/application_approve",  // Update with the correct URL for your Flask route
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(response) {
            // Handle success response
            alert("Application Approved");
        },
        error: function(xhr, status, error) {
            // Handle error response
            alert("Error Claiming Application: " + error);
        }
    });
}

function application_reject(user_id, type, fname, lname, password, image_name, wages_hr, status) {
    // Prepare the data to send to the backend
    var data = {
        user_id: user_id,
        type: type,
        fname: fname,
        lname: lname,
        password: password,
        image_name: image_name,
        wages_hr: wages_hr,
        status: status
    };

    // Send an AJAX request to the Flask backend
    $.ajax({
        type: "POST",
        url: "/application_reject",  // Update with the correct URL for your Flask route
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(response) {
            // Handle success response
            alert("Application Rejected");
        },
        error: function(xhr, status, error) {
            // Handle error response
            alert("Error Claiming Application: " + error);
        }
    });
}