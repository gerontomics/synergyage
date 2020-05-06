jQuery(function ($) {

	// path & tissue at sliding
	$('#gene_carousel').bind('slid.bs.carousel', function () {
		var $item = $('#gene_carousel .item.active');
		var name = $item.data('name');
		var no_mutations = $item.data('mutations');
		kegg_info(name, no_mutations, 1, '#gene_carousel .item.active', 'Select pathway', null);
		tissue_expression(name);
	});


	// select neighbours
	$('.select-neighbours').unbind('click').on('click', function () {
		var gene = $('#gene_carousel .item.active').data('name');
		var neighbours = cy.filter('node[genes = "' + gene + '"]').neighbourhood().nodes();
		cy.filter(neighbours).select();
	});

});


function update_node_details() {
	var $box = $('#cy_info .content .carousel-inner');
	var $items = $box.find('.item');
	var active_items = $box.find('.item.active').length;
	var initial_no_nodes = $items.size();
	var $first_item = $items.first();

	if (initial_no_nodes > 0) {
		// show container
		$('#cy_info').show();
		// show distraction mode
		$('#distraction_mode').removeClass('hidden');
	} else {
		// show container
		$('#cy_info').hide();
		// hide distraction mode
		$('#distraction_mode').addClass('hidden');
		// remove distraction mode from nodes & genes
		var nodes = cy.filter('node');
		var edges = cy.filter('edge');
		nodes.removeClass('distraction-mode').addClass('not-distraction');
		edges.removeClass('distraction-mode').addClass('not-distraction');
	}

	if (initial_no_nodes === 1 || active_items < 1) {
		$first_item.addClass('active');
		// path & tissue for first slide
		kegg_info($first_item.data('name'), $first_item.data('mutations'), 1, '#gene_carousel .item.active', 'Select pathway', null);
		tissue_expression($first_item.data('name'));
	}

	if (initial_no_nodes > 1) {
		// show carousel controls
		$('#gene_carousel .carousel-control').removeClass('hidden');
		// show number of genes
		$('#gene_carousel .count-genes').removeClass('hidden').find('strong').text(initial_no_nodes);
	} else {
		// hide carousel controls
		$('#gene_carousel .carousel-control').addClass('hidden');
		// hide number of genes
		$('#gene_carousel .count-genes').addClass('hidden').find('strong').text('');
	}
}


function remove_node_details(node_id) {
	$('#cy_info .content .carousel-inner .item[data-id="' + node_id + '"]').remove();

	update_node_details();
}


function add_node_details(node) {
	var html = '';
	var $box = $('#cy_info .content .carousel-inner');

	var data = node['_private']['data'];

	var max_lifespan = Math.round(data['max_lifespan_'] * 100) / 100;
	var min_lifespan = Math.round(data['min_lifespan_'] * 100) / 100;
	var avg_lifespan = Math.round(data['avg_lifespan_'] * 100) / 100;
	var id = data['id'];
	var name = data['genes'];
	var url = data['name'];
	var no_mutations = data['No_mutations'];
	var no_studies = data['number'];

	// for wildtype it's a different page
	if (name && name.toLowerCase() === 'wild type') url = 'wildtype';

	html += '<div class="item" data-id="' + id + '" data-name="' + name + '" data-mutations="' + no_mutations + '">';
	html += '<div class="title">' + name;
	html += ' <a href="/details/' + url + '">(details <i class="fa fa-external-link" aria-hidden="true"></i>)</a>';
	html += ' </div>';
	html += '<div class="extra-padding">';
	html += 'Average lifespan: <strong>' + avg_lifespan + '</strong>';
	html += ' days';
	html += '<br>';
	html += 'Lifespan interval: [<strong>' + min_lifespan + '</strong> - <strong>' + max_lifespan + '</strong>] days';
	html += '<br>';
	html += 'Number of studies: <strong>' + no_studies + '</strong>';
	html += '</div>';
	html += '<div class="kegg-info"></div>';
	html += '<div class="tissue-expression"></div>';
	html += '</div>';

	// info box
	$box.append(html);

	update_node_details();

	// open specific slide
	$('#gene_carousel .item').removeClass('active');
	$('#gene_carousel .item[data-id="' + id + '"]').addClass('active');
}


