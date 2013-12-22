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
    FB.api('/me?fields=birthday,email,first_name,last_name,gender', function(response) {
      console.log(response.birthday);
      $('[name="name"]').val(response.first_name);
      $('[name="lastName"]').val(response.last_name);
      $('[name="username"]').val(response.email);
      $('[name="gender"]').val(response.gender);
      $('[name="birth"]').val(response.birthday);
      $('[name="facebookId"]').val(response.id);
      $('#fb-show-sheet').remove();
      $('#btn-login').slideUp('fast');
      $('.confirm').slideDown('fast');
      // cargar datos de usuario visibles //
      $('#facebook-name').html(response.first_name+' '+response.last_name);
      $('#facebook-birth').html(response.user_birthday);
      $('#facebook-email').html(response.email);
      $('#facebook-avatar').attr('src','https://graph.facebook.com/'+response.id+'/picture?width=200&amp;height=200');

    }, {scope:'email,user_birthday'});
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

  $('.confirmBtn').click(function(e){
     e.preventDefault();
     $('#register').submit(); 
  })
