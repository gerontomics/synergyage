jQuery(function ($) {

	// init multiselect
	$('.multiselect').multiselect({
		buttonWidth: '100%'
	});


	// click on the first tab
	var first_tab_link = $('#table-nav li:first-child a');
	if (first_tab_link.length === 0) {
		$('#includeall').addClass('active');
	} else {
		first_tab_link.click();
	}

	if (getParameter('page') !== '') {
		$('html, body').animate({
			scrollTop: $('#page-scroll').offset().top - 80
		}, 500);
	}

	$('.gototop').click(function (event) {
		event.preventDefault();
		$('html, body').animate({
			scrollTop: $("body").offset().top
		}, 500);
	});

	$('#id_pubmed').attr('required', 'required');
	// after form is submitted with citation, value remains 2
	$('#id_type').val(1);
	$('a[href="#citation"]').click(function () {
		$('#id_pubmed').removeAttr('required');
		$('#id_citation').attr('required', 'required');
		$('#id_type').val(2);
	});
	$('a[href="#pubmed"]').click(function () {
		$('#id_citation').removeAttr('required');
		$('#id_pubmed').attr('required', 'required');
		$('#id_type').val(1);
	});

	$('#experiments .panel-body .list-header:even ul li').each(function (index) {
		var target = $(this).parent().parent().attr('data-target');
		$(target).children('ul').css('background', '#fffffa');
		$(this).css('background', '#fffffa');
	});

	$('#header-search a').click(function () {
		// hide search icon
		$(this).hide();

		// hide others links in menu, except the one with search
		$('.nav li').css('display', 'none');
		$('#header-search').css('display', 'block');

		// custom width for form
		$('.nav ul, #header-form').css('width', '330px');

		$('#header-form').removeClass('hidden');
	});

	// enable tooltips
	$('[data-toggle="tooltip"]').tooltip();

	// every gene search
	$('.search-submit').on('click', function () {
		var input = $(this).data('input');
		$('#header-form input[name="gene"]').val(input);
		$('#header-form button').click();
	});

	// every gene search
	$('.search-gene').on('click', function () {
		var input = $(this).data('gene');
		$('#header-form input[name="gene"]').val(input);
		$('#header-form button').click();
	});

	$('.show-abstract').on('click', function () {
		$(this).parent().parent().parent().find('.abstract-item').toggleClass('hidden');
	});

	$('#toggle_graph').on('click', function () {
		var clicks = $(this).attr('data-clicks');
		if (clicks % 2 === 0) {
			$(this).html('<i class="fa fa-eye" aria-hidden="true"></i> Show graph').css({'position': 'initial'});
			$('#cy').hide();
			$('#cy_pubmed').hide();
			$('.cy_button').hide();
			$('.cy-search').hide();
			$('#cy_info').hide();
			$('#distraction_mode').hide();
			$('#cy_pathways').hide();
			$(this).show();
		} else {
			$(this).html('<i class="fa fa-eye-slash" aria-hidden="true"></i> Hide graph').css({'position': 'absolute'});
			$('#cy').show();
			$('#cy_pubmed').show();
			$('.cy-search').show();
			$('#cy_info').show();
			$('#distraction_mode').show();
			$('#cy_pathways').show();
			$('.cy_button').css('display', 'inline-block');
		}
		$(this).attr('data-clicks', parseInt(clicks) + 1);
	});

	// distraction mode
	// yellow bg for selected nodes
	$('#distraction_mode').on('click', function () {
		var clicks = $(this).attr('data-clicks');
		var nodes = cy.filter('node');
		var edges = cy.filter('edge');
		if (clicks % 2 === 0) {
			nodes.addClass('distraction-mode').removeClass('not-distraction');
			edges.addClass('distraction-mode').removeClass('not-distraction');
			$(this).html('<i class="fa fa-lightbulb-o" aria-hidden="true"></i> Demphasize selection');
		} else {
			nodes.removeClass('distraction-mode').addClass('not-distraction');
			edges.removeClass('distraction-mode').addClass('not-distraction');
			$(this).html('<i class="fa fa-lightbulb-o" aria-hidden="true"></i> Emphasize selection');
		}
		$(this).attr('data-clicks', parseInt(clicks) + 1);
	});
	$('.toggle-table-results').on('click', function () {
		var clicks = $(this).attr('data-clicks');
		if (clicks % 2 === 0) {
			$(this).removeClass('fa-minus-square');
			$(this).addClass('fa-plus-square');
		} else {
			$(this).addClass('fa-minus-square');
			$(this).removeClass('fa-plus-square');
		}
		$(this).attr('data-clicks', parseInt(clicks) + 1);
	});

	$('#cy_legend').mouseover(function () {
		$('#cy_legend img').removeClass('hidden');
	});
	$('#cy_legend').mouseout(function () {
		$('#cy_legend img').addClass('hidden');
	});

	$('#experiments > .list-header').on('click', function () {
		if ($(this).data('clicked') === 0) {
			expTable($(this).data('name'));
			$(this).data('clicked', 1);
		}
	});

	$('.select-pmid-graph').on('click', function () {
		cy.nodes().removeClass('selected');
		cy.filter('node[pmid=' + $(this).data('pmid') + ']').select().addClass('selected');

		$('html, body').animate({
			scrollTop: $('body').offset().top
		}, 500);

		$('#cy_pubmed').html('');
	});

	// collapse first gene
	if ($('#experiments > .list-header').length === 1) {
		$('#experiments > .list-header').first().click();
	}

	// submit search form while changing select option
	$('#search_form .submit-change').change(function () {
		$('#search_form').submit();
	});

	$('.change-graph').on('click', function () {
		$('.change-graph').removeClass('active');
		$(this).addClass('active');
		showGeneGraph($(this).data('gene'), $(this).data('type'), $(this).data('tax_id'), $(this).data('page_id'));
	});

});


