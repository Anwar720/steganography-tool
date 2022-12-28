const img_btn = document.querySelector('.img_btn');
const url_btn = document.querySelector('.url_btn');
const glider = document.querySelector('.glider');
const img_input = document.querySelector('.img-input');
const url_input = document.querySelector('.url-input');
const img_upload = document.querySelector('#img-input')
const input_hide_image = document.querySelector('#hide-img-input');
const reset_img_btn = document.querySelectorAll('.reset-upload-btn')
  
url_btn.addEventListener('click',()=>{
  glider.parentElement.classList.add('activate')
  img_input.style.display = "none";
  url_input.style.display = "grid";
})

img_btn.addEventListener('click',()=>{
  glider.parentElement.classList.remove('activate');
  img_input.style.display = "block";
  url_input.style.display = "none";
})
img_upload.addEventListener('change',()=>{
  document.querySelector('.selected-img p').innerText = img_upload.files[0].name;
})
input_hide_image.addEventListener('change',()=>{
  document.querySelector('.hide p').innerText = input_hide_image.files[0].name;
})

reset_img_btn.forEach(btn=>{
     btn.addEventListener('click',()=>{
       btn.parentElement.querySelector('p').innerText = ''
       btn.parentElement.closest('form').reset()
  })
})

