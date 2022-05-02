function AjaxPost(event){
  const inputTextObj = document.getElementById("lemma");
  if (!inputTextObj.checkValidity()) {
    document.getElementById("result").innerHTML = inputTextObj.validationMessage;
    return;
  }
  event.preventDefault();
  let xhr = new XMLHttpRequest();
  xhr.open('POST', "/cgi-bin/lectus.cgi", true);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      document.getElementById("result").innerHTML = xhr.responseText;
    }
  }
  xhr.send(getquerystring());
}

function getquerystring() {
    var form = document.forms['form_lectus'];
    var word = form.lemma.value;
    // var path = form.dir.value;
    // var qstr = 'dir=' + path + '&' + 'lemma=' + word;
    var qstr = 'lemma=' + word;
    // var regex = form.regex.checked;
    // qstr += '&' + 'regex=' + regex;
    dicts_selected = form.dicts.selectedOptions;
    var Ndicts = dicts_selected.length;
    qstr +=  '&' + 'Ndicts=' + Ndicts;
    var arr = [].map.call(dicts_selected, function(opt){return opt.value;});
    qstr +=  '&' + 'dicts=' + arr;  // arr is a csv
    // console.log( qstr);
    // alert(qstr);
    return qstr;
}
