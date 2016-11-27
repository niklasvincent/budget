$(function() {
    $.ajax({
      url: "/api/v1.0/expenses/this_month",
      // Work with the response
      success: function(response) {
        var renderSummary = Handlebars.compile($('#summary-template').html());
        $('#main').append(
            renderSummary({
                total: response.total_sum
            })
        );


        var renderExpenses = Handlebars.compile($('#expense-template').html());
         for (var group in response.expenses_by_group) {
            $('#main').append(
                renderExpenses({
                    group: group,
                    total: response.total_sum_by_group[group],
                    expenses: response.expenses_by_group[group]
                })
            );
         }
      }
  });
});