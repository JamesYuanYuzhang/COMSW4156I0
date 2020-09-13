
var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

$(window).load(function() {
  $messages.mCustomScrollbar();
  setTimeout(function() {
    fakeMessage();
  }, 100);
});

function updateScrollbar() {
  $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
    scrollInertia: 10,
    timeout: 0
  });
}

function setDate(){
  d = new Date()
  if (m != d.getMinutes()) {
    m = d.getMinutes();
    $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
  }
}

function insertMessage() {
  msg = $('.message-input').val();
  if ($.trim(msg) == '') {
    return false;
  }
  $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
  setDate();
  $('.message-input').val(null);
  updateScrollbar();
  setTimeout(function() {
    //fakeMessage();
    sendmessage(msg)
  }, 1000 + (Math.random() * 20) * 100);
}

$('.message-submit').click(function() {
  insertMessage();
});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
    insertMessage();
    return false;
  }
})

var Fake = [
  'Hi there, I am a clever bot, how can I help you?',
  'Nice to meet you',
  'How are you?',
  'How do you do?',
  'It was a pleasure chat with you'
]
//var apigClientFactory = require('aws-api-gateway-client').default;



var apigClient = apigClientFactory.newClient({
});
var params = {
  // This is where any modeled request parameters should be added.
  // The key is the parameter name, as it is defined in the API in API Gateway.
  param0: '',
  param1: ''
};

var body = {
  // This is where you define the body of the request,
  "SenderID":"yy2979",
  "Text":"hello"
};

var additionalParams = {
  // If there are any unmodeled query parameters or headers that must be
  //   sent with the request, add them here.
  headers: {
    // "Access-Control-Allow-Origin": "*"
    param0: '',
    param1: ''
  },
  queryParams: {
    param0: '',
    param1: ''
  }
};



function fakeMessage() {
  if ($('.message-input').val() != '') {
    return false;
  }
  $('<div class="message loading new"><figure class="avatar"><img src="./touxiang.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));

  updateScrollbar();

  setTimeout(function() {
    $('.message.loading').remove();
    $('<div class="message new"><figure class="avatar"><img src="./touxiang.png" /></figure>' + Fake[i] + '</div>').appendTo($('.mCSB_container')).addClass('new');

    setDate();
    updateScrollbar();
    i++;
  }, 1000 + (Math.random() * 20) * 100);

}

function sendmessage(msg)
{
  $('<div class="message loading new"><figure class="avatar"><img src="./touxiang.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));

  updateScrollbar();
  setTimeout(function() {
    //response=apigClient.chatbotPost(null,body);
    body={"SenderID":"yy2979","Text":msg}
    console.log(msg)
    console.log(body)
    apigClient.chatbotPost(null,body)
    .then(function(result){
      console.log(result.data)
      $('.message.loading').remove();
      $('<div class="message new"><figure class="avatar"><img src="./touxiang.png" /></figure>' + result.data["body"] + '</div>').appendTo($('.mCSB_container')).addClass('new');
      setDate();
      updateScrollbar();
      // Add success callback code here.
    }).catch( function(result){
      console.log(result)
      // Add error callback code here.
    });
  }, 1000 + (Math.random() * 20) * 100);

}