function kegg_info(name, no_mutations, min_mutations, active_container, placeholder, tax_id) {
	var active_select_html = '';
	var inactive_option_value = '_';

	var $active_container = $(active_container);
	var $active_kegg_info = $active_container.find('.kegg-info');

	var $active_pathway = $('.active-pathway');
	var $active_pathway_close = $('.active-pathway .fa-times-circle');
	var $active_pathway_label = $('.active-pathway span');

	// get options in select
	if (no_mutations === min_mutations && $active_kegg_info.html() === '') {
		$.ajax({
			url: '/ajax/keggInfo/',
			async: false,
			data: {
				'name': name,
				'tax_id': tax_id
			},
			dataType: 'json',
			success: function (data) {
				$.each(data['data'], function (i, kegg) {
					active_select_html += '<option value="' + kegg[0] + '">' + kegg[1] + '</option>';
				});
			}
		});
	}

	// create select with retrived options
	if (active_select_html) {
		$active_kegg_info.html('<select class="change_kegg form-control input-sm"><option disabled="disabled" value="_" selected="selected" style="display: none;">' + placeholder + '</option>' + active_select_html + '</select>');
	}

	// active & inactive select elements
	var $active_select = $active_container.find('.change_kegg');
	var inactive_container = '#cy_pathways';
	if (active_container === '#cy_pathways') {
		inactive_container = '#gene_carousel .item.active';
	}

	$active_select.on('change', function () {
		// show placeholder for inactive select
		var $inactive_select = $(inactive_container).find('.change_kegg');
		$inactive_select.val(inactive_option_value);

		var current_path = $(this).val();

		if (current_path && current_path !== '' && current_path !== inactive_option_value) {
			$.ajax({
				url: '/ajax/keggInfo/',
				async: false,
				data: {
					'path': current_path
				},
				dataType: 'json',
				success: function (response) {
					var genes = [];

					$.each(response['data'], function (key, gene) {
						genes.push('node[genes = "' + gene + '"]');
					});

					cy.filter('node').removeClass('path');
					var filtered_nodes = cy.filter(genes.join(','));
					if (filtered_nodes.length > 0) filtered_nodes.addClass('path');
					else alert('No genes in SynergyAge for this pathway.')
				}
			});
			// show active pathway
			$active_pathway.removeClass('hidden');
			$active_pathway_label.text(current_path);
		} else {
			cy.filter('node').removeClass('path');
			// hide active pathway
			$active_pathway.addClass('hidden');
			$active_pathway_label.text('');
		}
	});

	// close icon
	$active_pathway_close.on('click', function () {
		// show placeholder for active select
		$active_select.val(inactive_option_value).trigger('change');
		// hide active pathway
		$active_pathway.addClass('hidden');
		$active_pathway_label.text('');
	});
}


function tissue_expression(name) {
	var tissue_expression = '';
	var $item = $('#gene_carousel .item.active');
	var $tissue_info = $item.find('.tissue-expression');

	if ($tissue_info.html() === '') {
		$.ajax({
			url: '/ajax/tissue_expression/',
			async: false,
			data: {
				'name': name
			},
			dataType: 'json',
			success: function (data) {
				$.each(data['data'], function (i, tissue) {
					tissue_expression += '<option value="' + tissue[0] + '">' + tissue[0] + '</option>';
				});
			}
		});
	}

	if (tissue_expression)
		$tissue_info.html('<select class="tissue_expression form-control input-sm"><option disabled="disabled" selected="selected" style="display: none;">Select tissue</option><option value="_">No tissue</option>' + tissue_expression + '</select>');

	$('.tissue_expression').on('change', function () {
		var value = $(this).val();

		if (value !== '' && value !== '_') {
			$.ajax({
				url: '/ajax/tissue_expression/',
				async: false,
				data: {
					'tissue': value
				},
				dataType: 'json',
				success: function (data) {
					var genes = [];

					$.each(data['data'], function (key, value) {
						genes.push('node[genes = "' + value + '"]');
					});

					cy.filter('node').removeClass('tissue');
					cy.filter(genes.join(',')).addClass('tissue');
				}
			});
		} else if (value === '_') {
			cy.filter('node').removeClass('tissue');
		}
	});
}