from django.conf.urls import url

from . import views

urlpatterns = [url(r'^$', views.index), url(r'^about/', views.about), url(r'^methods/', views.methods, name='methods'),
               # url(r'^browse/', views.browse, name='browse'),
               url(r'^download/', views.download), url(r'^search/', views.search),
               url(r'^submit-article/', views.submit_article),
               url(r'^roundworm/', views.browse_species, {'species_id': 6239}),
               url(r'^fruit-fly/', views.browse_species, {'species_id': 7227}),
               url(r'^mouse/', views.browse_species, {'species_id': 10090}),
               url(r'^details/(?P<id>[0-9]+)/$', views.details), url(r'^details/wildtype/$', views.wildtype),
               url(r'^ajax/expTable/$', views.expTable), url(r'^ajax/graphData/$', views.graphData),
               url(r'^ajax/keggInfo/$', views.keggInfo), url(r'^ajax/tissue_expression/$', views.tissue_expression),
               url(r'^ajax/type_of_interaction/$', views.type_of_interaction),
               url(r'^histogram.png$', views.histogram, name="histogram"), ]
