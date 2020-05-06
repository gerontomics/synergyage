(function ($) {

	// remove "novalidate" attribute for form
	$('#article_form').removeAttr('novalidate');

	// get initial state for current article
	var initial_state = $("#id_state option:selected").text();
	hide_show_reason(initial_state);
	disable_fields(initial_state);

	$("#id_state").change(function () {
		var new_state = $("option:selected", this).text();
		hide_show_reason(new_state);
		// disable_fields(new_state);
	});


	function hide_show_reason(state) {
		if (state == 'Reject') {
			// make "Rejection reason required
			$("#id_rejection_reason").attr('required', 'required');
			// show "Rejection reason" label as required
			$("label[for='id_rejection_reason']").addClass('required');
			// show "Rejection reason" textarea
			$(".field-rejection_reason").show();
		} else {
			// make "Rejection reason" input mandatory
			$("#id_rejection_reason").removeAttr('required');
			// show "Rejection reason" label as mandatory
			$("label[for='id_rejection_reason']").removeClass('required');
			// hide "Rejection reason" textarea
			$(".field-rejection_reason").hide();
		}
	}


	function disable_fields(state) {
		if (state == 'Maybe') {
			$("#id_pmid").removeAttr('readonly');
			$("#id_email").removeAttr('readonly');
			$("#id_citation").removeAttr('readonly');
			$("#id_description").removeAttr('readonly');
		} else {
			$("#id_pmid").attr('readonly', true);
			$("#id_email").attr('readonly', true);
			$("#id_citation").attr('readonly', true);
			$("#id_description").attr('readonly', true);
		}
	}

})(django.jQuery);