$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#pid").val(res.pid);
        $("#name").val(res.name);
        $("#condition").val(res.condition);
        if (res.active == true) {
            $("#active").val("true");
        } else {
            $("#active").val("false");
        }
        $("#quantity").val(res.quantity);
        $("#restock_level").val(res.restock_level);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#name").val("");
        $("#condition").val("");
        $("#active").val("");
        $("#quantity").val("");
        $("#restock_level").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Retrieve Inventory Items with PID
    // ****************************************

    $("#retrieve-btn").click(function () {

        let pid = +$("#pid").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory/${pid}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">PID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">condition</th>'
            table += '<th class="col-md-2">active</th>'
            table += '<th class="col-md-2">quantity</th>'
            table += '<th class="col-md-2">restock_level</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr pid="row_${i}"><td>${item.pid}</td><td>${item.name}</td><td>${item.condition}</td><td>${item.active}</td><td>${item.quantity}</td><td>${item.restock_level}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_form_data(firstItem)
            }

            flash_message("Success")
        });
        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Create Inventory Item
    // ****************************************

    $("#create-btn").click(function () {

        let pid = +$("#pid").val();
        let name = $("#name").val();
        let condition = +$("#condition").val();
        let active = $("#active").val() == "true";
        let quantity = +$("#quantity").val();
        let restock_level = +$("#restock_level").val();

        let data = {
            "pid": pid,
            "name": name,
            "condition": condition,
            "active": active,
            "quantity": quantity,
            "restock_level": restock_level
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Inventory Item
    // ****************************************

    $("#update-btn").click(function () {

        let pid = +$("#pid").val();
        let name = $("#name").val();
        let condition = +$("#condition").val();
        let active = $("#active").val() == "true";
        let quantity = +$("#quantity").val();
        let restock_level = +$("#restock_level").val();

        let data = {
            'pid': pid,
            "name": name,
            "condition": condition,
            "active": active,
            "quantity": quantity,
            "restock_level": restock_level
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/inventory/${pid}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Delete Inventory Items with PID
    // ****************************************

    $("#deleteAll-btn").click(function () {

        let pid = +$("#pid").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/inventory/${pid}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Inventory Items Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pid").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // List All Items
    // ****************************************

    $("#listAll-btn").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: "/inventory",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">PID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">condition</th>'
            table += '<th class="col-md-2">active</th>'
            table += '<th class="col-md-2">quantity</th>'
            table += '<th class="col-md-2">restock_level</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr pid="row_${i}"><td>${item.pid}</td><td>${item.name}</td><td>${item.condition}</td><td>${item.active}</td><td>${item.quantity}</td><td>${item.restock_level}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_form_data(firstItem)
            }

            flash_message("Success")
        });
        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    $("#delete-btn").click(function () {

        let pid = +$("#pid").val();
        let condition = +$("#condition").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/inventory/${pid}/${condition}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Inventory Item Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });
    // ****************************************
    // Search for a item
    // ****************************************

    $("#search-btn").click(function () {
        let pid = +$("#pid").val();
        let name = $("#name").val();
        let condition = +$("#condition").val();
        let active = $("#active").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (condition) {
            if (queryString.length > 0) {
                queryString += '&condition=' + condition
            } else {
                queryString += 'condition=' + condition
            }
        }
        if (active) {
            if (queryString.length > 0) {
                queryString += '&active=' + active
            } else {
                queryString += 'active=' + active
            }
        }

        $("#flash_message").empty();
        let ajax = null
        if(pid==0) {
            ajax = $.ajax({
                type: "GET",
                url: `/inventory?${queryString}`,
                contentType: "application/json",
                data: ''
            })
        } else {
            ajax = $.ajax({
                type: "GET",
                url: `/inventory/${pid}?${queryString}`,
                contentType: "application/json",
                data: ''
            })
        }

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">PID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">condition</th>'
            table += '<th class="col-md-2">active</th>'
            table += '<th class="col-md-2">quantity</th>'
            table += '<th class="col-md-2">restock_level</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr pid="row_${i}"><td>${item.pid}</td><td>${item.name}</td><td>${item.condition}</td><td>${item.active}</td><td>${item.quantity}</td><td>${item.restock_level}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_form_data(firstItem)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

})
