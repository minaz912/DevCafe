from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from userapp import views

urlpatterns = patterns('',
    url(r'^$', views.UserList.as_view(), name='user-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),
    url(r'^profile/$', views.GetUserProfile.as_view(), name='user-profile'),
    url(r'^uploadpicture/$', views.UpdateProfilePicture.as_view(), name='user-uploadPicture'),
)


urlpatterns = format_suffix_patterns(urlpatterns)


# urlpatterns += patterns('',
#     url(r'^/rest-auth/facebook/$', views.FacebookLogin.as_view(), name='fb_login')
# )
