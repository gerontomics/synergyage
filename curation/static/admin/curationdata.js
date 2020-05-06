(function ($) {

	/**
	 * Get last used ID for mutant ID (mutant_id).
	 * Not used anymore. Fixed by auto increment (AutoField(primary_key=True)).
	 */
	function next_mutant_id() {
		var last_id = $('.field-muutant_mutant_id p').eq(-2).text();

		if (!$.isNumeric(last_id))
			last_id = 0;

		next_id = parseInt(last_id) + 1;

		return next_id;
	}

	/**
	 * Get PubMed ID from curation data input.
	 */
	function get_pubmed() {
		var id = $('#id_pmid').val();

		return id;
	}


	/**
	 * Get values for every mutant and write them on the same row.
	 * @param {integer} mutant_id - The ID of the mutant.
	 * @param {string} element_id - The ID of mutant element. We need to know this to select closest elements to this one.
	 *
	 * !!! - Can be improved by using $(this) and maybe some loop (?).
	 */
	function data_from_popup(mutant_id, element_id) {
		$.ajax({
			url: '/admin/curation/muutant/' + mutant_id + '/change/?_popup=1',
			type: 'GET',
			success: function (data) {
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_mutant_id p')).text(($('#id_mutant_id', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_model_name p')).text(($('#id_model_name', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_parent p')).text(($('#id_parent', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_entrez_id p')).text(($('#id_entrez_id', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_intervention p')).text(($('#id_intervention', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_temperature p')).text(($('#id_temperature', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_diet p')).text(($('#id_diet', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_lifespan p')).text(($('#id_lifespan', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_calorically_restricted p')).text(($('#id_calorically_restricted', data).val()));
				$($('#' + element_id)).parent().parent().parent().find($('.field-muutant_composite_id p')).text(($('#id_composite_id', data).val()));
			}
		});
	}


	// when mutant select is changed in inline form section
	$('select[id^="id_CurationData_mutant-"]').on('change', function () {

		// number of options
		var no_options = $('option', this).length;
		var actual_options = $(this).attr('data-old');

		// if we don't have number of old options, save them
		if (!actual_options)
			$(this).attr('data-old', no_options);
		// if new number is bigger, do the magic. but, also, increase current number
		if (no_options > actual_options) {
			$('button[name="_continue"]').click();
		}

		// populate columns
		data_from_popup(this.value, this.id);
	})


	$(document).ready(function () {
		var pubmed_id = get_pubmed();

		// remove options from different PubMed IDs
		$('select[id^="id_CurationData_mutant-"] > option').each(function () {
			var option_text = $(this).text();
			// string before first |
			var option_pmid = option_text.substr(0, option_text.indexOf('|'));

			// if it's different, remove from the list
			if (option_pmid != pubmed_id)
				$(this).remove();
		});

		// remove plus button from populated fields
		$('.has_original .add-related').remove();

		// hide select dropdown
		$('select[id^="id_CurationData_mutant-"]').hide();

		// make PubMed ID readonly
		$('#id_pmid').attr('readonly', 'readonly');

		// prepopulate some fields
		$('a.add-related').click(function () {
			var initial_href = $(this).attr('href');

			// remove &pmid=X in case we already changed button href
			var clean_href = initial_href.replace(/&pmid=[0-9]/g, '');

			var new_href = clean_href + '&pmid=' + pubmed_id;

			$('a.add-related').attr('href', new_href);
		});

	});

})(django.jQuery);