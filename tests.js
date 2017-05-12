var request = require('request-promise-native');  

var post_data = {
  external_id: 1111,
  cart_id: 'bbda3d8e-ba6c-4b47-a3df-a73a02fb5f5b'
};

for (i=0; i < 5; i++) {

  post_data.external_id = post_data.external_id + i;

  request.post(
    "http://apicpython.calebhayashida.com/tracker",
    //"http://localhost:8888/tracker",
    {json: post_data},
    function (err, resp, body){
      console.log(body)
    }
  );

}
