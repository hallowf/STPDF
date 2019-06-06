---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
title: Home
permalink: /
nav_order: 1
---
# STPDF - ScanToPDF

ScanToPDF is an open-source free app that will allow you to easily make PDF's of image scans,
it supports a wide variety of feature like deskew image *(removes rotation), spliting into multiple
PDF's, custom themes and more ....

## Deskewing images

Altough ScanToPDF has the ability to deskew images it can't do it withouth [Tesseract](https://github.com/tesseract-ocr/tesseract),
and tesseract is not shipped with the app, if you are on linux you can just install it with your package manager
on windows you can find installers [here](https://github.com/UB-Mannheim/tesseract/wiki)

Tesseract will also need to be in the environment PATH variable, to check it is available just open up a command line and type tesseract,
if it displays info and it's arguments then it's working


<button class="btn js-toggle-dark-mode">Preview dark color scheme</button>

<script>
  const toggleDarkMode = document.querySelector('.js-toggle-dark-mode')
  const cssFile = document.querySelector('[rel="stylesheet"]')
  const originalCssRef = cssFile.getAttribute('href')
  const darkModeCssRef = originalCssRef.replace('just-the-docs.css', 'dark-mode-preview.css')

  addEvent(toggleDarkMode, 'click', function(){
    if (cssFile.getAttribute('href') === originalCssRef) {
      cssFile.setAttribute('href', darkModeCssRef)
    } else {
      cssFile.setAttribute('href', originalCssRef)
    }
  })
</script>
