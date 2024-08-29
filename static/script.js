function buttonClick() {
    var x = document.getElementById("topdown");

    if (x.style.display !== "none") {
        x.style.display = "none";
    } else {
        x.style.display = "block";
    }
}

function startLoading() {
    const loadingContainer = document.getElementById('loading-container');
    loadingContainer.style.display = 'block';

    const loadingBar = document.getElementById('loading-bar');
    const loadingText = document.getElementById('loading-text');

    let progress = 0;
    const interval = 1000; // 1 second interval
    const totalTime = 10000; // 17 seconds

    function updateLoadingBar() {
        progress += (interval / totalTime) * 100;
        loadingBar.style.width = `${progress}%`;
        loadingText.innerText = `Loading... ${Math.round(progress)}%`;

        if (progress >= 100) {
            clearInterval(loadingInterval);
            loadingText.innerText = 'Loading completing... hang on a second!';
        }
    }

    const loadingInterval = setInterval(updateLoadingBar, interval);
}

function reveal(counter) {
    var m = document.getElementById("markscheme-" + counter);

    if (m.style.display === "none") {
        m.style.display = "block";
    } else {
        m.style.display = "none";
    }
}

function reveal2(counter) {
    var m1 = document.getElementById("worked-" + counter);

    if (m1.style.display === "none") {
        m1.style.display = "block";
    } else {
        m1.style.display = "none";
    }
}

function reveal3(counter) {
    var m2 = document.getElementById("guidance-" + counter);

    if (m2.style.display === "none") {
        m2.style.display = "block";
    } else {
        m2.style.display = "none";
    }
}

function search() {
    var m2 = document.getElementById("all");

    if (m2.style.display === "none") {
        m2.style.display = "block";
    } else {
        m2.style.display = "none";
    }
}

