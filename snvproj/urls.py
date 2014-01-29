#NEW APP
from django.conf.urls import patterns, include, url
import snv.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

        url(r'^$', snv.views.home.as_view(), name='home',),
        url(r'^listuniprot$', snv.views.UniprotList.as_view(), name='uniprot-list',),
        url(r'^(?P<pk>\d+)/$', snv.views.UniprotView.as_view(), name='uniprot-view',),


        url(r'^login/$', 'django.contrib.auth.views.login'),
        url(r'^logout/$', 'django.contrib.auth.views.logout'),
        url(r'^search-form/$', snv.views.search_form),
        url(r'^search/$', snv.views.search, name='search-results',),
    # url(r'^snvproj/', include('snvproj.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

)
