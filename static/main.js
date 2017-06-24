$(function() {
    $.ajax({
        url: "/api/v1.0/expenses/this_month",
        success: function(response) {
            var renderSummary = Handlebars.compile($('#summary-template').html());
            $('#main').append(
                renderSummary({
                    total: response.total_sum
                })
            );

            var renderExpenses = Handlebars.compile($('#expense-template').html());
            for (var group in response.total_sum_by_category) {
                $('#main').append(
                    renderExpenses({
                        group: group,
                        categories: response.total_sum_by_category[group],
                        total: response.total_sum_by_group[group],
                    })
                );
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