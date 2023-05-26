url_input = document.querySelector('.urlbox input')
start = document.querySelector('#start')
qual = document.querySelector('#qual')
loader = document.querySelector('.loader')

container = document.querySelector('.result')
title = document.querySelector('.result h3')
stats = document.querySelector('.result p')
thumb = document.querySelector('.result img')
bar = document.querySelector('.result progress')
end = document.querySelector('.end')

const is_url = /https:\/\/..\.pornhub\.com\/view_video\.php\?viewkey=([\da-z]{13})/gm

update = (session) => {
    /* Constantly update text / bar while downloading */

    console.log('updating...')

    x = new XMLHttpRequest()
    x.open('GET', '/state?id=' + session)

    x.onreadystatechange = () => {
        if (x.readyState == 4) {

            value = x.response

            console.log('Session status:', value)

            if (value.includes('/')) {
                // Process executing, update html

                args = value.split('/')
                cur = args[0]
                out = args[1]
                per = Math.round(( Number(cur) / Number(out) ) * 100)

                stats.innerHTML = `Downloading ${per}% (${value})`
                bar.value = per

                // Continue listenning
                return setTimeout(update, 800, session)
            }

            else if (value === 'unknown-thread') {
                alert('Error: disconnected from thread')
                bar.value = 0
                bar.style.backgroundColor = 'crismon'
            }

            else if (value === 'error') {
                stats.innerHTML = `Download failed.`
                bar.value = 0
                bar.style.backgroundColor = 'crismon'
            }

            else if (value === 'done') {
                stats.innerHTML = `Downloaded!`
                bar.value = 100
            }

            else {
                console.log('Unhandled value:', value)
            }

            // Show the end pannel
            end.style.display = 'flex'
        }
    }

    x.send(null)
}

download = () => {
    /* Start the download of the url */

    url = url_input.value

    // Check if url is valid
    if (!url.match(is_url)) {
        url_input.value = ''
        return alert('Invalid URL!')
    }

    // Show the loading animation
    console.log('Downloading', url)
    loader.style.display = 'unset'

    // Send the request
    xhr = new XMLHttpRequest()
    
    key = url.split('key=')[1]
    xhr.open('GET', `/get?key=` + key)

    console.log('using key', key)

    xhr.onreadystatechange = () => {
        if (xhr.readyState == 4) {

            data = JSON.parse(xhr.response)

            // Hide the loading animation
            loader.style.display = 'none'
            console.log('Received:', data)

            // Display the result div
            thumb.src = data.thumbnail
            title.innerHTML = 'Video: ' + data.title
            stats.innerHTML = 'Download started!'
            container.style.display = 'unset'

            // Loop every 3 seconds to see evolution
            setTimeout(update, 1000, data.session)
        }
    }

    xhr.send(null)
}

open = () => {
    /* (Kindly) ask the backend to open the video */

    o = new XMLHttpRequest()
    o.open('GET', '/open')
    o.send(null)
}

// Bind URL entry
start.addEventListener('click', download)
url_input.addEventListener('keypress', ev => {
    if (ev.key === 'Enter') { download() }
})

// EOF