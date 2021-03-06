from django.urls import path
from .views import ServiceCreateView, ServiceDetailView, ServiceEditView, ServiceDeleteView, EventCreateView, \
    EventDetailView, EventEditView, EventDeleteView, ProfileView, ProfileEditView, AddFollower, RemoveFollower, \
    ApplicationDeleteView, ApplicationEditView, FollowersListView, FollowingsListView, RemoveMyFollower, TimeLine, \
    AllServicesView, AllEventsView, CreatedServicesView, CreatedEventsView, AppliedServicesView, ConfirmServiceTaken, \
    ConfirmServiceGiven, RateUser, RateUserDelete, RateUserEdit, ServiceSearch, EventSearch, Notifications, \
    EventApplicationDeleteView, AppliedEventsView, RequestCreateView, CreatedRequestsView, RequestsFromMeView, \
    RequestDetailView, RequestDeleteView, ServiceFilter, AllUsersView, UsersServicesListView, UsersEventsListView, \
    AddAdminView, RemoveAdminView, DashboardServiceDetailView, DashboardEventDetailView, DashboardUserDetailView, \
    ServiceDetailCommunicationView, EventDetailCommunicationView, ServiceCommunicationDeleteView, \
    EventCommunicationDeleteView, ServiceLike, ServiceUnlike, EventLike, EventUnlike, ServiceLikesList, EventLikesList, \
    MyLikes, AdminDashboardIndex, OnlineUsersList, ComplaintUser, ComplaintUserEdit, ComplaintUserDelete, Complaints, \
    MyComplaints, DeactivateService, DeactivateEvent, DeactivateUser, ActivateUser, DeactivateServiceApplication, \
    DeactivateEventApplication, Deactivateds, FeaturedServicesView, FeaturedEventsView, AddServiceFeatured, \
    RemoveServiceFeatured, AddEventFeatured, RemoveEventFeatured, SearchLogList, SearchLogListZero, SearchLogWordCloud, \
    ComplaintUserAdminSide, ComplaintsCreatedAbout, ComplaintsCreator, ComplaintsDoneByMe, RecommendationsView, \
    RecommendationApproveView, RecommendationDisapproveView

