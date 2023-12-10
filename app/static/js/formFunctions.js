function comprobarTlf(){
    var telefonoWarning = document.getElementById('telefonoWarning');
    var tlfn = document.getElementById('telefono').value;
    if (!/^[0-9]*$/.test(tlfn)) {
      telefonoWarning.style.display = 'block';
    } else {
      telefonoWarning.style.display = 'none';
    }
  };

function checkEmails() {
  var email = document.getElementById('email').value;
  var confirmEmail = document.getElementById('confirmEmail').value;
  var emailWarning = document.getElementById('emailWarning');
  var emailSuccess = document.getElementById('emailSuccess');
  
  if (email !== confirmEmail || email === '' && confirmEmail === '') {
    emailWarning.style.display = email !== '' && confirmEmail !== '' ? 'inline' : 'none';
    emailSuccess.style.display = 'none';
  } else {
    emailWarning.style.display = 'none';
    emailSuccess.style.display = 'inline';
  }
}

function showInput(checkbox) {
    var fileInput = document.getElementById('file' + checkbox.id.charAt(checkbox.id.length - 1));
    if (checkbox.checked) {
      fileInput.style.display = 'inline';
    } else {
      fileInput.style.display = 'none';
    }
  }
  
  function showTick(fileInput) {
    if (fileInput.files.length > 0) {
      var tick = document.getElementById('tick' + fileInput.id.charAt(fileInput.id.length - 1));
      tick.style.display = 'inline';
    }
  }

  function actualizarFoto(){
    document.getElementById('fotografia').click();
    event.preventDefault(); 
  }
  function nombreDocumento(){
    if(document.querySelector('label[id="descripFot"]')!=null){
      document.getElementById('fotoId').removeChild(document.querySelector('label[id="descripFot"]'));
    }
    if (document.getElementById('fotografia').files.length!=0){
      var newLabel = document.createElement("label");
      newLabel.textContent = " "+document.getElementById('fotografia').files[0].name;
      newLabel.id = "descripFot";
      document.getElementById('fotoId').appendChild(newLabel);
    }

  }
  
  function comprobarCampos(){
    var inputs = document.getElementsByTagName('input');
    for (var i = 0; i < inputs.length; i++) {
      inputs[i].oninvalid = function(e) {
        e.target.setCustomValidity("");
        if (!e.target.validity.valid) {
          e.target.setCustomValidity("Por favor, rellene este campo.");
        }
      };
    }
    return comprobarSubidaArchivos();
  }

  function comprobarSubidaArchivos(){
    if(document.getElementById('titulo').files.length<1){
      alert('Debe adjuntar un documento del título o equivalencia');
      return false;
    }else if(document.getElementById('fotografia').files.length<1){
      alert('Debe adjuntar una fotografía');
      return false;
    }else{
      return true;
    }
  }