function type_of_interactions(csrf_token) {
	// append type of interaction in browse/search table
	var gene_names = [];
	$('.results-table tr[data-type!="Single mutant"]').each(function () {
		var gene_name = $(this).data('gene-name');
		gene_names.push(gene_name);
	});

	$.ajax({
		url: '/ajax/type_of_interaction/',
		type: 'POST',
		data: {
			'gene_names': gene_names,
			'csrfmiddlewaretoken': csrf_token
		},
		dataType: 'json',
		success: function (data) {
			$('.results-table tr .interaction-type span').html('<em>Not enough data to assess</em>');
			$('.results-table tr[data-type="Single mutant"] .interaction-type span').html('<em>Not applicable</em>');
			var explanations = {
				'Additive (positive)': "The increased lifespan obtained upon the combined interventions is similar to the sum of the individual effects",
				'Almost additive (negative)': "The decreased lifespan obtained with combined interventions is greater than each of the individual effects (both decreasing lifespan), however not larger than their sum",
				'Almost additive (positive)': "The increased lifespan obtained with combined interventions is greater than each of the individual effects (both increasing lifespan), however not larger than their sum",
				'Antagonistic (negative)': "Decreased lifespan effects obtained by individual interventions are reduced to less than the minimal effect among them when a combined intervention occurs",
				'Antagonistic (positive)': "Increased lifespan effects obtained by individual interventions are reduced to less than the minimal effect among them when a combined intervention occurs",
				'Contains dependence': "Based on available data (incomplete set of intermediary mutants), it seems that dependency relationships exist between the individual interventions (i.e. the large effect of some sub-combinations or individual effects are larger if other genes are not intervened upon)",
				'Dependent': "The lifespan effect obtained upon the combined interventions is between the effect individual effects, suggesting that the stronger intervention depends on the weaker intervention not occurring.",
				'Enhancer, opposite lifespan effects': "The effect of one gene intervention is enhanced by another gene intervention that by itself results in an opposite effect.",
				'Opposite lifespan effects of single mutants': "Individual effect on lifespan are opposite and their combined effect is either non-significant or between the individual effects.",
				'Partially known monotony. Negative epistasis': "Based on available data (incomplete set of intermediary mutants), each additional intervention seems to further increase the negative effect on lifespan",
				'Partially known monotony. Positive epistasis': "Based on available data (incomplete set of intermediary mutants), each additional intervention seems to further increase the positive effect on lifespan",
				'Synergistic (negative)': "The decreased lifespan obtained upon the combined interventions is greater to the sum of the individual effects (all decreasing lifespan)",
				'Synergistic (positive)': "The increased lifespan obtained upon the combined interventions is greater than the sum of the individual effects (all increasing lifespan)"
			};
			$.each(data['result'], function (gene_name, values) {
				var total = 0;
				var html = [];
				$.each(values, function (i, value) {
					total += value[1];
				});

				$.each(values, function (i, value) {
					var percetange = value[1] / total * 100;
					html.push('<div><i class="fa fa-question-circle epistasis-line" aria-hidden="true" data-toggle="tooltip" title="' + explanations[value[0]] + '"></i> <a href="/methods#methods_image" class="epistasis-methods-link" data-image="/static/curation/images/types/' + value[0] + '.png">' + value[0] + '</a> in ' + percetange.toFixed(0) + '% of cases') + '</div>';
				});

				$('.results-table tr[data-gene-name="' + gene_name + '"] .interaction-type span').html(html.join(', '));
			});
			$('.results-table tr .interaction-type span').removeClass('hidden');
			$('.epistasis-line').tooltip();

			$('.epistasis-methods-link').mouseenter(function () {
				if ($(this).parent('div').children('div.image').length) {
					$(this).parent('div').children('div.image').show();
				} else {
					var image_name = $(this).data('image');
					var imageTag = '<div class="epistasis-method">' + '<img src="' + image_name + '">' + '</div>';
					$(this).parent('div').append(imageTag);
				}
			});
			$('.epistasis-methods-link').mouseleave(function () {
				$(this).parent('div').children('div.epistasis-method').hide();
			});
		}
	});
}


