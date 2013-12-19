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
  	$('.loadingUsers').fadeIn();
    FB.api('/me', function(response) {
      friends(response.id);

      $.post( "/user/modifyFbId", { fbUser : response.id})
        .done(function( data ) {
      });
    }, {scope: 'email,user_friends,friends_birthday,user_birthday,user_location,friends_location,user_interests,user_photos'});
  }


  function friends(idloginUser) {
    FB.api('/'+idloginUser+'/friends', function(response) {
    totalFriends = response.data.length;
     count = 0;
     console.log(response.data);
      $.each(response.data, function( key, value ) {
        $.each(value, function( k, v ) {
          if(k=='id'){
		      FB.api('/'+v+'?fields=birthday,id,first_name,gender', function(response) {
		    		count ++;
              percent = (100/parseInt(totalFriends))*count;
              $('.status').css('width',percent+'%');
              birthday = response.birthday;
              gender = response.gender;

              if(birthday== undefined){
               birthday = '0/0';
              }              

              if(gender== undefined){
               gender = 'no';
              }        

              var birthday = birthday.split('/');
			        $.post( "/user/addFbFriends", { me : idloginUser,name : response.first_name, friend:response.id ,month: birthday[0], day: birthday[1],birthday: birthday[1]+'/'+birthday[0], gender: gender  })
			          .done(function( data ) {
			        });
    			    if(totalFriends==count){
    			      	$('.loadingUsers').fadeOut();
    			      	location.href="/user/calendar?friends=show";
    			    }

		      }, {scope: 'email,user_birthday'});
          }
        });
      });

    }, {scope: 'email,user_friends,friends_birthday,user_birthday,user_location,friends_location,user_interests,user_photos'});
  }  

