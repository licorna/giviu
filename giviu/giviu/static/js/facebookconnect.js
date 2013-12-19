  window.fbAsyncInit = function() {
  FB.init({
    appId      : '259478790867380',
    status     : true, // check login status
    cookie     : true, // enable cookies to allow the server to access the session
    xfbml      : true  // parse XFBML
  });

  FB.Event.subscribe('auth.authResponseChange', function(response) {
    if (response.status === 'connected') {
      newuser();
      $('#changeAccount').show();
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

  function newuser() {
    FB.api('/me', function(response) {
      console.log(response);
      $('[name="name"]').val(response.first_name);
      $('[name="lastName"]').val(response.last_name);
      $('[name="username"]').val(response.email);
      $('[name="gender"]').val(response.gender);
      $('[name="birth"]').val(response.birthday);
      $('[name="facebookId"]').val(response.id);
      $('#selecttype').addClass('up');
      $('#registercontent').addClass('big');
      $('#fb-show-sheet').remove();
      $('.msg').show();
      $('.loader').hide();
    }, {scope: 'email,user_friends,friends_birthday,user_birthday,user_location,friends_location,user_interests,user_photos'});
  }


  function login(){
    FB.login();
    $('.msg').hide();
    $('.loader').show();
  }

  function changeAccount(){
    $('#selecttype').removeClass('up');
    $('#registercontent').removeClass('big');
    FB.logout();
  }

