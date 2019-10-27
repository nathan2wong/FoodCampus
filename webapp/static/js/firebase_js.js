  var firebaseConfig = {
    apiKey: "AIzaSyCCAsUqC4wIAoGOX01B-12WdsUmn6le_J0",
    authDomain: "foodcampus.firebaseapp.com",
    databaseURL: "https://foodcampus.firebaseio.com",
    projectId: "foodcampus",
    storageBucket: "foodcampus.appspot.com",
    messagingSenderId: "252754605166",
    appId: "1:252754605166:web:62a0a073c803d156c7a27f",
    measurementId: "G-G3YHDS277G"
  };
  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);
  firebase.analytics();
  var uiConfig = {
    'signInSuccessUrl': '/user',
    'signInOptions': [
      // Leave the lines as is for the providers you want to offer your users.
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID
    ],
    // Terms of service url
    'tosUrl': '/user',
  };

  var ui = new firebaseui.auth.AuthUI(firebase.auth());
  ui.start('#firebaseui-auth-container', uiConfig);
  firebase.auth().onAuthStateChanged(function(user) {
  if (user) {
    $('#logged-out').hide();
    var name = user.displayName;
    console.log(name);
    /* If the provider gives a display name, use the name for the
    personal welcome message. Otherwise, use the user's email. */
    var welcomeName = name ? name : user.email;
    firebase.auth().currentUser.getIdToken(/* forceRefresh */ true).then(function(idToken) {
      userIdToken = idToken;

      /* Now that the user is authenicated, fetch the notes. */
        $.ajax(window.location + '/notes', {
          /* Set header for the XMLHttpRequest to get data from the web server
          associated with userIdToken */
          headers: {
            'Authorization': userIdToken
          }
        })

      $('#user').text(welcomeName);
      $('#logged-in').show();



    });

  } else {
    $('#logged-in').hide();
    $('#logged-out').show();

  }
  })
