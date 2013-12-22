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
    }, {scope: 'email,user_friends,friends_birthday,user_birthday,user_location,friends_location,user_interests,user_photos'});
  };

  (function(d){
   var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
   if (d.getElementById(id)) {return;}
   js = d.createElement('script'); js.id = id; js.async = true;
   js.src = "//connect.facebook.net/en_US/all.js";
   ref.parentNode.insertBefore(js, ref);
  }(document));

  function newuser() {
    FB.api('/me/', function(response) {
      $('[name="name"]').val(response.first_name);
      $('[name="location"]').val(response.location.name);
      $('[name="lastName"]').val(response.last_name);
      $('[name="username"]').val(response.email);
      $('[name="gender"]').val(response.gender);
      $('[name="birth"]').val(response.birthday);
      $('[name="facebookId"]').val(response.id);
      $('#fb-show-sheet').remove();
      $('#btn-login').slideUp('fast');
      $('.confirm').slideDown('fast');
      // cargar datos de usuario visibles //
    
      if(response.email==undefined){
        email = '<input type="text" name="username" placeholder="ingresa tu correo electronico" class="span9 required email">';
      }else{
        email = response.email;
      }
      $('#facebook-name').html(response.first_name);
      $('#facebook-birth').html(response.birthday);
      $('#facebook-email').html(email);
      $('#facebook-avatar').attr('src','https://graph.facebook.com/'+response.id+'/picture?width=200&amp;height=200');
    }, {scope: 'email,user_friends,friends_birthday,user_birthday,user_location,friends_location,user_interests,user_photos'});
  }

  function birthday(id) {
    FB.api('/'+id+'?fields=birthday', function(response) {
      console.log(response);
    }, {access_token:accesToken,scope: 'email,user_friends,friends_birthday,user_birthday,user_location,friends_location,user_interests,user_photos'});
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