function species_network(tax_id) {
	var info = '';
	var style = '';
	if (tax_id === 6239) {
		info = '../static/curation/cytoscape/roundworm_info.cyjs';
		style = '../static/curation/cytoscape/roundworm_style.json';
	} else if (tax_id === 7227) {
		info = '../static/curation/cytoscape/fly_network.cyjs';
		style = '../static/curation/cytoscape/style_fly.json';
	} else if (tax_id === 10090) {
		info = '../static/curation/cytoscape/mouse_network.cyjs';
		style = '../static/curation/cytoscape/style_mouse.json';
	}

	$.get(info, function (data) {
		$.get(style, function (style) {

			var json_data = JSON.parse(data);
			var style_data = style[0]['style'];

			var cy = cytoscape({
				container: $('#cy'),
				layout: {name: 'preset'},
				elements: json_data['elements'],
				style: style_data,
				ready: function () {
					window.cy = this;

					// all pathways
					kegg_info(null, 0, 0, '#cy_pathways', 'KEGG Pathways', tax_id);
					$('#cy_pathways').removeClass('hidden');

					// fullscreen
					$('#cy_fullscreen').unbind('click').on('click', function () {
						cytoscapeFull(cy);
						var clicks = $(this).attr('data-clicks');
						if (clicks % 2 === 0) $(this).text('Exit fullscreen mode');
						else $(this).text('Fullscreen mode');
						$(this).attr('data-clicks', parseInt(clicks) + 1);
					});

					// reload graph
					$('#reload_graph').unbind('click').on('click', function () {
						reloadGraph(cy, 'species', null, null, tax_id, null);
					});

					// search
					$('#cy_search').on('keydown', function (e) {
						if (e.which == 13 || e.keyCode == 13) {
							var val = $(this).val();
							var search_type = $('#cy_search_type').val();
							if (val) {
								if (search_type === '1') {
									var exact_match = cy.filter('node[genes="' + val + '"]');
									if (exact_match.length > 0) {
										exact_match.select().addClass('selected'); // exact
										// open exact match slide
										var exact_match_id = exact_match[0]['_private']['data']['id'];
										$('#gene_carousel .item').removeClass('active');
										$('#gene_carousel .item[data-id="' + exact_match_id + '"]').addClass('active');
									} else {
										alert('Nothing found');
									}
								} else if (search_type === '2') {
									var contains = cy.filter('node[genes*="' + val + ';"]');
									var exact = cy.filter('node[genes="' + val + '"]');
									var ends_with = cy.filter('node[genes$="' + val + '"]');
									if (contains.length > 0 || exact.length > 0 || ends_with.length > 0) {
										contains.select().addClass('selected'); // contains
										exact.select().addClass('selected'); // exact
										ends_with.select().addClass('selected'); // ends with
										// open exact match slide
										var exact_id = exact['_private']['data']['id'];
										$('#gene_carousel .item').removeClass('active');
										$('#gene_carousel .item[data-id="' + exact_id + '"]').addClass('active');
									} else alert('Nothing found');
								}
							}
						}
					});
				}

			});

			cy.panzoom({
				maxZoom: 2 // max zoom level
			});

			cy.userZoomingEnabled(false);

			// yellow bg for selected nodes
			cy.filter('node').addClass('not-distraction');

			// node selection & deselection
			cy.on('select', 'node', function (event) {
				add_node_details(event.target);
				event.target.neighborhood('edge').addClass('selected');
			});
			cy.on('unselect', 'node', function (event) {
				remove_node_details(event.target.id());
				event.target.neighborhood('edge').removeClass('selected');
			});
			// tap
			cy.on('tap', 'node', function (event) {
				var state = this['_private']['selected'];
				var ctrl_key = window.event.metaKey || window.event.ctrlKey;
				if (state === true && ctrl_key === false) {
					// alert('catch');
				}
			});

		});
	});
}

