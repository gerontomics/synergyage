(function ($) {

	// set PubMed ID input readonly
	$('#id_pmid').attr('readonly', 'readonly');
	// set model name (model_name) input readonly
	$('#id_model_name').attr('readonly', 'readonly');

	$('#id_parent, #id_intervention').on('input', function () {
		var generated_value = $('#id_parent').val() + '(' + $('#id_intervention').val() + ')';
		$('#id_model_name').val(generated_value);
	});

})(django.jQuery);