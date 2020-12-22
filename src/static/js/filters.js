var selected_filename = document.getElementById("selected_filename").innerHTML.trim()

function getCleanedData(options) {
    var selectedOptions = options.map((soption) => soption.selected == true ? soption.label : null);
    var cleanedOptions = selectedOptions.filter((option) => option != null);
    if (cleanedOptions[0] == 'All') {
        cleanedOptions = ['All'];
    }
    return cleanedOptions
}

function updateSelect(elementId, optionArray) {
    var select = document.getElementById(elementId);
    var options = "";
    for (var e in optionArray) {
        options += "<option " + "value=" + '"' + optionArray[e] + '"' + ">" + optionArray[e] + "</option>";
    }
    select.innerHTML = options;
}

// Change in Portfolio
document.getElementById("portfolio").onchange = function () {
    var allOptions = [...this.options];
    cleanedOptions = getCleanedData(allOptions)

    document.getElementById("portfolio-text").value = cleanedOptions.join();
    document.getElementById("offering-text").value = "";
    document.getElementById("emp-portfolio-text").value = "";
    document.getElementById("emp-offering-text").value = "";
    document.getElementById("client-text").value = "";
    document.getElementById("project-text").value = "";

    var endpoint = 'api/filter-options';
    var api_data = [];
    var post_data = {
        'filename': selected_filename,
        'portfolio': cleanedOptions,
        'offering': ['IG'],
        'emp_portfolio': ['IG'],
        'emp_offering': ['IG'],
        'client': ['IG'],
        'project': ['IG']
    };

    $.ajax({
        method: 'POST',
        data: post_data,
        url: endpoint,
        success: function (data) {
            api_data = JSON.parse(data);
            updateSelect('offering', api_data['offering']);
            updateSelect('emp-portfolio', api_data['emp_portfolio']);
            updateSelect('emp-offering', api_data['emp_offering']);
            updateSelect('client', api_data['client_name']);
            updateSelect('project', api_data['project_name']);
        },
        error: function (error_data) {
            console.log('Cannot fetch chart data')
        }
    });
}


// Change in Offering
document.getElementById("offering").onchange = function () {
    var portfolioOptions = document.getElementById("portfolio");
    cleanedPROptions = getCleanedData([...portfolioOptions.options]);
    var allOptions = [...this.options];
    cleanedOptions = getCleanedData(allOptions)

    document.getElementById("offering-text").value = cleanedOptions.join();
    document.getElementById("emp-portfolio-text").value = "";
    document.getElementById("emp-offering-text").value = "";
    document.getElementById("client-text").value = "";
    document.getElementById("project-text").value = "";

    var endpoint = 'api/filter-options';
    var api_data = [];
    var post_data = {
        'filename': selected_filename,
        'portfolio': cleanedPROptions,
        'offering': cleanedOptions,
        'emp_portfolio': ['IG'],
        'emp_offering': ['IG'],
        'client': ['IG'],
        'project': ['IG']
    };

    $.ajax({
        method: 'POST',
        data: post_data,
        url: endpoint,
        success: function (data) {
            api_data = JSON.parse(data);
            updateSelect('emp-portfolio', api_data['emp_portfolio']);
            updateSelect('emp-offering', api_data['emp_offering']);
            updateSelect('client', api_data['client_name']);
            updateSelect('project', api_data['project_name']);
        },
        error: function (error_data) {
            console.log('Cannot fetch chart data')
        }
    });
}