function reloadGraph(cy, graph, gene, type, tax_id, page_id) {
	// first, deselect all the nodes to hide infobox (carousel)
	cy.nodes().unselect();
	cy.destroy();

	if (graph === 'species')
		species_network(tax_id);
	else if (graph === 'details')
		showGeneGraph(gene, type, tax_id, page_id);
}

function selectPubmed(nodes) {
	var element = $('#cy_pubmed');
	// if we have at least one node
	if (nodes && nodes[0] || pmid) {
		var pmid = nodes[0]['_private']['data']['pmid'];

		element.html('Select genes with PubMED: <em>' + pmid + '</em>');
		element.removeClass('hidden');

		element.unbind('click').on('click', function () {
			cy.nodes().removeClass('selected');
			cy.filter('node[pmid=' + pmid + ']').select().addClass('selected');
		});
	} else {
		element.addClass('hidden');
	}
}

function infoGeneBox(nodes, neighbours) {
	var html = '';
	var box = $('#cy_info .content');

	html += '<div id="gene_carousel" class="carousel slide" data-ride="carousel" data-interval="false">';

	html += '<div class="carousel-inner">';

	var count = nodes.length;

	$.each(nodes, function (i, data) {

		if (i === 0)
			html += '<div class="item active">';
		else
			html += '<div class="item">';

		var lifespan = data['_private']['data']['lifespan'];
		var temperature = data['_private']['data']['temperature'];
		var name = data['_private']['data']['name'];
		var url = data['_private']['data']['id'];

		// for wildtype it's a different page
		if (name.toLowerCase() === 'wild type') url = 'wildtype';

		html += '<div class="title">' + name;
		html += ' <a href="/details/' + url + '">(details <i class="fa fa-external-link" aria-hidden="true"></i>)</a>';
		html += '</div>';
		html += '<div class="extra-padding">';
		html += '<div>Lifespan: <strong>' + lifespan + '</strong> days</div>';
		if (temperature !== '')
			html += '<div>Temperature: <strong>' + temperature + '</strong> °C</div>';
		html += '</div>';

		html += '</div>';

	});

	html += '</div>';

	if (count > 0)
		html += '<div class="text-center"><div class="select-neighbours">Select neighbours</div></div>';

	if (count > 1) {
		html += '<div class="count-genes text-center"><small class="text-muted"><strong>' + count + '</strong> nodes selected</small></div>';
		html += '<a class="left carousel-control" href="#gene_carousel" data-slide="prev"><span class="glyphicon glyphicon-chevron-left"></span></a>';
		html += '<a class="right carousel-control" href="#gene_carousel" data-slide="next"><span class="glyphicon glyphicon-chevron-right"></span></a>';
	}

	html += '</div>';

	// info box
	box.html(html);

	// show div
	$('#cy_info').show();

	// enable tooltips
	$('[data-toggle="tooltip"]').tooltip();

	$('.select-neighbours').on('click', function () {
		cy.filter(neighbours).select();
	});
}

