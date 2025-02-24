function addHobby(event) {
    event.preventDefault();
    const hobbyInput = document.getElementById('hobby');
    const hobbyName = hobbyInput.value;

    fetch('/add_hobby', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ hobby: hobbyName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const hobbyList = document.getElementById('hobby-list');
            const newHobby = document.createElement('li');
            newHobby.textContent = hobbyName + ' ';
            const removeLink = document.createElement('a');
            removeLink.href = `/remove_hobby/${data.hobby_id}`;
            removeLink.textContent = 'x';
            newHobby.appendChild(removeLink);
            hobbyList.appendChild(newHobby);
            hobbyInput.value = '';
        } else {
            alert(data.message || 'Failed to add hobby');
        }
    });
}

function loadPopularHobbies(page) {
    fetch(`/popular_hobbies?page=${page}`)
    .then(response => response.json())
    .then(data => {
        const popularHobbyList = document.getElementById('popular-hobby-list');
        popularHobbyList.innerHTML = '';

        // set start variable of ol
        popularHobbyList.start = data.start;

        data.hobbies.forEach(hobby => {
            const hobbyItem = document.createElement('li');
            const hobbyLink = document.createElement('a');
            hobbyLink.href = `/hobby/${hobby.id}`;
            hobbyLink.textContent = `${hobby.name} (${hobby.user_count} users)`;
            hobbyItem.appendChild(hobbyLink);
            popularHobbyList.appendChild(hobbyItem);
        });


        // set page number, update buttons
        document.getElementById('page-number').textContent = page;

        if (page === 1) {
            document.getElementById('prev-page').disabled = true;
        } else {
            document.getElementById('prev-page').disabled = false;
        } 
        
        if (page == data.total_pages) {
            document.getElementById('next-page').disabled = true;
        } else {
            document.getElementById('next-page').disabled = false;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    let currentPage = 1;
    loadPopularHobbies(currentPage);

    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadPopularHobbies(currentPage);
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        currentPage++;
        loadPopularHobbies(currentPage);
    });
});