// Change in Emp-Portfolio
document.getElementById("emp-portfolio").onchange = function () {
    var portfolioOptions = document.getElementById("portfolio");
    cleanedPROptions = getCleanedData([...portfolioOptions.options]);
    var offeringOptions = document.getElementById("offering");
    cleanedOFOptions = getCleanedData([...offeringOptions.options]);
    var allOptions = [...this.options];
    cleanedOptions = getCleanedData(allOptions)

    document.getElementById("emp-portfolio-text").value = cleanedOptions.join();
    document.getElementById("emp-offering-text").value = "";
    document.getElementById("client-text").value = "";
    document.getElementById("project-text").value = "";

    var endpoint = 'api/filter-options';
    var api_data = [];
    var post_data = {
        'filename': selected_filename,
        'portfolio': cleanedPROptions,
        'offering': cleanedOFOptions,
        'emp_portfolio': cleanedOptions,
        'emp_offering': ['IG'],
        'client': ['IG'],
        'project': ['IG']
    };

    $.ajax({
        method: 'POST',
        data: post_data,
        url: endpoint,
        success: function (data) {
            api_data = JSON.parse(data);
            updateSelect('emp-offering', api_data['emp_offering']);
            updateSelect('client', api_data['client_name']);
            updateSelect('project', api_data['project_name']);
        },
        error: function (error_data) {
            console.log('Cannot fetch chart data')
        }
    });
}

// Change in Emp - Offering
document.getElementById("emp-offering").onchange = function () {
    var portfolioOptions = document.getElementById("portfolio");
    cleanedPROptions = getCleanedData([...portfolioOptions.options]);
    var offeringOptions = document.getElementById("offering");
    cleanedOFOptions = getCleanedData([...offeringOptions.options]);
    var empPortfolioOptions = document.getElementById("emp-portfolio");
    cleanedEPROptions = getCleanedData([...empPortfolioOptions.options]);
    var allOptions = [...this.options];
    cleanedOptions = getCleanedData(allOptions)

    document.getElementById("emp-offering-text").value = cleanedOptions.join();
    document.getElementById("client-text").value = "";
    document.getElementById("project-text").value = "";

    var endpoint = 'api/filter-options';
    var api_data = [];
    var post_data = {
        'filename': selected_filename,
        'portfolio': cleanedPROptions,
        'offering': cleanedOFOptions,
        'emp_portfolio': cleanedEPROptions,
        'emp_offering': cleanedOptions,
        'client': ['IG'],
        'project': ['IG']
    };

    $.ajax({
        method: 'POST',
        data: post_data,
        url: endpoint,
        success: function (data) {
            api_data = JSON.parse(data);
            updateSelect('client', api_data['client_name']);
            updateSelect('project', api_data['project_name']);
        },
        error: function (error_data) {
            console.log('Cannot fetch chart data')
        }
    });
}

// Change in Client Name
document.getElementById("client").onchange = function () {
    var portfolioOptions = document.getElementById("portfolio");
    cleanedPROptions = getCleanedData([...portfolioOptions.options]);
    var offeringOptions = document.getElementById("offering");
    cleanedOFOptions = getCleanedData([...offeringOptions.options]);
    var empPortfolioOptions = document.getElementById("emp-portfolio");
    cleanedEPROptions = getCleanedData([...empPortfolioOptions.options]);
    var empOfferingOptions = document.getElementById("emp-offering");
    cleanedEPOFOptions = getCleanedData([...empOfferingOptions.options]);
    var allOptions = [...this.options];
    cleanedOptions = getCleanedData(allOptions);

    document.getElementById("client-text").value = cleanedOptions.join();
    document.getElementById("project-text").value = "";

    var endpoint = 'api/filter-options';
    var api_data = [];
    var post_data = {
        'filename': selected_filename,
        'portfolio': cleanedPROptions,
        'offering': cleanedOFOptions,
        'emp_portfolio': cleanedEPROptions,
        'emp_offering': cleanedEPOFOptions,
        'client': cleanedOptions,
        'project': ['IG']
    };
    $.ajax({
        method: 'POST',
        data: post_data,
        url: endpoint,
        success: function (data) {
            api_data = JSON.parse(data);
            updateSelect('project', api_data['project_name']);
        },
        error: function (error_data) {
            console.log('Cannot fetch chart data')
        }
    });
}

// Change in Project Name
document.getElementById("project").onchange = function () {
    var allOptions = [...this.options];
    cleanedOptions = getCleanedData(allOptions)
    document.getElementById("project-text").value = cleanedOptions.join();

}