function populateGraph(nodes, edges, gene, type, tax_id, page_id) {
	$.ajax({
		url: '/ajax/graphData/',
		async: false,
		data: {
			'gene': gene,
			'type': type,
			'tax_id': tax_id,
			'page_id': page_id
		},
		dataType: 'json',
		success: function (data) {
			// extra points
			if (!$.isEmptyObject(data['extra_points'][0]['nodes'])) {
				$('#cy_empty').hide();
				$.each(data['extra_points'][0]['nodes'], function (i, node) {
					nodes.push({
						data: {
							id: node['node_id'],
							lifespan: node['lifespan'],
							class: 'node-point',
							name: node['name'],
							temperature: node['temperature'],
							name_with_lifespan: node['name'] + ' – ' + node['lifespan'],
							pmid: node['pmid']
						},
						position: {'x': node['x_position'], 'y': node['y_position']}
					});
				});

				$.each(data['extra_points'][0]['edges'], function (i, edge) {

					// edge class, based on lifespan (asc or desc)
					var first_node = data['extra_points'][0]['nodes'].find(x => x.node_id === edge['id1']);
					var second_node = data['extra_points'][0]['nodes'].find(x => x.node_id === edge['id2']);

					var edge_class = '';
					if (first_node && second_node) {
						if (second_node['lifespan'] > first_node['lifespan'] * 1.05) edge_class = 'asc';
						else if (second_node['lifespan'] < first_node['lifespan'] * 0.95) edge_class = 'desc';
					}

					edges.push({
						data: {
							id: edge['id1'] + '_' + edge['id2'],
							class: edge_class,
							source: edge['id1'],
							target: edge['id2']
						}
					});
				});
			} else {
				$('#cy_empty').show();
			}

			var lifespan_bar_used_points = [];

			if (!$.isEmptyObject(data['lifespan'])) {
				// lifespan bar (add space on the top & bottom of the line (edge). this is also used for gene enumeration - is the space below lowest lifespan
				var lifespan_bar_extra = 40;
				// the difference between node and lifespan bar (line)
				var lifespan_value_difference = 40;
				// bottom node
				nodes.push({
					data: {id: 'lf1', class: 'invisible'},
					// + 1 below, because the node have 2 width/height
					position: {'x': 0, 'y': data['lifespan']['min_lifespan_point'] + lifespan_bar_extra * 2 + 1}
				});
				// top (lifespan (days)) node
				nodes.push({
					data: {id: 'lf2', name: 'Lifespan (days)', class: 'lifespan_days'},
					position: {'x': 0, 'y': data['lifespan']['max_lifespan_point'] - lifespan_bar_extra * 2}
				});
				// the edge between bottom &  top
				edges.push({
					data: {id: 'lf1_lf2', source: 'lf1', target: 'lf2'}
				});

				// appendValueOnLifespanBar(nodes, edges, 0, data['lifespan']['min_lifespan'], data['lifespan']['min_position'], lifespan_value_difference, lifespan_bar_used_points, true, tax_id);
				// appendValueOnLifespanBar(nodes, edges, 0, data['lifespan']['max_lifespan'], data['lifespan']['max_position'], lifespan_value_difference, lifespan_bar_used_points, true, tax_id);
				// appendValueOnLifespanBar(nodes, edges, 0, ((data['lifespan']['max_lifespan'] + data['lifespan']['min_lifespan']) / 2), (Math.round(data['lifespan']['max_position'] + data['lifespan']['min_position']) / 2), lifespan_value_difference, lifespan_bar_used_points, true, tax_id);
				if (0 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 0, 0, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (10 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 10, 10, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (20 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 20, 20, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (30 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 30, 30, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (40 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 40, 40, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (50 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 50, 50, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (60 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 60, 60, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (70 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 70, 70, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (80 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 80, 80, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (90 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 90, 90, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);
				if (100 < data['lifespan']['max_lifespan_point_value']) appendValueOnLifespanBar(nodes, edges, 0, 100, 100, lifespan_value_difference, lifespan_bar_used_points, false, tax_id);

				// max lifespan db
				nodes.push({
					data: {class: 'invisible'},
					position: {'x': 0 - lifespan_value_difference, 'y': data['lifespan']['max_lifespan_point']}
				});
				// min lifespan db
				nodes.push({
					data: {class: 'invisible'},
					position: {'x': 0 - lifespan_value_difference, 'y': data['lifespan']['min_lifespan_point']}
				});


				// genes enumeration
				// first node
				nodes.push({
					data: {id: 'ge1', class: 'invisible'},
					position: {'x': data['lifespan']['y'] + lifespan_bar_extra, 'y': data['lifespan']['min_lifespan_point'] + lifespan_bar_extra * 2}
				});
				// last node
				nodes.push({
					data: {id: 'ge2', class: 'invisible'},
					// - 1 below, because the node have 2 width/height
					position: {'x': 0 - 1, 'y': data['lifespan']['min_lifespan_point'] + lifespan_bar_extra * 2}
				});
				// bar
				edges.push({
					data: {id: 'ge1_ge2', source: 'ge2', target: 'ge1'}
				});
			}

			// genes enumeration on the x axis
			$.each(data['positions'], function (i, gene) {
				nodes.push({
					data: {name: gene['name'], class: 'axis_value'},
					position: {'x': gene['x_position'], 'y': data['lifespan']['min_lifespan_point'] + lifespan_bar_extra}
				});
				// nodes.push({
				// 	data: {id: i + 'a', class: 'bar_value'},
				// 	position: {'x': gene['x_position'], 'y': data['lifespan']['min_position'] + lifespan_bar_extra * 1.5}
				// });
				// nodes.push({
				// 	data: {id: i + 'b', class: 'bar_value'},
				// 	position: {'x': gene['x_position'], 'y': data['lifespan']['min_position'] + lifespan_bar_extra * 2 + 1}
				// });
				// edges.push({
				// 	data: {source: i + 'a', target: i.toString() + 'b', class: 'bar_value_lines'}
				// });
			});
		}
	});
}

function cytoscapeFull(cy) {
	var isInFullScreen = (document.fullscreenElement && document.fullscreenElement !== null) ||
		(document.webkitFullscreenElement && document.webkitFullscreenElement !== null) ||
		(document.mozFullScreenElement && document.mozFullScreenElement !== null) ||
		(document.msFullscreenElement && document.msFullscreenElement !== null);

	var fullscreen_element_id = 'cy_container';
	var fullscreen_element = document.getElementById(fullscreen_element_id);
	var $fullscreen_element = $('#' + fullscreen_element_id);

	if (!isInFullScreen) {
		if (fullscreen_element.requestFullscreen) fullscreen_element.requestFullscreen();
		else if (fullscreen_element.mozRequestFullScreen) fullscreen_element.mozRequestFullScreen();
		else if (fullscreen_element.webkitRequestFullScreen) fullscreen_element.webkitRequestFullScreen();
		else if (fullscreen_element.msRequestFullscreen) fullscreen_element.msRequestFullscreen();

		// set fullscreen dimensions to graph
		resizeGraph(cy, screen.width, screen.height);
	} else {
		if (document.exitFullscreen) document.exitFullscreen();
		else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
		else if (document.mozCancelFullScreen) document.mozCancelFullScreen();
		else if (document.msExitFullscreen) document.msExitFullscreen();

		resizeGraph(cy, '', '')
	}

	// fix for esc
	// fix for firefox
	$(document).bind('mozfullscreenchange', function () {
		$fullscreen_element.trigger('mozfullscreenchange');
	});
	// list of browser fullscreen change events
	var browse_events = 'fullscreenchange webkitfullscreenchange msfullscreenchange mozfullscreenchange';
	// on fullscreen change
	$fullscreen_element.unbind(browse_events).bind(browse_events, function () {
		var state = document.fullScreen || document.webkitIsFullScreen || document.msfullscreenchange || document.mozFullScreen;
		if (!state) {
			resizeGraph(cy, '', '');
			$('#cy_fullscreen').text('Fullscreen mode').attr('data-clicks', 0);
		} else {
			$('#cy_fullscreen').text('Exit fullscreen mode').attr('data-clicks', 1);
		}
	});
}

function resizeGraph(cy, width, height) {
	var $cy_element = $('#cy');
	$cy_element.css('width', width);
	$cy_element.css('height', height);
	cy.resize();
	cy.fit();
}

function showGeneGraph(gene, type, tax_id, page_id) {
	var nodes = [];
	var edges = [];

	populateGraph(nodes, edges, gene, type, tax_id, page_id);

	var cy = cytoscape({
		container: $('#cy'),
		layout: {name: 'preset'},
		elements: {nodes: nodes, edges: edges},
		style: [
			{
				//	node
				"selector": 'node',
				"css": {
					"text-valign": "center",
					"text-halign": "left",
					"width": 15,
					"height": 15,
					"font-size": 20,
					"background-color": "rgb(187,203,218)"
				}
			},
			{
				"selector": "node:selected",
				"css": {
					"content": "data(name_with_lifespan)",
					"background-color": "rgb(255,255,0)"
				}
			},
			{
				"selector": "node.selected",
				"css": {
					"background-color": "rgb(255,165,0)"
				}
			},
			// shapes
			{
				"selector": "node[type='wildtype']",
				"css": {
					"shape": "diamond"
				}
			},
			{
				"selector": "node[type='single']",
				"css": {
					"shape": "ellipse"
				}
			},
			{
				"selector": "node[type='double']",
				"css": {
					"shape": "square"
				}
			},
			{
				"selector": "node[type='rest']",
				"css": {
					"shape": "hexagon"
				}
			},
			// invisible node
			{
				"selector": "node[class='invisible']",
				"css": {
					"color": "rgb(0,0,0)",
					"background-opacity": 0,
					"content": "data(name)",
					"font-size": "30px",
					"text-halign": "center",
					"width": 2,
					"height": 2
				}
			},
			// invisible, lifespan (days) node
			{
				"selector": "node[class='lifespan_days']",
				"css": {
					"color": "rgb(0,0,0)",
					"background-opacity": 0,
					"padding-top": "20px",
					"content": "data(name)",
					"font-size": "30px",
					"text-halign": "center",
					"width": 2,
					"height": 2
				}
			},
			// bar value (lines)
			{
				"selector": "node[class='bar_value']",
				"css": {
					"color": "rgb(0,0,0)",
					"background-opacity": 0,
					"width": 2,
					"height": 2
				}
			},
			// axis values
			{
				"selector": "node[class='axis_value']",
				"css": {
					"content": "data(name)",
					"text-halign": "center",
					"font-size": "26px",
					"background-color": "rgb(255,255,255)",
					"background-opacity": 0
				}
			},
			// edge
			{
				"selector": "edge",
				"css": {
					"target-arrow-color": "rgb(132,132,132)",
					"width": 1.0,
					"curve-style": "bezier",
					"line-color": "rgb(132,132,132)",
					"target-arrow-shape": "triangle"
				}
			},
			{
				"selector": "edge:selected",
				"css": {
					"line-color": "rgb(255,255,0)"
				}
			},
			{
				"selector": "edge[class='asc']",
				"css": {
					"line-color": "rgb(0,128,0)"
				}
			},
			{
				"selector": "edge[class='bar_value_lines']",
				"css": {
					"target-arrow-shape": "none"
				}
			},
			{
				"selector": "edge[class='desc']",
				"css": {
					"line-color": "rgb(255,0,0)"
				}
			}
		],
		ready: function () {
			window.cy = this;

			// fullscreen
			$('#cy_fullscreen').unbind('click').on('click', function () {
				cytoscapeFull(cy);
				var clicks = $(this).attr('data-clicks');
				if (clicks % 2 === 0) $(this).text('Exit fullscreen mode');
				else $(this).text('Fullscreen mode');
				$(this).attr('data-clicks', parseInt(clicks) + 1);
			});

			// reload graph
			$('#reload_graph').unbind('click').on('click', function () {
				reloadGraph(cy, 'details', gene, type, tax_id, page_id);
			});
		}
	});


	cy.panzoom({
		maxZoom: 2, // max zoom level
		minZoom: 0.25 // min zoom level
	});

	cy.userZoomingEnabled(false);

	// node selection
	cy.on('select unselect', "node[class='node-point']", function () {
		cy.nodes().removeClass('selected');

		var nodes = cy.$('node:selected');
		var neighbours = this.neighborhood().nodes();

		infoGeneBox(nodes, neighbours);

		// show "select genes with the same pubmed"
		selectPubmed(nodes);

		// expand list with the selected gene name
		var name = $(this)[0]['_private']['data']['name'];
		var $list = $('#experiments .list-header[data-name="' + name + '"]');

		$('#experiments .collapse').removeClass('in');
		if ($list.hasClass('collapsed'))
			$list.click();
	});

	cy.nodes().unselect(); // probably useless...
	selectPubmed();
	$('#cy_info').hide();

	cy.nodes().ungrabify();
}

function getParameter(name) {
	return (location.search.split(name + '=')[1] || '').split('&')[0];
}

function expTable(name) {
	var $table = $('#experiments > div[data-name="' + name + '"] #experiments_container .table');
	$.ajax({
		url: '/ajax/expTable/',
		async: false,
		data: {
			'name': name
		},
		dataType: 'json',
		success: function (data) {
			if ($.isEmptyObject(data)) {
				$table.addClass('hidden');
			} else {
				// store table html source
				var html = '';

				var th0 = '<th></th><th></th>';
				var th1 = '<th></th><th></th>';
				var th2 = '<th></th><th></th>';
				var th3 = '<th></th><th></th>';
				var th4 = '<th></th><th></th>';
				var th5 = '<th></th><th></th>';
				var th6 = '<th></th><th></th>';

				$.each(data, function (experiment_id, experiments) {

					// table lines :-)
					var td0 = '<td></td><td></td>';
					var td1 = '<td></td><td></td>';
					var td2 = '<td></td><td></td>';
					var td3 = '<td></td><td></td>';
					var td4 = '<td></td><td></td>';
					var td5 = '<td></td><td></td>';
					var td6 = '<td></td><td></td>';

					html += '<tr data-id="' + experiment_id + '">';

					$.each(experiments, function (i, experiment) {
						if (experiment[2] === 0)
							td0 = '<td>' + experiment[0] + '</td><td class="text-center">' + experiment[1] + '</td>';
						if (experiment[2] === 1)
							td1 = '<td>' + experiment[0] + '</td><td class="text-center">' + experiment[1] + '</td>';
						if (experiment[2] === 2)
							td2 = '<td>' + experiment[0] + '</td><td class="text-center">' + experiment[1] + '</td>';
						if (experiment[2] === 3)
							td3 = '<td>' + experiment[0] + '</td><td class="text-center">' + experiment[1] + '</td>';
						if (experiment[2] === 4)
							td4 = '<td>' + experiment[0] + '</td><td class="text-center">' + experiment[1] + '</td>';
						if (experiment[2] === 5)
							td5 = '<td>' + experiment[0] + '</td><td class="text-center">' + experiment[1] + '</td>';
						if (experiment[2] === 6)
							td6 = '<td>' + experiment[0] + '</td><td class="text-center">' + experiment[1] + '</td>';
					});

					// table head. if we have at least one row with content, then we have th
					if (th0 === '<th></th><th></th>' && td0 !== '<td></td><td></td>')
						th0 = '<th>Name</th><th>Lifespan (days)</th>';
					if (th1 === '<th></th><th></th>' && td1 !== '<td></td><td></td>')
						th1 = '<th>Name</th><th>Lifespan (days)</th>';
					if (th2 === '<th></th><th></th>' && td2 !== '<td></td><td></td>')
						th2 = '<th>Name</th><th>Lifespan (days)</th>';
					if (th3 === '<th></th><th></th>' && td3 !== '<td></td><td></td>')
						th3 = '<th>Name</th><th>Lifespan (days)</th>';
					if (th4 === '<th></th><th></th>' && td4 !== '<td></td><td></td>')
						th4 = '<th>Name</th><th>Lifespan (days)</th>';
					if (th5 === '<th></th><th></th>' && td5 !== '<td></td><td></td>')
						th5 = '<th>Name</th><th>Lifespan (days)</th>';
					if (th6 === '<th></th><th></th>' && td6 !== '<td></td><td></td>')
						th6 = '<th>Name</th><th>Lifespan (days)</th>';

					html += td0;
					html += td1;
					html += td2;
					html += td3;
					html += td4;
					html += td5;
					html += td6;

					html += '</tr>';
				});

				var th_html = '<tr>' + th0 + th1 + th2 + th3 + '</tr>';

				// update the table with table head and html rows
				$table.html(th_html);
				$table.append(html);
			}
		}
	});
}

function load_histograms(index) {
	var $parent = $('#histograms');
	var no_elements = $parent.find('div[data-index]').length;

	if (index < no_elements) {
		var $element = $parent.find('div[data-index=' + index + ']');
		var src = $parent.find('div[data-index=' + index + ']').data('src');
		var img = $('<img src="' + src + '" class="img-responsive" alt="histogram">').on('load', function () {
			$element.append(img);
			load_histograms(index + 1);
		});
	}
}


function appendValueOnLifespanBar(nodes, edges, x, name, y, difference, used_points, already_fixed, tax_id) {
	// mouse names
	if (tax_id === 10090) name = name * 10;

	// name is rounded
	name = Math.round(name);

	// if value wasn't used before
	if ($.inArray(y, used_points) === -1) {

		// must be the same as in view!
		var graph_y = y;

		// coefficient (different for mouse)
		if (!already_fixed) {
			if (tax_id === 10090) graph_y = ((200 - name * 15) / 10);
			else graph_y = (200 - y * 15);
		}

		nodes.push({
			data: {name: name, class: 'axis_value'},
			position: {'x': x - difference, 'y': graph_y}
		});
		nodes.push({
			data: {id: 'lb_' + y, class: 'bar_value'},
			position: {'x': x - difference / 2, 'y': graph_y}
		});
		nodes.push({
			data: {id: 'lb_' + y + '_1', class: 'bar_value'},
			position: {'x': x + 1, 'y': graph_y}
		});
		edges.push({
			data: {source: 'lb_' + y, target: 'lb_' + y + '_1', class: 'bar_value_lines'}
		});

		used_points.push(name);
	}
}


function superscript_square_brackets() {
	var elements = $('.superscript-square-brackets');
	elements.each(function () {
		var $current_element = $(this);
		var current_element_text = $current_element.text();
		var new_element_text = current_element_text;
		var matches = current_element_text.match(/\[(.+?)\]/g);
		if (matches) {
			for (var i = 0; i < matches.length; i++) {
				var match = matches[i];
				var plain_match = match.replace('[', '').replace(']', '');
				var new_element_text = new_element_text.replace(match, '<sup>' + plain_match + '</sup>');
				$current_element.html(new_element_text);
			}
		}
	});
}