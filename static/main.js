function selectMonth() {
    var yearAndMonth = window.location.hash.substr(1);
    if (yearAndMonth) {
        return yearAndMonth;
    }
    return null;
}

$(function() {
    var yearAndMonth = selectMonth();
    var yearAndMonthParameter = yearAndMonth == null ? "this_month" : yearAndMonth;
    var url = "/api/v1.0/expenses/" + yearAndMonthParameter;
    $.ajax({
        url: url,
        success: function(response) {
            var renderSummary = Handlebars.compile($('#summary-template').html());
            $('#main').append(
                renderSummary({
                    year_and_month: yearAndMonth,
                    total: response.total_sum
                })
            );

            var renderExpenses = Handlebars.compile($('#expense-template').html());
            var index = 0;
            for (var group in response.total_sum_by_category) {
                $('#main').append(
                    renderExpenses({
                        index: index,
                        group: group,
                        categories: response.total_sum_by_category[group],
                        total: response.total_sum_by_group[group],
                    })
                );
                index++;
            }
        }
    });

    $('#main').on('show.bs.collapse', function(event) {
            $('#' + event.target.id + "__expand").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
    });

    $('#main').on('hidden.bs.collapse', function(event) {
            $('#' + event.target.id + "__expand").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
    });

});