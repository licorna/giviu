  window.fbAsyncInit = function() {
  FB.init({
    appId      : '259478790867380',
    status     : true, // check login status
    cookie     : true, // enable cookies to allow the server to access the session
    xfbml      : true  // parse XFBML
  });

  FB.Event.subscribe('auth.authResponseChange', function(response) {
    if (response.status === 'connected') {
      showUserInfo();
    } else if (response.status === 'not_authorized') {
      FB.login();
    } else {
      FB.login();
    }
    });
  };

  (function(d){
   var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
   if (d.getElementById(id)) {return;}
   js = d.createElement('script'); js.id = id; js.async = true;
   js.src = "//connect.facebook.net/en_US/all.js";
   ref.parentNode.insertBefore(js, ref);
  }(document));

function showUserInfo(){
    FB.api('/me/', function(response) {
    	$('.not-logged').remove();
    	$('.logged').removeClass();
    	$('.avatarHeader').html('<img src="https://graph.facebook.com/'+response.id+'/picture?width=40&amp;height=40"/>');
    	$('#session-name').html(response.first_name);
    }, {scope: 'email,user_friends,friends_birthday,user_birthday,user_location,friends_location,user_interests,user_photos'});
}