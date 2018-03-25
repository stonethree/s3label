function logError(error) {
    console.log('Looks like there was a problem: \n', error);
}

function validateResponse(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}

function readResponseAsBlob(response) {
    return response.blob();
}

function showImage(responseAsBlob) {
    let canvas_fg = document.getElementById("canvas-fg");
    let canvas_bg = document.getElementById("canvas-bg");

    let ctx = canvas_fg.getContext("2d");
    let ctx2 = canvas_bg.getContext("2d");    

    let img = new Image();
    let imgUrl = URL.createObjectURL(responseAsBlob);

    img.onload = function () {
        setCanvasSize(canvas_fg, img.width, img.height);
        setCanvasSize(canvas_bg, img.width, img.height);
        ctx2.drawImage(img, padX, padY);
    }
    img.src = imgUrl;
}

function fetchAndDisplayImage(pathToResource) {
    fetch(pathToResource)
        .then(validateResponse)
        .then(readResponseAsBlob)
        .then(showImage)
        .catch(logError);
}

function setCanvasSize(c, width, height) {
    c.width = width + padX * 2;
    c.height = height + padX * 2;
    c.style.width = width + padX * 2 + 'px';
    c.style.height = height + padX * 2 + 'px';
    console.log('c '+ c.width + ', ' + c.height, padX, padY);
}