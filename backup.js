//popup.html backup

<!DOCTYPE html>
<html>
    <head>
        <title>OurCal</title>
        <script type="text/javascript" src="jquery-3.6.0.min.js"></script>
        <script src="popup.js"></script>
    </head>
    <body>
        <h1>OurCal</h1>
        <h2>Friends List:
            <p id="friends">(smartcalendar@umich.edu - Blue)</p>
        </h2>
        <input type="text" id="code" value="Authorization Code">
        <input type="text" id="email" value="Email">
        <input type="text" id="color" value="Blue">
        <input type="submit" id="input_email" value="Submit">
        <input type="submit" id="popper" value="Pop Last">
    </body>
</html>

//popup.js backup

$(function(){
    var newFriend = [];
    var newEmail = [];
    var newColor = [];
    
    chrome.storage.sync.get('friends', function(listFriend){
        let temp = '';
        let tempArray = [];
        newFriend = listFriend.friends;
        newEmail = [];
        newColor = [];
        console.log(newFriend);
        if(newFriend.length < 2) {
            temp = '(smartcalendar@umich.edu - Blue)';
            tempArray.push(temp);
        }
        else {
            for(var i = 0; i < newFriend[0].length; i++) {
                newEmail.push(newFriend[0][i]);
                newColor.push(newFriend[1][i]);
                temp = `(${newFriend[0][i]} - ${newFriend[1][i]})`;
                tempArray.push(temp);
            }
        }
        
        $("#friends").text(tempArray);
        
        
    })
    
    $('#input_email').click(function(){
        chrome.storage.sync.get('friends', function(addFriend){
            let temp = '';
            let tempArray = [];
            newEmail.push($('#email').val());
            newColor.push($('#color').val());
            newFriend = [newEmail, newColor];
            console.log(newFriend);
            chrome.storage.sync.set({'friends': newFriend});
            for(var i = 0; i < newFriend[0].length; i++) {
                temp = `(${newFriend[0][i]} - ${newFriend[1][i]})`;
                tempArray.push(temp);
            }
            $("#friends").text(tempArray);
            
        });
    });

    $('#popper').click(function(){
        chrome.storage.sync.get('friends', function(deleteFriend){
            //newFriend = [];
            //newColor = [];
            //newEmail = [];
            let temp = '';
            let tempArray = [];
            newFriend = deleteFriend.friends;
            newColor.pop();
            newEmail.pop();
            newFriend[0].pop();
            newFriend[1].pop();
            //console.log(newColor);
            for(var i = 0; i < newFriend[0].length; i++) {
                temp = `(${newFriend[0][i]} - ${newFriend[1][i]})`;
                tempArray.push(temp);
            }
            $("#friends").text(tempArray);
            chrome.storage.sync.set({'friends': newFriend});
        });
    })
});
