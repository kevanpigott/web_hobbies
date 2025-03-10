let current_user

function get_current_user() {
    // check if the global variable is already set
    if (current_user) {
        return current_user;
    }
    return fetch("/get_current_user")
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            current_user = data.user;
            return current_user;
        } else {
            console.error(data.message);
            return null;
        }
    })
    .catch(error => {
        console.error("Error fetching current user:", error);
        return null;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM loaded");
    // get the current user using the /get_current_user
    get_current_user().then(user => {
        if (user) {
            // add the username to the h2-welcome element
            const h2Welcome = document.getElementById('h2-welcome');
            h2Welcome.textContent = `Welcome, ${user.username}!`;

            // Refresh user hobbies and most common user
            refreshUserHobbies();
            refreshMostCommonUser();
            refreshMostCommonUserNeverMet();
            fetchOneOnOnes();
        }
    });
});


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

function fetchOneOnOnes() {
    fetch(`/get_user_one_on_ones/${current_user.id}`)
        .then(response => response.json())
        .then(data => {
            const oneOnOneList = document.getElementById('one-on-one-list');
            oneOnOneList.innerHTML = '';
            data.one_on_ones.forEach(meeting => {
                const utcDate = new Date(meeting.date + 'Z'); // Ensure the date string is treated as UTC
                const localDate = utcDate.toLocaleString(); // convert UTC back to Local
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.innerHTML = `
                    ${localDate} with <a href="/user/${meeting.user.username}">${meeting.user.username}</a>
                    <button class="btn btn-danger btn-sm" onclick="cancelOneOnOne(${meeting.id})">Cancel</button>
                `;
                oneOnOneList.appendChild(li);
            });
        });
}


function cancelOneOnOne(meetingId) {
    fetch(`/cancel_one_on_one/${meetingId}`, {
        method: 'DELETE'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              fetchOneOnOnes();
              refreshMostCommonUserNeverMet();
          } else {
              alert('Failed to cancel meeting: ' + data.message);
          }
      });
}

function addHobbyToList(hobbyName, hobbyId) {
    const hobbyList = document.getElementById('hobby-list');
    const newHobby = document.createElement('li');
    newHobby.classList.add('li-hobby'); // Add the class li-hobby
    newHobby.textContent = hobbyName + ' ';
    const removeLink = document.createElement('a');
    removeLink.href = '#';
    removeLink.textContent = 'x';
    removeLink.addEventListener('click', (event) => {
        event.preventDefault();
        removeHobby(hobbyId);
    });
    newHobby.appendChild(removeLink);
    hobbyList.appendChild(newHobby);
}

function refreshUserHobbies() {
    fetch(`/get_user_hobbies/${current_user.id}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const hobbyList = document.getElementById('hobby-list');
                hobbyList.innerHTML = '';
                data.hobbies.forEach(hobby => {
                    addHobbyToList(hobby.name, hobby.id);
                });
            } else {
                console.error(data.message);
            }
        })
        .catch(error => console.error("Error fetching user hobbies:", error));
}

function removeHobby(hobbyId) {
    fetch(`/remove_hobby/${hobbyId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            refreshUserHobbies();
            refreshMostCommonUser();
            refreshMostCommonUserNeverMet();
        } else {
            alert(data.message || 'Failed to remove hobby');
        }
    })
    .catch(error => console.error("Error removing hobby:", error));
}

function refreshMostCommonUser() {
    fetch("/most_common_user")
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const mostCommonUser = data.user;
                const mostCommonUserElement = document.getElementById("most-common-user");

                // Remove existing child if it exists
                while (mostCommonUserElement.firstChild) {
                    mostCommonUserElement.removeChild(mostCommonUserElement.firstChild);
                }

                // Create and append the new link
                const userLink = document.createElement('a');
                userLink.href = `/user/${mostCommonUser.username}`;
                userLink.textContent = mostCommonUser.username;
                mostCommonUserElement.textContent = 'Most common user: ';
                mostCommonUserElement.appendChild(userLink);
            } else {
                console.error(data.message);
            }
        })
        .catch(error => console.error("Error fetching most common user:", error));
}

function refreshMostCommonUserNeverMet() {
    fetch("/most_common_user_never_met")
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const mostCommonUserNeverMet = data.user;
            const mostCommonUserNeverMetElement = document.getElementById("most-common-user-never-met");

            // Remove existing child if it exists
            while (mostCommonUserNeverMetElement.firstChild) {
                mostCommonUserNeverMetElement.removeChild(mostCommonUserNeverMetElement.firstChild);
            }

            // Create and append the new link
            const userLink = document.createElement('a');
            userLink.href = `/user/${mostCommonUserNeverMet.username}`;
            userLink.textContent = mostCommonUserNeverMet.username;
            mostCommonUserNeverMetElement.textContent = 'Most common user never met: ';
            mostCommonUserNeverMetElement.appendChild(userLink);
        } else {
            console.error(data.message);
        }
    })
    .catch(error => console.error("Error fetching most common user never met:", error));
}

function addHobby(event) {
    event.preventDefault();
    const hobbyInput = document.getElementById('hobby');
    const hobbyName = hobbyInput.value;
    const encodedHobbyName = encodeURIComponent(hobbyName);

    fetch(`/add_hobby/${encodedHobbyName}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addHobbyToList(hobbyName, data.hobby_id);
            hobbyInput.value = ''; // Clear the input field after adding the hobby
            refreshMostCommonUser();
            refreshMostCommonUserNeverMet();
        } else {
            alert(data.message || 'Failed to add hobby');
        }
    })
    .catch(error => console.error("Error adding hobby:", error));
}

function loadPopularHobbies(page) {
    fetch(`/popular_hobbies/${page}`)
    .then(response => response.json())
    .then(data => {
        const popularHobbyList = document.getElementById('popular-hobby-list');
        popularHobbyList.innerHTML = '';

        // set start variable of ol
        popularHobbyList.start = data.start;

        data.hobbies.forEach(hobby => {
            const hobbyItem = document.createElement('li');
            const hobbyLink = document.createElement('a');
            hobbyItem.classList.add('list-group-item'); // Add the class li-hobby
            hobbyLink.classList.add('class="text-decoration-none'); // Add the class li-hobby
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
    })
    .catch(error => console.error("Error fetching popular hobbies:", error));
}
