url_input = document.querySelector('.urlbox input')
start = document.querySelector('#start')
qual = document.querySelector('#qual') // --qual-- -> filter dropdown
loader = document.querySelector('.loader')
container = document.querySelector('.result')
title = document.querySelector('.result h3')
stats = document.querySelector('.result p')
thumb = document.querySelector('.result img')
bar = document.querySelector('.result progress')
end = document.querySelector('.end')
filters = document.querySelector('.filters')
filter_quality = filters.querySelector('select')

const is_url = /https:\/\/..\.pornhub\.com\/view_video\.php\?viewkey=([\da-z]{13})/gm


update = (session) => {
    /* Constantly update text / bar while downloading */

    console.log('updating...')

    x = new XMLHttpRequest()
    x.open('GET', '/status?id=' + session)

    x.onreadystatechange = () => {
        if (x.readyState == 4) {

            res = JSON.parse(x.response)

            console.log('New response just dropped:', res)

            if (res.status === 'Downloading' ) {

                stats.innerHTML = `${res.progress}%`
                bar.value = res.progress
                document.title = `PH - DL - ${res.progress}%`

                // Continue listenning
                return setTimeout(update, 1000, session)
            }

            else if (res.status === 'done') {

                // Start the download
                link = document.createElement('a')
                link.download = 'video.mp4'
                link.href = res.filepath
                link.style.display = 'none'
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
                delete link
            }

            else {
                // In case of error, show error
                
                alert('Error: ' + res.status)
            }

            bar.value = res.progress || 0
            document.title = 'PH - DL'
            end.style.display = 'flex'

        }
    }

    x.send(null)
}

download = () => {
    /* Start the download of the url */

    // Hide the filters
    filters.classList.add('hidden')

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

    url = `/get?key=${key}&qual=${filter_quality.value || 'best'}`

    console.log('sending:', url)

    xhr.open('GET', url)
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

            // Loop every 2 seconds to see evolution
            setTimeout(update, 2000, data.session)
        }
    }

    xhr.send(null)
}

// Bind URL entry
start.addEventListener('click', download)
url_input.addEventListener('keypress', ev => {
    if (ev.key === 'Enter') { download() }
})

// EOF