urlpatterns = [
    path('service/create', ServiceCreateView.as_view(), name='service-create'),
    path('service', AllServicesView.as_view(), name='allservices'),
    path('service/createdservices', CreatedServicesView.as_view(), name='createdservices'),
    path('service/appliedservices', AppliedServicesView.as_view(), name='appliedservices'),
    path('service/<int:pk>', ServiceDetailView.as_view(), name='service-detail'),
    path('service/edit/<int:pk>', ServiceEditView.as_view(), name='service-edit'),
    path('service/delete/<int:pk>', ServiceDeleteView.as_view(), name='service-delete'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('event/create', EventCreateView.as_view(), name='event-create'),
    path('event', AllEventsView.as_view(), name='allevents'),
    path('event/createdevents', CreatedEventsView.as_view(), name='createdevents'),
    path('event/<int:pk>', EventDetailView.as_view(), name='event-detail'),
    path('event/edit/<int:pk>', EventEditView.as_view(), name='event-edit'),
    path('event/delete/<int:pk>', EventDeleteView.as_view(), name='event-delete'),
    path('profile/<int:pk>/followers/add/<int:followpk>', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove/<int:followpk>', RemoveFollower.as_view(), name='remove-follower'),
    path('followers/remove/<int:follower_pk>', RemoveMyFollower.as_view(), name='remove-my-follower'),
    path('service/<int:service_pk>/application/delete/<int:pk>', ApplicationDeleteView.as_view(), name='application-delete'),
    path('service/<int:service_pk>/application/edit/<int:pk>/', ApplicationEditView.as_view(), name='application-edit'),
    path('service/<int:pk>/confirmtaken/', ConfirmServiceTaken.as_view(), name='confirm-service-taken'),
    path('service/<int:pk>/confirmgiven/', ConfirmServiceGiven.as_view(), name='confirm-service-given'),
    path('profile/<int:pk>/followers/', FollowersListView.as_view(), name='followers'),
    path('profile/<int:pk>/followings/', FollowingsListView.as_view(), name='followings'),
    path('rate/<int:servicepk>/<int:ratedpk>', RateUser.as_view(), name='rateuser'),
    path('rate/edit/<int:pk>', RateUserEdit.as_view(), name='rating-edit'),
    path('rate/delete/<int:pk>', RateUserDelete.as_view(), name='rating-delete'),
    path('timeline', TimeLine.as_view(), name='timeline'),
    path('service-search', ServiceSearch.as_view(), name='service-search'),
    path('event-search', EventSearch.as_view(), name='event-search'),
    path('notifications', Notifications.as_view(), name='notifications'),
    path('event/<int:event_pk>/application/delete/<int:pk>', EventApplicationDeleteView.as_view(), name='event-application-delete'),
    path('event/appliedevents', AppliedEventsView.as_view(), name='appliedevents'),
    path('request/create', RequestCreateView.as_view(), name='request-create'),
    path('request/createdrequests', CreatedRequestsView.as_view(), name='createdrequests'),
    path('request/requestsfromme', RequestsFromMeView.as_view(), name='requestsfromme'),
    path('request/<int:pk>', RequestDetailView.as_view(), name='request-detail'),
    path('request/delete/<int:pk>', RequestDeleteView.as_view(), name='request-delete'),
    path('service-filter', ServiceFilter.as_view(), name='service-filter'),
    path('allusers', AllUsersView.as_view(), name='allusers'),
    path('recommendations', RecommendationsView.as_view(), name='recommendations'),
    path('recommendations/approve/<int:pk>', RecommendationApproveView.as_view(), name='recommendations-approve'),
    path('recommendations/disapprove/<int:pk>', RecommendationDisapproveView.as_view(), name='recommendations-disapprove'),

    path('profile/<int:pk>/services/', UsersServicesListView.as_view(), name='usersservices'),
    path('profile/<int:pk>/events/', UsersEventsListView.as_view(), name='usersevents'),

    path('profile/<int:pk>/admins/add/', AddAdminView.as_view(), name='add-admin'),
    path('profile/<int:pk>/admins/remove/', RemoveAdminView.as_view(), name='remove-admin'),

    path('dashboard/service/<int:pk>', DashboardServiceDetailView.as_view(), name='dashboard-service-detail'),
    path('dashboard/event/<int:pk>', DashboardEventDetailView.as_view(), name='dashboard-event-detail'),
    path('dashboard/user/<int:pk>', DashboardUserDetailView.as_view(), name='dashboard-user-detail'),

    path('service/<int:pk>/communication', ServiceDetailCommunicationView.as_view(), name='service-detail-communication'),
    path('event/<int:pk>/communication', EventDetailCommunicationView.as_view(), name='event-detail-communication'),
    path('service/<int:service_pk>/communication/<int:pk>/delete', ServiceCommunicationDeleteView.as_view(), name='service-communication-delete'),
    path('event/<int:event_pk>/communication/<int:pk>/delete', EventCommunicationDeleteView.as_view(), name='event-communication-delete'),

    path('service/<int:pk>/like', ServiceLike.as_view(), name='service-like'),
    path('event/<int:pk>/like', EventLike.as_view(), name='event-like'),
    path('service/<int:pk>/unlike', ServiceUnlike.as_view(), name='service-unlike'),
    path('event/<int:pk>/unlike', EventUnlike.as_view(), name='event-unlike'),
    path('service/<int:pk>/likelist', ServiceLikesList.as_view(), name='service-liked-list'),
    path('event/<int:pk>/likelist', EventLikesList.as_view(), name='event-liked-list'),
    path('mylikes', MyLikes.as_view(), name='mylikes'),

    path('admindashboardindex', AdminDashboardIndex.as_view(), name='admindashboardindex'),
    path('onlineusers', OnlineUsersList.as_view(), name='onlineusers'),

    path('complaint/<int:pk>', ComplaintUser.as_view(), name='complaintuser'),
    path('complaint/edit/<int:pk>', ComplaintUserEdit.as_view(), name='complaint-edit'),
    path('complaint/delete/<int:pk>', ComplaintUserDelete.as_view(), name='complaint-delete'),
    path('complaints', Complaints.as_view(), name='complaints'),
    path('mycomplaints', MyComplaints.as_view(), name='mycomplaints'),
    path('complaintsolve/<int:pk>', ComplaintUserAdminSide.as_view(), name='complaintsolve'),
    path('complaintscreatedabout/<int:pk>', ComplaintsCreatedAbout.as_view(), name='complaintscreatedabout'),
    path('complaintscreator/<int:pk>', ComplaintsCreator.as_view(), name='complaintscreator'),
    path('complaintsdonebyme/<int:pk>', ComplaintsDoneByMe.as_view(), name='complaintsdonebyme'),

    path('deactivateds', Deactivateds.as_view(), name='deactivateds'),

    path('profile/deactivate/<int:pk>', DeactivateUser.as_view(), name='deactivate-user'),
    path('profile/activate/<int:pk>', ActivateUser.as_view(), name='activate-user'),
    path('service/<int:pk>/deactivate', DeactivateService.as_view(), name='deactivate-service'),
    path('event/<int:pk>/deactivate', DeactivateEvent.as_view(), name='deactivate-event'),
    path('service/application/<int:pk>/deactivate', DeactivateServiceApplication.as_view(), name='deactivate-service-application'),
    path('event/application/<int:pk>/deactivate', DeactivateEventApplication.as_view(), name='deactivate-event-application'),

    path('featuredservices', FeaturedServicesView.as_view(), name='featuredservices'),
    path('featuredevents', FeaturedEventsView.as_view(), name='featuredevents'),
    path('add-service-featured/<int:pk>', AddServiceFeatured.as_view(), name='add-service-featured'),
    path('remove-service-featured/<int:pk>', RemoveServiceFeatured.as_view(), name='remove-service-featured'),
    path('add-event-featured/<int:pk>', AddEventFeatured.as_view(), name='add-event-featured'),
    path('remove-event-featured/<int:pk>', RemoveEventFeatured.as_view(), name='remove-event-featured'),

    path('searchloglist', SearchLogList.as_view(), name='searchloglist'),
    path('searchloglistzero', SearchLogListZero.as_view(), name='searchloglistzero'),
    path('searchlogwordcloud', SearchLogWordCloud.as_view(), name='searchlogwordcloud'),
]