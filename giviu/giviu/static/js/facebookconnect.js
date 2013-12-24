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
      $.ajax({
        type: "GET",
        url: "/api/users/exists-by-fb/"+response.id,
        cache: false,
        statusCode: {
          200: function() {
            $('#register').append('<input type="hidden" name="facebookId" value="'+response.id+'">');
            $('#facebook-name').html('<strong>Bienvenido nuevamente</strong> '+response.first_name);
          },
          404:function(){
            $('#register').append('<input type="hidden" name="name" value="'+response.first_name+'">');
            $('#register').append('<input type="hidden" name="location" value="'+response.location.name+'">');
            $('#register').append('<input type="hidden" name="lastName" value="'+response.last_name+'">');
            $('#register').append('<input type="hidden" name="email" value="'+response.email+'">');
            $('#register').append('<input type="hidden" name="gender" value="'+response.gender+'">');
            $('#register').append('<input type="hidden" name="birth" value="'+response.birthday+'">');
            $('#register').append('<input type="hidden" name="facebookId" value="'+response.id+'">');
            $('#facebook-name').html(response.first_name);
            $('#facebook-birth').html(response.birthday);
            $('#facebook-email').html(email);
          }
        }
      });
      $('#fb-show-sheet').remove();
      $('#btn-login').slideUp('fast');
      $('.confirm').slideDown('fast');
      // cargar datos de usuario visibles //
    
      if(response.email==undefined){
        email = '<input type="text" name="username" placeholder="ingresa tu correo electronico" class="span9 required email">';
      }else{
        email = response.email;
      }

      $('#facebook-avatar').attr('src','https://graph.facebook.com/'+response.id+'/picture?width=200&amp;height=200');
    }, {scope: 'email,user_friends,friends_birthday,user_birthday,user_location,friends_location,user_interests,user_photos'});
  }

  $('.confirmBtn').click(function(e){
     e.preventDefault();
     $('#register').submit(); 
  })