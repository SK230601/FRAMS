function claim_approve(user_id, user_name, date, break_out, break_in, break_hrs, status, message) {
    // Prepare the data to send to the backend
    var data = {
        user_id: user_id,
        user_name: user_name,
        date: date,
        break_out: break_out,
        break_in: break_in,
        break_hrs: break_hrs,
        status: status,
        message: message
    };

    // Send an AJAX request to the Flask backend
    $.ajax({
        type: "POST",
        url: "/claim_approve",  // Update with the correct URL for your Flask route
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(response) {
            // Handle success response
            alert("Break claim Approved");
        },
        error: function(xhr, status, error) {
            // Handle error response
            alert("Error claiming break: " + error);
        }
    });
}

function claim_reject(user_id, user_name, date, break_out, break_in, break_hrs, status, message) {
    // Prepare the data to send to the backend
    var data = {
        user_id: user_id,
        user_name: user_name,
        date: date,
        break_out: break_out,
        break_in: break_in,
        break_hrs: break_hrs,
        status: status,
        message: message
    };

    // Send an AJAX request to the Flask backend
    $.ajax({
        type: "POST",
        url: "/claim_reject",  // Update with the correct URL for your Flask route
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(response) {
            // Handle success response
            alert("Claim Rejected");
        },
        error: function(xhr, status, error) {
            // Handle error response
            alert("Error claiming break: " + error);
        }
    });
}

function claim(user_id, user_name, date, break_out, break_in, break_hrs, status, message) {
    // Prepare the data to send to the backend
    var data = {
        user_id: user_id,
        user_name: user_name,
        date: date,
        break_out: break_out,
        break_in: break_in,
        break_hrs: break_hrs,
        status: status,
        message: message
    };

    // Send an AJAX request to the Flask backend
    $.ajax({
        type: "POST",
        url: "/claim_break",  // Update with the correct URL for your Flask route
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function(response) {
            // Handle success response
            alert("Break claimed successfully!");
        },
        error: function(xhr, status, error) {
            // Handle error response
            alert("Error claiming break: " + error);
        }
    });
}